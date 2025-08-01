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
        """Tests FP32, FP16, BF16, and INT8 performance and speedup."""
        size = 2048 if self.device.type == "cuda" else 256
        results = {}
        fp16_supported = self._check_fp16_support()
        bf16_supported = self._check_bf16_support()
        int8_supported = self._check_int8_support()
        
        # FP32 test
        results["fp32"] = self._test_precision(
            torch.float32, size, duration / 4
        )
        
        # FP16 test
        if fp16_supported:
            results["fp16"] = self._test_precision(
                torch.float16, size, duration / 4
            )
        else:
            results["fp16"] = {"supported": False}
            
        # BF16 test (for newer GPUs)
        if bf16_supported:
            results["bf16"] = self._test_precision(
                torch.bfloat16, size, duration / 4
            )
        else:
            results["bf16"] = {"supported": False}
            
        # INT8 test
        if int8_supported:
            results["int8"] = self._test_precision(
                torch.int8, size, duration / 4
            )
        else:
            results["int8"] = {"supported": False}
        
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
            if "iterations" in results.get("int8", {}):
                results["int8_speedup"] = (
                    results["int8"]["iterations"] / results["fp32"]["iterations"]
                )
        
        # Determine mixed precision capability
        results["mixed_precision_ready"] = fp16_supported or bf16_supported or int8_supported
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
            # Handle INT8 differently - use quantized tensors
            if dtype == torch.int8:
                # Create float tensors first, then quantize
                a_float = torch.randn((size, size), device=self.device, dtype=torch.float32)
                b_float = torch.randn((size, size), device=self.device, dtype=torch.float32)
                
                # Quantize to INT8
                a = torch.quantize_per_tensor(a_float, scale=0.1, zero_point=0, dtype=torch.qint8)
                b = torch.quantize_per_tensor(b_float, scale=0.1, zero_point=0, dtype=torch.qint8)
            else:
                # Regular tensor creation for other dtypes
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
            
            # Calculate FLOPs for this precision
            flops_per_iter = 2 * size**3  # Matrix multiply FLOPs
            total_flops = flops_per_iter * iterations
            tflops = (total_flops / elapsed) / 1e12 if elapsed > 0 else 0
            
            return {
                "supported": True,
                "iterations": iterations,
                "avg_time_per_iter": elapsed / iterations if iterations > 0 else 0,
                "dtype": str(dtype),
                "tflops": tflops,
                "matrix_size": size
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
    
    def _check_int8_support(self):
        """Check if INT8 quantization is supported on this device."""
        if self.device.type == "cpu":
            return False
        try:
            import torch
            cc = torch.cuda.get_device_capability(self.device)
            # INT8 support varies by GPU architecture
            # Generally available on compute capability 6.1+ (Pascal and newer)
            return cc[0] >= 6 and cc[1] >= 1
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
    
    def int8_quantization_test(self, duration: float = 10) -> Dict[str, any]:
        """Tests INT8 quantization performance and accuracy.

        Args:
            duration (float): Duration of the test in seconds (default 10).

        Returns:
            Dict[str, any]: Dictionary with INT8 support, performance metrics, and accuracy.
        """
        if self.device.type == "cpu":
            return {"int8_available": False}
            
        # Check INT8 support
        if not self._check_int8_support():
            return {"int8_available": False}
        
        size = 2048
        results = {}
        
        try:
            # Create FP32 tensors
            a_fp32 = torch.randn((size, size), device=self.device, dtype=torch.float32)
            b_fp32 = torch.randn((size, size), device=self.device, dtype=torch.float32)
            
            # Quantize to INT8
            scale_a = torch.max(torch.abs(a_fp32)) / 127.0
            scale_b = torch.max(torch.abs(b_fp32)) / 127.0
            
            a_int8 = torch.quantize_per_tensor(a_fp32, scale=scale_a, zero_point=0, dtype=torch.qint8)
            b_int8 = torch.quantize_per_tensor(b_fp32, scale=scale_b, zero_point=0, dtype=torch.qint8)
            
            # FP32 reference computation
            start_time = time.time()
            c_fp32 = torch.matmul(a_fp32, b_fp32)
            torch.cuda.synchronize()
            fp32_time = time.time() - start_time
            
            # INT8 computation
            start_time = time.time()
            c_int8 = torch.matmul(a_int8, b_int8)
            torch.cuda.synchronize()
            int8_time = time.time() - start_time
            
            # Dequantize INT8 result for comparison
            c_int8_dequant = c_int8.dequantize()
            
            # Calculate accuracy (relative error)
            relative_error = torch.mean(torch.abs(c_fp32 - c_int8_dequant) / torch.abs(c_fp32))
            
            # Calculate speedup
            speedup = fp32_time / int8_time if int8_time > 0 else 0
            
            # Calculate TFLOPS
            flops = 2 * size**3
            int8_tflops = (flops / int8_time) / 1e12 if int8_time > 0 else 0
            
            results = {
                "int8_available": True,
                "speedup_vs_fp32": speedup,
                "int8_tflops": int8_tflops,
                "relative_error": relative_error.item(),
                "matrix_size": size,
                "fp32_time": fp32_time,
                "int8_time": int8_time
            }
            
        except Exception as e:
            results = {
                "int8_available": False,
                "error": str(e)
            }
        
        return results
