"""vLLM monitoring tool package"""

__version__ = "0.1.2"

# Import modules with error handling for build process
try:
    from .monitor import VLLM_TOP, VLLMMetricsMonitor
    from .main import main, parse_vllm_metrics_once
    __all__ = ["VLLM_TOP", "VLLMMetricsMonitor", "main", "parse_vllm_metrics_once"]
except ImportError:
    # During build process, modules might not be available
    __all__ = []