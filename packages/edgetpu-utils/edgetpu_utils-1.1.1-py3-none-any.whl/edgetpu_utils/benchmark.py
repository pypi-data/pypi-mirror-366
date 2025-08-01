"""Benchmarking utilities for EdgeTPU models."""

import time
from typing import List

import numpy as np
from pycoral.utils.edgetpu import make_interpreter


def benchmark_models(
    model_paths: List[str],
    num_inferences: int,
    device: str = "pci:0",
    percentile: int = 50,
) -> tuple:
    """Benchmark multiple EdgeTPU models."""
    num_models = len(model_paths)

    bench_start_time = time.perf_counter()
    time_spans = []
    for i in range(num_models):
        if device == "pci:0":
            time_span = benchmark_model(
                str(model_paths[i]), num_inferences, device, percentile
            )
        else:
            raise Exception(f"Invalid device type: {device}")
        time_spans.append(time_span)

    bench_time_span = (time.perf_counter() - bench_start_time) * 1000

    return num_models, bench_time_span / num_inferences, time_spans


def benchmark_model(
    model_path: str,
    num_inferences: int = 100,
    device: str = "pci:0",
    percentile: int = 50,
) -> float:
    """Benchmark a single EdgeTPU model."""
    interpreter = make_interpreter(str(model_path), device=device)
    interpreter.allocate_tensors()
    interpreter.invoke()

    time_spans = []
    for _ in range(num_inferences):
        start_time = time.perf_counter()
        interpreter.invoke()
        time_span = (time.perf_counter() - start_time) * 1000
        time_spans.append(time_span)

    return np.percentile(time_spans, percentile)
