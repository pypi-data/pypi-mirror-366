import sys
import os
import argparse

# Try relative import first, fall back to absolute import
try:
    from .monitor import VLLM_TOP
except ImportError:
    # If relative import fails, try absolute import
    try:
        from vllm_top.monitor import VLLM_TOP
    except ImportError:
        # Last resort: add current directory to path and import
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        from monitor import VLLM_TOP

def parse_vllm_metrics_once(port=8000, host="0.0.0.0"):
    """Function for one-time metrics parsing"""
    monitor = VLLM_TOP(port=port, host=host)
    grouped_metrics = monitor.fetch_metrics()
    
    if not grouped_metrics:
        print("Failed to fetch metrics")
        return
    
    monitor.update_history(grouped_metrics)
    monitor.display_metrics(grouped_metrics)

def main():
    """Main entry point for the vllm-top CLI"""
    parser = argparse.ArgumentParser(description='vLLM metrics monitoring tool')
    parser.add_argument('--port', '-p', type=int, default=8000, 
                       help='Port number where vLLM server is running (default: 8000)')
    parser.add_argument('--host', type=str, default="0.0.0.0",
                       help='Host address of vLLM server (default: 0.0.0.0)')
    parser.add_argument('--snapshot', action='store_true',
                       help='Take a single snapshot instead of continuous monitoring')
    parser.add_argument('--interval', '-i', type=float, default=0.1,
                       help='Display refresh interval in seconds (default: 0.1)')
    
    args = parser.parse_args()
    
    if args.snapshot:
        # One-time snapshot
        parse_vllm_metrics_once(port=args.port, host=args.host)
    else:
        # Continuous monitoring mode
        monitor = VLLM_TOP(port=args.port, host=args.host)
        monitor.run_monitor(args.interval)

if __name__ == "__main__":
    main()