import json
import os
from typing import List, Dict, Any
from nedo_vision_training.modules.dataset.DatasetHandler import DatasetHandler
import logging
from PIL import Image

logger = logging.getLogger(__name__)

class COCODatasetHandler(DatasetHandler):
    def __init__(self, dataset_id: str, output_dir: str, 
                 train_ratio: float = 0.7, 
                 val_ratio: float = 0.15, 
                 test_ratio: float = 0.15,
                 seed: int = 42,
                 config: dict = None):
        super().__init__(dataset_id, output_dir, train_ratio, val_ratio, test_ratio, seed, config)
        self.val_dir = os.path.join(output_dir, "valid")
        
    def _get_image_dimensions(self, image_path: str) -> tuple:
        """
        Get the width and height of an image.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            tuple: (width, height) of the image
        """
        try:
            with Image.open(image_path) as img:
                return img.size
        except Exception as e:
            logger.error(f"Failed to get image dimensions for {image_path}: {e}")
            return (0, 0)
        
    def _process_split(self, items: List[Any], split_name: str) -> Dict[str, Any]:
        """
        Process a single split of the dataset
        
        Args:
            items (List[Any]): List of dataset items for this split
            split_name (str): Name of the split (train/val/test)
            
        Returns:
            Dict[str, Any]: COCO format data for this split
        """
        split_dir = getattr(self, f"{split_name}_dir")
        coco_data = {
            "images": [],
            "annotations": [],
            "categories": set()
        }
        
        annotation_id = 1
        image_id = 1
        
        for item in items:
            # Download image from S3
            local_image_path = os.path.join(split_dir, os.path.basename(item.file_path))
            self.s3_client.download_file(item.file_path, local_image_path)
            
            # Get image dimensions
            width, height = self._get_image_dimensions(local_image_path)
            
            # Add image entry
            image_entry = {
                "id": image_id,
                "file_name": os.path.basename(item.file_path),
                "width": width,
                "height": height
            }
            coco_data["images"].append(image_entry)
            
            # Process annotations
            # Convert protobuf RepeatedCompositeContainer to regular list if needed
            annotations = item.annotations
            if hasattr(annotations, '__iter__') and not isinstance(annotations, (list, tuple)):
                # Check if it's a protobuf RepeatedCompositeContainer
                if hasattr(annotations, '_values'):
                    annotations = list(annotations._values)
                else:
                    annotations = list(annotations)
                
            for ann in annotations:
                coco_ann = self._convert_annotations([ann], width, height)[0]
                coco_ann.update({
                    "id": annotation_id,
                    "image_id": image_id
                })
                coco_data["annotations"].append(coco_ann)
                coco_data["categories"].add(ann.label)
                annotation_id += 1
                
            image_id += 1
            
        return coco_data
        
    def process_dataset(self) -> Dict[str, Any]:
        """
        Process the dataset and convert it to COCO format with train/val/test splits
        
        Returns:
            Dict[str, Any]: Processing results including success status and metadata
        """
        try:
            # Ensure output directories exist
            self._ensure_output_dir()
            
            # Fetch dataset from gRPC service
            dataset_result = self.dataset_service.get_dataset(self.dataset_id)
            
            if not dataset_result["success"]:
                logger.error(f"Failed to fetch dataset: {dataset_result['message']}")
                raise Exception(dataset_result["message"])
                
            # Split dataset
            train_items, val_items, test_items = self._split_dataset(dataset_result["data"])
            
            # Process each split
            splits = {
                "train": train_items,
                "val": val_items,
                "test": test_items
            }
            
            all_categories = set()
            split_data = {}
            
            for split_name, items in splits.items():
                split_data[split_name] = self._process_split(items, split_name)
                all_categories.update(split_data[split_name]["categories"])
                
            categories = [
                {"id": 0, "name": "objects", "supercategory": "none"}
            ]
            
            for idx, cat in enumerate(sorted(all_categories), start=1):
                categories.append({
                    "id": idx,
                    "name": cat,
                    "supercategory": "objects"
                })
            
            # Update category IDs in all splits
            category_map = {cat["name"]: cat["id"] for cat in categories}
            for split_name in splits:
                for ann in split_data[split_name]["annotations"]:
                    ann["category_id"] = category_map[ann["category_name"]]
                    del ann["category_name"]
                split_data[split_name]["categories"] = categories

                # Add info field if missing
                if "info" not in split_data[split_name]:
                    split_data[split_name]["info"] = {
                        "description": f"{split_name} split of dataset {self.dataset_id}",
                        "version": "1.0",
                        "year": 2024
                    }

                # Save split annotations in the split directory
                split_dir = getattr(self, f"{split_name}_dir")
                split_file = os.path.join(split_dir, "_annotations.coco.json")
                with open(split_file, 'w') as f:
                    json.dump(split_data[split_name], f, indent=2)
                    
            logger.info(f"Dataset successfully processed and converted to COCO format")
            
            # Return success status
            return {
                "success": True,
                "message": "Dataset successfully processed and converted to COCO format",
                "output_dir": self.output_dir,
                "categories": categories
            }
            
        except Exception as e:
            logger.error(f"Failed to process dataset: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to process dataset: {e}"
            }
            
    def _convert_annotations(self, annotations: List[Any], img_width: int, img_height: int) -> List[Dict[str, Any]]:
        """
        Convert annotations to COCO format
        
        Args:
            annotations (List[Any]): Original annotations
            img_width (int): Image width in pixels
            img_height (int): Image height in pixels
        
        Returns:
            List[Dict[str, Any]]: Annotations in COCO format
        """
        coco_annotations = []
        
        for ann in annotations:
            # Convert bbox from (x1,y1,x2,y2) in percentage to COCO format (x,y,width,height) in pixels
            x = getattr(ann, 'b_box_x1', 0.0) * img_width
            y = getattr(ann, 'b_box_y1', 0.0) * img_height
            x2 = getattr(ann, 'b_box_x2', 0.0) * img_width
            y2 = getattr(ann, 'b_box_y2', 0.0) * img_height
            label = getattr(ann, 'label', '')
            
            width = x2 - x
            height = y2 - y
            
            coco_ann = {
                "bbox": [x, y, width, height],
                "category_name": label,  # Will be converted to category_id later
                "area": width * height,
                "iscrowd": 0
            }
            coco_annotations.append(coco_ann)
            
        return coco_annotations 