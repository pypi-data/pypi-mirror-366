#!/usr/bin/env python3
"""Command Line Interface for GPU Benchmark Tool.

This module provides the command-line interface for running GPU benchmarks, diagnostics, and monitoring.
"""

import argparse
import json
import sys
import platform
from datetime import datetime

from .benchmark import run_full_benchmark
from .backends import list_available_backends
from .diagnostics import print_system_info, print_enhanced_monitoring_status, print_comprehensive_diagnostics
from .benchmark import run_multi_gpu_benchmark

from . import __version__

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False


def print_banner():
    """Prints the tool banner with version information."""
    print("=" * 60)
    print(f"GPU Benchmark Tool v{__version__}")
    print("=" * 60)


def print_gpu_info(info):
    """Pretty prints GPU information.

    Args:
        info (dict): Dictionary containing GPU information to display.
    """
    print("\nGPU Information:")
    print("-" * 30)
    for key, value in info.items():
        print(f"{key:.<25} {value}")


def print_health_score(health):
    """Pretty prints the health score with color coding.

    Args:
        health (dict): Health assessment dictionary with score, status, recommendation, and details.
    """
    score = health["score"]
    status = health["status"]
    
    # Use our color utility functions
    from .utils import print_success, print_warning, print_error, print_info
    
    print("\nHealth Assessment:")
    print("-" * 30)
    
    # Color-code the score based on status
    if status in ["healthy", "good"]:
        print_success(f"Score: {score}/100", bold=True)
        print_success(f"Status: {status.upper()}", bold=True)
    elif status in ["degraded", "warning"]:
        print_warning(f"Score: {score}/100", bold=True)
        print_warning(f"Status: {status.upper()}", bold=True)
    elif status == "critical":
        print_error(f"Score: {score}/100", bold=True)
        print_error(f"Status: {status.upper()}", bold=True)
    else:
        print_info(f"Score: {score}/100", bold=True)
        print_info(f"Status: {status.upper()}", bold=True)
    
    print(f"Recommendation: {health['recommendation']}")
    
    if "details" in health and "breakdown" in health["details"]:
        print("\nScore Breakdown:")
        for component, points in health["details"]["breakdown"].items():
            print(f"  {component:.<25} {points} points")
    
    if "details" in health and "specific_recommendations" in health["details"]:
        recs = health["details"]["specific_recommendations"]
        if recs:
            print("\nSpecific Recommendations:")
            for rec in recs:
                print(f"  • {rec}")


def print_test_results(results):
    """Pretty prints stress test results.

    Args:
        results (dict): Dictionary containing results from various stress tests.
    """
    if "matrix_multiply" in results:
        print("\nMatrix Multiplication Test:")
        mm = results["matrix_multiply"]
        print(f"  Performance: {mm['tflops']:.2f} TFLOPS")
        print(f"  Iterations: {mm['iterations']}")
    
    if "memory_bandwidth" in results:
        print("\nMemory Bandwidth Test:")
        mb = results["memory_bandwidth"]
        print(f"  Bandwidth: {mb['bandwidth_gbps']:.2f} GB/s")
    
    if "mixed_precision" in results:
        print("\nMixed Precision Support:")
        mp = results["mixed_precision"]
        
        # Show FP32 baseline first
        if mp.get("fp32", {}).get("supported"):
            fp32_tflops = mp.get("fp32", {}).get("tflops", 0)
            print(f"  FP32: Baseline ({fp32_tflops:.2f} TFLOPS)")
        else:
            print("  FP32: Not available")
        
        if mp.get("fp16", {}).get("supported"):
            speedup = mp.get("fp16_speedup", 0)
            tflops = mp.get("fp16", {}).get("tflops", 0)
            print(f"  FP16: Supported (Speedup: {speedup:.2f}x, {tflops:.2f} TFLOPS)")
        else:
            print("  FP16: Not supported")
        
        if mp.get("bf16", {}).get("supported"):
            speedup = mp.get("bf16_speedup", 0)
            tflops = mp.get("bf16", {}).get("tflops", 0)
            print(f"  BF16: Supported (Speedup: {speedup:.2f}x, {tflops:.2f} TFLOPS)")
        else:
            print("  BF16: Not supported")
            
        if mp.get("int8", {}).get("supported"):
            speedup = mp.get("int8_speedup", 0)
            tflops = mp.get("int8", {}).get("tflops", 0)
            print(f"  INT8: Supported (Speedup: {speedup:.2f}x, {tflops:.2f} TFLOPS)")
        else:
            print("  INT8: Not supported")


