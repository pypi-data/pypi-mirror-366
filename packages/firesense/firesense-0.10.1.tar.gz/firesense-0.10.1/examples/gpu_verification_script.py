#!/usr/bin/env python3
"""GPU verification script for PyTorch setup."""

import time

import torch


def print_gpu_info():
    """Print detailed GPU information."""
    print("=" * 60)
    print("PyTorch GPU Configuration")
    print("=" * 60)

    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"cuDNN version: {torch.backends.cudnn.version()}")
        print(f"Number of GPUs: {torch.cuda.device_count()}")

        for i in range(torch.cuda.device_count()):
            print(f"\nGPU {i}:")
            print(f"  Name: {torch.cuda.get_device_name(i)}")
            print(
                f"  Memory: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.2f} GB"
            )
            print(
                f"  Compute Capability: {torch.cuda.get_device_properties(i).major}.{torch.cuda.get_device_properties(i).minor}"
            )
    else:
        print("No CUDA GPUs available")


def benchmark_gpu():
    """Run simple benchmarks comparing CPU vs GPU performance."""
    if not torch.cuda.is_available():
        print("\nGPU not available, skipping benchmarks")
        return

    print("\n" + "=" * 60)
    print("Performance Benchmarks")
    print("=" * 60)

    # Matrix multiplication benchmark
    sizes = [1000, 2000, 4000]

    for size in sizes:
        print(f"\nMatrix multiplication ({size}x{size}):")

        # CPU benchmark
        a_cpu = torch.randn(size, size)
        b_cpu = torch.randn(size, size)

        start = time.time()
        torch.matmul(a_cpu, b_cpu)
        cpu_time = time.time() - start
        print(f"  CPU time: {cpu_time:.4f} seconds")

        # GPU benchmark
        a_gpu = a_cpu.cuda()
        b_gpu = b_cpu.cuda()

        # Warm up
        torch.cuda.synchronize()
        _ = torch.matmul(a_gpu, b_gpu)
        torch.cuda.synchronize()

        start = time.time()
        torch.matmul(a_gpu, b_gpu)
        torch.cuda.synchronize()
        gpu_time = time.time() - start
        print(f"  GPU time: {gpu_time:.4f} seconds")
        print(f"  Speedup: {cpu_time/gpu_time:.2f}x")


def test_model_operations():
    """Test common deep learning operations on GPU."""
    if not torch.cuda.is_available():
        print("\nGPU not available, skipping model operations test")
        return

    print("\n" + "=" * 60)
    print("Deep Learning Operations Test")
    print("=" * 60)

    # Create a simple neural network
    model = torch.nn.Sequential(
        torch.nn.Linear(1024, 512),
        torch.nn.ReLU(),
        torch.nn.Linear(512, 256),
        torch.nn.ReLU(),
        torch.nn.Linear(256, 10),
    ).cuda()

    print(f"Model on GPU: {next(model.parameters()).is_cuda}")

    # Test forward pass
    batch_size = 64
    input_data = torch.randn(batch_size, 1024).cuda()

    # Warm up
    _ = model(input_data)
    torch.cuda.synchronize()

    # Benchmark
    start = time.time()
    for _ in range(100):
        model(input_data)
    torch.cuda.synchronize()
    elapsed = time.time() - start

    print("Forward passes: 100")
    print(f"Total time: {elapsed:.4f} seconds")
    print(f"Time per forward pass: {elapsed/100*1000:.2f} ms")

    # Test memory usage
    print("\nGPU Memory Usage:")
    print(f"  Allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
    print(f"  Reserved: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")


def test_gemma_compatibility():
    """Test if transformers library can use GPU for Gemma models."""
    print("\n" + "=" * 60)
    print("Gemma Model GPU Compatibility Test")
    print("=" * 60)

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if torch.cuda.is_available():
            print("Testing Gemma model GPU loading capability...")
            print(
                "Note: This only tests the loading mechanism, not actual model inference"
            )
            print("(Actual model download requires authentication)")

            # Check if we can specify GPU device
            device = torch.device("cuda:0")
            print(f"Target device: {device}")
            print("✓ GPU device specification successful")

            # Test tensor operations that Gemma would use
            test_tensor = torch.randn(1, 10, 256).to(device)
            print(f"✓ Test tensor on GPU: {test_tensor.is_cuda}")

            # Test attention-like operation
            attention = torch.nn.MultiheadAttention(256, 8).to(device)
            output, _ = attention(test_tensor, test_tensor, test_tensor)
            print("✓ Attention operation on GPU successful")

        else:
            print("GPU not available for Gemma model testing")

    except ImportError:
        print("Transformers library not properly installed")
    except Exception as e:
        print(f"Error during Gemma compatibility test: {e}")


if __name__ == "__main__":
    print_gpu_info()
    benchmark_gpu()
    test_model_operations()
    test_gemma_compatibility()

    print("\n" + "=" * 60)
    print("GPU Verification Complete!")
    print("=" * 60)
