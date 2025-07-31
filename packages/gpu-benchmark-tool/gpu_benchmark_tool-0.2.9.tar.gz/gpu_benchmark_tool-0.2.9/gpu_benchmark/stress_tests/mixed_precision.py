"""Mixed precision stress tests.

This module provides tests for mixed precision (FP16, BF16) and tensor core performance on GPUs.
"""

import torch
import time
from typing import Dict


class MixedPrecisionTest:
    """Test mixed precision capabilities and tensor core performance.

    Args:
        device (torch.device): The device (CPU or GPU) to run tests on.
    """
    
    def __init__(self, device: torch.device):
        self.device = device
        
    def run_test(self, duration: float = 10) -> Dict[str, any]:
        """Tests FP32, FP16, and BF16 performance and speedup."""
        size = 2048 if self.device.type == "cuda" else 256
        results = {}
        fp16_supported = self._check_fp16_support()
        bf16_supported = self._check_bf16_support()
        # FP32 test
        results["fp32"] = self._test_precision(
            torch.float32, size, duration / 3
        )
        # FP16 test
        if fp16_supported:
            results["fp16"] = self._test_precision(
                torch.float16, size, duration / 3
            )
        else:
            results["fp16"] = {"supported": False}
        # BF16 test (for newer GPUs)
        if bf16_supported:
            results["bf16"] = self._test_precision(
                torch.bfloat16, size, duration / 3
            )
        else:
            results["bf16"] = {"supported": False}
        # Calculate speedups
        if results["fp32"].get("iterations", 0) > 0:
            if "iterations" in results.get("fp16", {}):
                results["fp16_speedup"] = (
                    results["fp16"]["iterations"] / results["fp32"]["iterations"]
                )
            if "iterations" in results.get("bf16", {}):
                results["bf16_speedup"] = (
                    results["bf16"]["iterations"] / results["fp32"]["iterations"]
                )
        # Determine mixed precision capability
        results["mixed_precision_ready"] = fp16_supported or bf16_supported
        return results
    
    def _test_precision(self, dtype: torch.dtype, size: int, duration: float) -> Dict[str, any]:
        """Tests performance for a specific precision.

        Args:
            dtype (torch.dtype): Data type to test (e.g., torch.float16).
            size (int): Matrix dimension.
            duration (float): Duration of the test in seconds.

        Returns:
            Dict[str, any]: Dictionary with support, iterations, average time, and dtype.
        """
        try:
            a = torch.randn((size, size), device=self.device, dtype=dtype)
            b = torch.randn((size, size), device=self.device, dtype=dtype)
            
            start_time = time.time()
            iterations = 0
            
            while time.time() - start_time < duration:
                c = torch.matmul(a, b)
                if self.device.type == "cuda":
                    torch.cuda.synchronize()
                iterations += 1
            
            elapsed = time.time() - start_time
            
            return {
                "supported": True,
                "iterations": iterations,
                "avg_time_per_iter": elapsed / iterations if iterations > 0 else 0,
                "dtype": str(dtype)
            }
            
        except Exception as e:
            return {
                "supported": False,
                "error": str(e)
            }
    
    def _check_fp16_support(self):
        if self.device.type == "cpu":
            return False
        try:
            import torch
            cc = torch.cuda.get_device_capability(self.device)
            return cc[0] >= 7
        except Exception:
            return False
    def _check_bf16_support(self):
        if self.device.type == "cpu":
            return False
        try:
            import torch
            cc = torch.cuda.get_device_capability(self.device)
            return cc[0] >= 8
        except Exception:
            return False
    
    def tensor_core_test(self, duration: float = 10) -> Dict[str, any]:
        """Tests Tensor Core performance if available.

        Args:
            duration (float): Duration of the test in seconds (default 10).

        Returns:
            Dict[str, any]: Dictionary with tensor core availability, iterations, TFLOPS, and matrix size.
        """
        if self.device.type == "cpu":
            return {"tensor_cores_available": False}
            
        # Tensor cores require specific dimensions (multiples of 8)
        size = 4096
        
        # Check if tensor cores are available
        device_id = self.device.index if self.device.index is not None else 0
        major, _ = torch.cuda.get_device_capability(device_id)
        
        if major < 7:  # Tensor cores introduced in Volta (7.0)
            return {"tensor_cores_available": False}
        
        # Run with tensor core friendly dimensions
        torch.backends.cuda.matmul.allow_tf32 = True
        
        a = torch.randn((size, size), device=self.device, dtype=torch.float32)
        b = torch.randn((size, size), device=self.device, dtype=torch.float32)
        
        start_time = time.time()
        iterations = 0
        
        while time.time() - start_time < duration:
            c = torch.matmul(a, b)
            torch.cuda.synchronize()
            iterations += 1
        
        elapsed = time.time() - start_time
        
        return {
            "tensor_cores_available": True,
            "iterations": iterations,
            "tflops": (2 * size**3 * iterations / elapsed) / 1e12,
            "matrix_size": size
        }
