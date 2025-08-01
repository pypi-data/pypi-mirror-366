# EdgeTPU Utils

Utilities for EdgeTPU model partitioning, benchmarking, and TensorFlow Lite operations.

## Installation

```bash
pip install edgetpu-utils
```

## Usage

```python
import edgetpu_utils as eu

# Model partitioning
segments = eu.partition_with_num_ops(model_path, num_segments, ops_per_segment)

# Benchmarking
latency = eu.benchmark_model(model_path, num_inferences=100)

# Model analysis
num_ops = eu.get_num_ops(model_path)
param_size = eu.calculate_parameter_sizes(model_path)
```

## Features

- Model partitioning by operations or layer indices
- EdgeTPU model benchmarking
- TensorFlow Lite model analysis
- Parameter caching token management
