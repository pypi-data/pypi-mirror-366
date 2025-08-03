from vllm_top.monitor import VLLM_TOP

def main():
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        monitor = VLLM_TOP()
        monitor.run_monitor(interval)
    else:
        # One-time snapshot
        monitor = VLLM_TOP()
        monitor.fetch_metrics()
        monitor.display_metrics(monitor.fetch_metrics())

if __name__ == "__main__":
    main()