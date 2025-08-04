#!/usr/bin/env python3
"""
Command-line interface for the Nedo Vision Training Service Library.
"""

import argparse
import sys
import signal
import traceback
from .training_service import TrainingService
from .doctor import run_doctor


def signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    print("\n🛑 Received interrupt signal. Shutting down gracefully...")
    sys.exit(0)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Nedo Vision Training Service Library CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check system dependencies and requirements
  nedo-training doctor

  # Start training service with token (defaults to localhost:50051)
  nedo-training run --token YOUR_TOKEN

  # Start with custom server host/port
  nedo-training run --token YOUR_TOKEN --server-host custom.server.com --server-port 60000
        """
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Doctor command
    doctor_parser = subparsers.add_parser(
        'doctor', 
        help='Check system dependencies and requirements',
        description='Run diagnostic checks for CUDA, NVIDIA drivers, and other dependencies'
    )
    
    # Run command (existing functionality)
    run_parser = subparsers.add_parser(
        'run',
        help='Start the training service',
        description='Start the Nedo Vision Training Service'
    )
    
    run_parser.add_argument(
        "--token", 
        required=True,
        help="Authentication token provided by the manager (required)"
    )
    
    run_parser.add_argument(
        "--server-host",
        default="localhost",
        help="Server hostname for communication (default: localhost)"
    )
    
    run_parser.add_argument(
        "--server-port",
        type=int,
        default=50051,
        help="Server port for communication (default: 50051)"
    )
    
    run_parser.add_argument(
        "--system-usage-interval",
        type=int,
        default=30,
        help="System usage reporting interval in seconds (default: 30)"
    )
    
    run_parser.add_argument(
        "--latency-check-interval",
        type=int,
        default=10,
        help="Latency monitoring interval in seconds (default: 10)"
    )
    
    # Add legacy arguments for backward compatibility (when no subcommand is used)
    parser.add_argument(
        "--token", 
        help="(Legacy) Authentication token provided by the manager"
    )
    
    parser.add_argument(
        "--server-host",
        default="localhost",
        help="(Legacy) Server hostname for communication (default: localhost)"
    )
    
    parser.add_argument(
        "--server-port",
        type=int,
        default=50051,
        help="(Legacy) Server port for communication (default: 50051)"
    )
    
    parser.add_argument(
        "--system-usage-interval",
        type=int,
        default=30,
        help="(Legacy) System usage reporting interval in seconds (default: 30)"
    )
    
    parser.add_argument(
        "--latency-check-interval",
        type=int,
        default=10,
        help="(Legacy) Latency monitoring interval in seconds (default: 10)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="nedo-vision-training 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Handle subcommands
    if args.command == 'doctor':
        sys.exit(run_doctor())
    elif args.command == 'run':
        run_training_service(args)
    elif args.token:  # Legacy mode - if token is provided without subcommand
        print("⚠️  Warning: Using legacy command format. Consider using 'nedo-training run --token ...' instead.")
        run_training_service(args)
    else:
        # If no subcommand provided and no token, show help
        parser.print_help()
        sys.exit(1)


def run_training_service(args):
    """Run the training service with the provided arguments."""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    from .logger.Logger import Logger
    logger = Logger()
    
    try:
        # Create and start the training service
        service = TrainingService(
            token=args.token,
            server_host=args.server_host,
            server_port=args.server_port,
            system_usage_interval=args.system_usage_interval,
            latency_check_interval=args.latency_check_interval
        )
        
        logger.info("🚀 Starting Nedo Vision Training Service...")
        logger.info(f"🌐 Server: {args.server_host}:{args.server_port}")
        logger.info(f"⏱️ System Usage Interval: {args.system_usage_interval}s")
        
        # Start the service
        service.run()
        
        # Keep the service running
        try:
            while getattr(service, 'running', False):
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutdown requested...")
        finally:
            service.stop()
            logger.info("✅ Service stopped successfully")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 