def run_mock_benchmark(args):
    """Runs the benchmark in mock mode (simulated GPU).

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    print("\nRunning in mock mode (simulated GPU)...")
    
    from .backends.mock import MockBackend
    from .backends import get_gpu_backend
    from .monitor import enhanced_stress_test
    from .scoring import score_gpu_health
    
    # Use mock backend
    backend = MockBackend()
    monitor = backend.create_monitor(0)
    
    # Get mock GPU info
    gpu_info = backend.get_device_info(0)
    
    # Run enhanced stress test with mock monitor
    print("Running simulated stress tests...")
    print("(This will take about {} seconds)".format(args.duration))
    
    try:
        import torch
        # Check if we can use CPU at least
        device = torch.device("cpu")
        metrics = enhanced_stress_test(monitor, args.duration, 0)
        
        # Score the results
        result = score_gpu_health(
            baseline_temp=metrics.get("baseline_temp", 45),
            max_temp=metrics.get("max_temp", 75),
            power_draw=metrics.get("max_power", 150),
            utilization=metrics.get("avg_utilization", 95),
            throttled=len(metrics.get("throttle_events", [])) > 0,
            errors=len(metrics.get("errors", [])) > 0,
            throttle_events=metrics.get("throttle_events", []),
            temperature_stability=metrics.get("temperature_stability"),
            enhanced_metrics=metrics.get("stress_test_results")
        )
        
        if len(result) == 4:
            score, status, recommendation, details = result
        else:
            score, status, recommendation = result
            details = {}
            
        # Build report
        report = {
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "version": __version__,
                "duration": args.duration,
                "enhanced_mode": not args.basic,
                "mock_mode": True
            },
            "gpu_info": gpu_info,
            "metrics": metrics,
            "health_score": {
                "score": score,
                "status": status,
                "recommendation": recommendation,
                "details": details
            }
        }
        
        if not args.basic and "stress_test_results" in metrics:
            report["performance_tests"] = metrics["stress_test_results"]
            
    except ImportError:
        # Torch not available, create simple mock results
        print("Note: PyTorch not installed, using simplified mock results")
        report = {
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "version": __version__,
                "duration": args.duration,
                "mock_mode": True
            },
            "gpu_info": gpu_info,
            "health_score": {
                "score": 85,
                "status": "healthy",
                "recommendation": "Mock GPU performing well in simulation mode"
            },
            "metrics": {
                "max_temp": 72,
                "max_power": 150,
                "baseline_temp": 45,
                "avg_utilization": 95
            }
        }
    
    # Print results
    print_gpu_info(report["gpu_info"])
    print_health_score(report["health_score"])
    
    if not args.basic and "performance_tests" in report:
        print_test_results(report["performance_tests"])
    
    # Export if requested
    if args.export:
        with open(args.export, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nResults exported to {args.export}")
    
    return 0


def cmd_benchmark(args):
    """Runs the benchmark command.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    
    # Handle mock mode separately
    if args.mock:
        return run_mock_benchmark(args)
    
    # Real GPU benchmark
    if not PYNVML_AVAILABLE:
        print("Error: pynvml is required for GPU benchmarking")
        print("Install with: pip install nvidia-ml-py torch")
        print("Or use --mock flag for simulation mode")
        return 1
    
    # Check for enhanced monitoring requirements
    if args.enhanced:
        try:
            import torch
            if not torch.cuda.is_available():
                print("Warning: Enhanced monitoring requires CUDA support")
                print("Install PyTorch with CUDA: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
                print("Continuing with basic monitoring...")
                args.enhanced = False
        except ImportError:
            print("Warning: PyTorch not available for enhanced monitoring")
            print("Install with: pip install torch")
            print("Continuing with basic monitoring...")
            args.enhanced = False
    
    try:
        pynvml.nvmlInit()
    except pynvml.NVMLError as e:
        print_error(f"Error initializing NVML: {e}")
        print_error("Make sure NVIDIA drivers are installed and nvidia-smi works")
        print_info("Or use --mock flag for simulation mode")
        return 1
    
    from .benchmark import run_full_benchmark, run_multi_gpu_benchmark, export_results
    from .backends import list_available_backends
    from .diagnostics import print_system_info
    from .utils import print_success, print_warning, print_error, print_info
    
    # Single GPU benchmark
    if args.gpu_id is not None:
        device_count = pynvml.nvmlDeviceGetCount()
        if args.gpu_id >= device_count:
            print_error(f"Error: GPU {args.gpu_id} not found. Found {device_count} GPU(s)")
            return 1
        
        print(f"\nBenchmarking GPU {args.gpu_id}...")
        handle = pynvml.nvmlDeviceGetHandleByIndex(args.gpu_id)
        
        # Show temperature thresholds if verbose
        if args.verbose:
            from .diagnostics import print_temperature_thresholds
            print_temperature_thresholds(handle)
        
        # Run benchmark
        enhanced_mode = args.enhanced or (not args.basic)
        result = run_full_benchmark(
            handle, 
            duration=args.duration,
            enhanced=enhanced_mode,
            device_id=args.gpu_id
        )
        
        # Print results
        print_gpu_info(result["gpu_info"])
        print_health_score(result["health_score"])
        
        if not args.basic and "performance_tests" in result:
            print_test_results(result["performance_tests"])
        
        # Export if requested
        if args.export:
            filename = export_results(result, args.export)
            print(f"\nResults exported to: {filename}")
    
    # Multi-GPU benchmark
    else:
        print("\nBenchmarking all GPUs...")
        enhanced_mode = args.enhanced or (not args.basic)
        results = run_multi_gpu_benchmark(
            duration=args.duration,
            enhanced=enhanced_mode
        )
        
        if "error" in results:
            print_error(f"Error: {results['error']}")
            return 1
            
        print(f"\nFound {results['device_count']} GPU(s)")
        
        for gpu_id, result in results["results"].items():
            print(f"\n{'='*60}")
            print(f"GPU {gpu_id}")
            print('='*60)
            
            if "error" in result:
                print(f"Error: {result['error']}")
                continue
            
            print_gpu_info(result["gpu_info"])
            print_health_score(result["health_score"])
            
            if not args.basic and "performance_tests" in result:
                print_test_results(result["performance_tests"])
        
        # Print summary
        summary = results["summary"]
        print(f"\n{'='*60}")
        print("SUMMARY")
        print('='*60)
        print(f"Total GPUs: {summary['total_gpus']}")
        print(f"Healthy GPUs: {summary['healthy_gpus']} ({summary['health_percentage']:.1f}%)")
        
        if summary["warnings"]:
            print("\nWarnings:")
            for warning in summary["warnings"]:
                print(f"  • {warning}")
        
        # Export if requested
        if args.export:
            filename = export_results(results, args.export)
            print(f"\nResults exported to: {filename}")
    
    return 0


def cmd_list(args):
    """Lists available GPUs and backends."""
    from .backends import list_available_backends
    backends = list_available_backends()
    if not backends:
        print("No supported GPU backends found!")
        print("\nOptions:")
        print("  1. Install NVIDIA support: pip install gpu-benchmark-tool[nvidia]")
        print("  2. Use mock mode: gpu-benchmark benchmark --mock")
        return 1
    for backend in backends:
        print(f"\n{backend['type'].upper()} Backend:")
        print(f"  Devices: {backend['device_count']}")
    if PYNVML_AVAILABLE:
        try:
            pynvml.nvmlInit()
            count = pynvml.nvmlDeviceGetCount()
            print("\nNVIDIA GPUs:")
            for i in range(count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode('utf-8')
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                print(f"  [{i}] {name} ({mem_info.total / 1e9:.1f} GB)")
        except pynvml.NVMLError:
            pass
    return 0


def cmd_monitor(args):
    """Real-time monitoring (basic version).

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    if args.mock:
        print("Mock monitoring not implemented yet")
        return 1
        
    if not PYNVML_AVAILABLE:
        print("Error: pynvml is required for monitoring")
        return 1
    
    import time
    
    try:
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(args.gpu_id or 0)
        
        print(f"Monitoring GPU {args.gpu_id or 0} (Press Ctrl+C to stop)...")
        print("-" * 60)
        
        while True:
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            print(f"\rTemp: {temp}°C | Power: {power:.1f}W | "
                  f"GPU: {util.gpu}% | Mem: {util.memory}% | "
                  f"VRAM: {mem_info.used/1e9:.1f}/{mem_info.total/1e9:.1f} GB", 
                  end='', flush=True)
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
    except pynvml.NVMLError as e:
        print(f"\nError: {e}")
        return 1
    
    return 0


def main():
    """Main CLI entry point.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        description="GPU Benchmark Tool - Comprehensive GPU health monitoring and optimization"
    )
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Benchmark command
    bench_parser = subparsers.add_parser('benchmark', help='Run GPU benchmark')
    bench_parser.add_argument(
        '--gpu-id', '-g', type=int, 
        help='Specific GPU to benchmark (default: all GPUs)'
    )
    bench_parser.add_argument(
        '--duration', '-d', type=int, default=60,
        help='Test duration in seconds (default: 60)'
    )
    bench_parser.add_argument(
        '--basic', '-b', action='store_true',
        help='Run basic tests only (faster)'
    )
    bench_parser.add_argument(
        '--enhanced', '-E', action='store_true',
        help='Force enhanced monitoring (comprehensive stress tests)'
    )
    bench_parser.add_argument(
        '--export', '-e', type=str,
        help='Export results to JSON file'
    )
    bench_parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Verbose output'
    )
    bench_parser.add_argument(
        '--mock', '-m', action='store_true',
        help='Use mock GPU (for testing/development)'
    )
    bench_parser.set_defaults(func=cmd_benchmark)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available GPUs')
    list_parser.set_defaults(func=cmd_list)
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Real-time GPU monitoring')
    monitor_parser.add_argument(
        '--gpu-id', '-g', type=int,
        help='GPU to monitor (default: 0)'
    )
    monitor_parser.add_argument(
        '--mock', '-m', action='store_true',
        help='Use mock GPU (for testing/development)'
    )
    monitor_parser.set_defaults(func=cmd_monitor)
    
    # System info command
    sysinfo_parser = subparsers.add_parser('system-info', help='Show baseline system information')
    sysinfo_parser.set_defaults(func=lambda args: print_system_info() or 0)
    
    # Enhanced monitoring status command
    enhanced_parser = subparsers.add_parser('enhanced-status', help='Check enhanced monitoring requirements')
    enhanced_parser.set_defaults(func=lambda args: print_enhanced_monitoring_status() or 0)
    
    # Comprehensive diagnostics command
    comprehensive_parser = subparsers.add_parser('diagnostics', help='Comprehensive GPU diagnostics and version check')
    comprehensive_parser.set_defaults(func=lambda args: print_comprehensive_diagnostics() or 0)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Print banner and system info at the start
    print_banner()
    print_system_info()
    
    # Execute command
    if args.command is None:
        parser.print_help()
        return 0
    
    # For system-info, just print and exit
    if args.command == 'system-info':
        return 0
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
