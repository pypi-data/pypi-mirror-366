#!/usr/bin/env python3
"""
Doctor module for checking external dependencies and system requirements.
"""

import subprocess
import sys
import platform
import importlib.util
import os
from typing import Dict, List, Tuple, Optional


class DependencyChecker:
    """Class to check various system dependencies and requirements."""

    def __init__(self):
        self.checks = []
        self.warnings = []
        self.errors = []

    def check_python_version(self) -> Tuple[bool, str]:
        """Check if Python version is compatible."""
        version = sys.version_info
        required_major, required_minor = 3, 8
        
        if version.major >= required_major and version.minor >= required_minor:
            return True, f"✅ Python {version.major}.{version.minor}.{version.micro}"
        else:
            return False, f"❌ Python {version.major}.{version.minor}.{version.micro} (requires >= {required_major}.{required_minor})"

    def check_gpu_availability(self) -> Tuple[bool, str]:
        """Check if GPU is available through PyTorch or other means."""
        gpu_info = []
        
        # Check PyTorch GPU availability
        try:
            import torch
            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                for i in range(device_count):
                    try:
                        device_name = torch.cuda.get_device_name(i)
                        memory_gb = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                        gpu_info.append(f"GPU {i}: {device_name} ({memory_gb:.1f}GB)")
                    except:
                        gpu_info.append(f"GPU {i}: Available")
                
                if gpu_info:
                    return True, f"✅ GPU(s) detected via PyTorch: {'; '.join(gpu_info)}"
            else:
                # Check if PyTorch is compiled with CUDA but no GPU available
                if hasattr(torch.version, 'cuda') and torch.version.cuda:
                    return False, "⚠️  PyTorch has CUDA support but no GPU detected"
        except ImportError:
            pass
        
        # Check for common GPU-related files on Linux (including Jetson)
        gpu_files_to_check = [
            "/proc/driver/nvidia/version",  # NVIDIA driver info
            "/sys/class/drm/card0/device/vendor",  # Generic GPU vendor
            "/dev/dri/card0",  # Direct Rendering Infrastructure
        ]
        
        for gpu_file in gpu_files_to_check:
            try:
                if platform.system() == "Linux" and os.path.exists(gpu_file):
                    if "nvidia" in gpu_file:
                        with open(gpu_file, 'r') as f:
                            content = f.read().strip()
                            if content:
                                return True, f"✅ NVIDIA GPU detected (driver info available)"
                    else:
                        return True, f"✅ GPU hardware detected"
            except (OSError, IOError):
                continue
        
        return False, "❌ No GPU detected"

    def check_cuda_availability(self) -> Tuple[bool, str]:
        """Check if CUDA is available through various methods."""
        # First check through PyTorch (most reliable)
        try:
            import torch
            if torch.cuda.is_available():
                cuda_version = torch.version.cuda if hasattr(torch.version, 'cuda') else "Unknown"
                return True, f"✅ CUDA available via PyTorch (version: {cuda_version})"
            elif hasattr(torch.version, 'cuda') and torch.version.cuda:
                return False, f"⚠️  PyTorch compiled with CUDA {torch.version.cuda} but GPU not accessible"
        except ImportError:
            pass
        
        # Check CUDA installation on system (cross-platform)
        cuda_paths_to_check = []
        if platform.system() == "Windows":
            cuda_paths_to_check = [
                "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA",
                "C:\\Program Files (x86)\\NVIDIA GPU Computing Toolkit\\CUDA"
            ]
        else:  # Linux/Unix-like (including Jetson)
            cuda_paths_to_check = [
                "/usr/local/cuda",
                "/opt/cuda",
                "/usr/cuda"
            ]
        
        for cuda_path in cuda_paths_to_check:
            if os.path.exists(cuda_path):
                # Try to find version info
                version_file = os.path.join(cuda_path, "version.txt")
                if os.path.exists(version_file):
                    try:
                        with open(version_file, 'r') as f:
                            version_info = f.read().strip()
                            return True, f"✅ CUDA Toolkit found: {version_info}"
                    except (OSError, IOError):
                        pass
                return True, f"✅ CUDA Toolkit found at {cuda_path}"
        
        # Check for CUDA libraries in system paths
        try:
            if platform.system() != "Windows":
                # Check for libcudart (CUDA runtime library)
                result = subprocess.run(
                    ["ldconfig", "-p"], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                if result.returncode == 0 and "libcudart" in result.stdout:
                    return True, "✅ CUDA runtime libraries found in system"
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass
        
        return False, "❌ CUDA not detected"

    def check_pytorch_cuda(self) -> Tuple[bool, str]:
        """Check if PyTorch with CUDA support is available."""
        try:
            import torch
            if torch.cuda.is_available():
                cuda_version = torch.version.cuda
                device_count = torch.cuda.device_count()
                device_name = torch.cuda.get_device_name(0) if device_count > 0 else "Unknown"
                return True, f"✅ PyTorch CUDA {cuda_version} ({device_count} GPU(s), {device_name})"
            else:
                return False, "⚠️  PyTorch installed but CUDA not available"
        except ImportError:
            return False, "❌ PyTorch not installed"
        except Exception as e:
            return False, f"❌ PyTorch CUDA check failed: {str(e)}"

    def check_required_packages(self) -> Tuple[bool, str]:
        """Check if required Python packages are installed."""
        # Package name -> import name mapping
        package_mappings = {
            'torch': 'torch',
            'torchvision': 'torchvision',
            'opencv-python': 'cv2',
            'numpy': 'numpy',
            'pillow': 'PIL',
            'grpcio': 'grpc',
            'protobuf': 'google.protobuf',
            'pika': 'pika',
            'boto3': 'boto3',
            'psutil': 'psutil',
            'requests': 'requests',
            'tqdm': 'tqdm'
        }
        
        missing_packages = []
        installed_packages = []
        
        for package_name, import_name in package_mappings.items():
            try:
                # Try to actually import the module
                __import__(import_name)
                installed_packages.append(package_name)
            except ImportError:
                # Double-check using importlib for packages that might have different import names
                try:
                    spec = importlib.util.find_spec(import_name)
                    if spec is not None:
                        installed_packages.append(package_name)
                    else:
                        missing_packages.append(package_name)
                except (ImportError, ModuleNotFoundError):
                    missing_packages.append(package_name)
        
        if not missing_packages:
            return True, f"✅ All required packages installed ({len(installed_packages)} packages)"
        else:
            return False, f"❌ Missing packages: {', '.join(missing_packages)}"

    def check_system_info(self) -> Tuple[bool, str]:
        """Check system information."""
        system = platform.system()
        architecture = platform.machine()
        processor = platform.processor() or "Unknown"
        
        # Add specific information for common training platforms
        additional_info = []
        
        # Check if running on Jetson device
        if system == "Linux":
            try:
                # Check for Jetson-specific files
                jetson_files = [
                    "/sys/firmware/devicetree/base/model",
                    "/proc/device-tree/model"
                ]
                for jetson_file in jetson_files:
                    if os.path.exists(jetson_file):
                        with open(jetson_file, 'r') as f:
                            model = f.read().strip()
                            if "jetson" in model.lower() or "nvidia" in model.lower():
                                additional_info.append(f"Jetson device: {model}")
                                break
            except (OSError, IOError):
                pass
        
        # Get CPU count and memory info
        try:
            import psutil
            cpu_count = psutil.cpu_count()
            memory_gb = psutil.virtual_memory().total / (1024**3)
            additional_info.append(f"{cpu_count} CPUs, {memory_gb:.1f}GB RAM")
        except ImportError:
            try:
                import multiprocessing
                cpu_count = multiprocessing.cpu_count()
                additional_info.append(f"{cpu_count} CPUs")
            except:
                pass
        
        info_str = f"✅ System: {system} {architecture}"
        if processor != "Unknown":
            info_str += f" ({processor})"
        if additional_info:
            info_str += f" - {', '.join(additional_info)}"
        
        return True, info_str

    def check_disk_space(self) -> Tuple[bool, str]:
        """Check available disk space."""
        try:
            import psutil
            current_dir = os.getcwd()
            disk_usage = psutil.disk_usage(current_dir)
            
            total_gb = disk_usage.total / (1024**3)
            free_gb = disk_usage.free / (1024**3)
            used_gb = disk_usage.used / (1024**3)
            free_percent = (free_gb / total_gb) * 100
            
            if free_gb < 5:  # Less than 5GB free
                return False, f"⚠️  Disk Space: {free_gb:.1f}GB free of {total_gb:.1f}GB ({free_percent:.1f}% free) - Low disk space!"
            elif free_gb < 20:  # Less than 20GB free
                return True, f"⚠️  Disk Space: {free_gb:.1f}GB free of {total_gb:.1f}GB ({free_percent:.1f}% free) - Consider freeing up space"
            else:
                return True, f"✅ Disk Space: {free_gb:.1f}GB free of {total_gb:.1f}GB ({free_percent:.1f}% free)"
                
        except ImportError:
            # Fallback using shutil
            try:
                import shutil
                total, used, free = shutil.disk_usage(os.getcwd())
                free_gb = free / (1024**3)
                total_gb = total / (1024**3)
                
                if free_gb < 5:
                    return False, f"⚠️  Disk Space: {free_gb:.1f}GB free of {total_gb:.1f}GB - Low disk space!"
                else:
                    return True, f"✅ Disk Space: {free_gb:.1f}GB free of {total_gb:.1f}GB"
            except:
                return True, "⚠️  Disk Space: Unable to check disk space"
        except Exception as e:
            return True, f"⚠️  Disk Space: Unable to check ({str(e)})"

    def check_gpu_memory(self) -> Tuple[bool, str]:
        """Check GPU memory using Python libraries."""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_info = []
                for i in range(torch.cuda.device_count()):
                    try:
                        properties = torch.cuda.get_device_properties(i)
                        total_memory = properties.total_memory
                        # Get current memory usage
                        torch.cuda.set_device(i)
                        allocated = torch.cuda.memory_allocated(i)
                        cached = torch.cuda.memory_reserved(i)
                        free = total_memory - cached
                        
                        total_gb = total_memory / (1024**3)
                        allocated_gb = allocated / (1024**3)
                        free_gb = free / (1024**3)
                        
                        gpu_info.append(f"GPU {i}: {total_gb:.1f}GB total, {allocated_gb:.1f}GB used, {free_gb:.1f}GB free")
                    except Exception as e:
                        # Fallback to basic info if detailed memory info fails
                        properties = torch.cuda.get_device_properties(i)
                        total_gb = properties.total_memory / (1024**3)
                        gpu_info.append(f"GPU {i}: {total_gb:.1f}GB total")
                
                if gpu_info:
                    return True, f"✅ GPU Memory: {'; '.join(gpu_info)}"
                else:
                    return False, "❌ No GPU memory information available"
            else:
                return False, "❌ No CUDA-capable GPU available for memory check"
        except ImportError:
            return False, "❌ PyTorch not available for GPU memory check"
        except Exception as e:
            return False, f"❌ GPU memory check failed: {str(e)}"

    def run_all_checks(self) -> Dict[str, Tuple[bool, str]]:
        """Run all dependency checks."""
        checks = {
            "Python Version": self.check_python_version(),
            "System Info": self.check_system_info(),
            "Disk Space": self.check_disk_space(),
            "GPU Hardware": self.check_gpu_availability(),
            "CUDA Support": self.check_cuda_availability(),
            "Required Packages": self.check_required_packages(),
            "PyTorch CUDA": self.check_pytorch_cuda(),
            "GPU Memory": self.check_gpu_memory(),
        }
        return checks

    def print_report(self, checks: Dict[str, Tuple[bool, str]]) -> bool:
        """Print a formatted report of all checks."""
        print("\n" + "="*60)
        print("🔍 NEDO VISION TRAINING SERVICE - DEPENDENCY DOCTOR")
        print("="*60)
        
        all_passed = True
        critical_failed = False
        
        # Define critical checks
        critical_checks = ["Python Version", "Required Packages"]
        
        for check_name, (passed, message) in checks.items():
            print(f"{message}")
            
            if not passed:
                all_passed = False
                if check_name in critical_checks:
                    critical_failed = True
                    self.errors.append(f"{check_name}: {message}")
                else:
                    self.warnings.append(f"{check_name}: {message}")
        
        print("\n" + "="*60)
        
        if critical_failed:
            print("❌ CRITICAL ISSUES DETECTED - Service may not work properly")
            print("\n🔧 Recommended Actions:")
            for error in self.errors:
                print(f"   • Fix: {error}")
        elif not all_passed:
            print("⚠️  WARNINGS DETECTED - Service should work but performance may be affected")
            print("\n💡 Recommendations:")
            for warning in self.warnings:
                print(f"   • Consider: {warning}")
        else:
            print("✅ ALL CHECKS PASSED - System is ready for training!")
        
        print("="*60)
        
        return all_passed and not critical_failed


def run_doctor():
    """Run the dependency doctor and return exit code."""
    checker = DependencyChecker()
    checks = checker.run_all_checks()
    success = checker.print_report(checks)
    
    return 0 if success else 1
