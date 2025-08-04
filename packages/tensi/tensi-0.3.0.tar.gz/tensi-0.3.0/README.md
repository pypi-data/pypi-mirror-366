# Tensi

**Interactive tensor shape visualization**

Tensi turns multi‑dimensional tensors into intuitive, interactive geometry so you can instantly see what your data looks like.

*I built Tensi while wrangling distributed sharding‑and‑concatenation of latent tensors. Interactive geometric visuals of tensor shapes finally made the process make sense.*

## Installation

```bash
pip install tensi
```



## Quick Start

```python
import tensi
import torch

# Visualize a 3D tensor
tensor = torch.randn(2, 4, 5)  # [Batch, Rows, Cols]
fig = tensi.visualize(tensor)
fig.show()
```

## Usage Examples

### Basic Usage

```python
import tensi
import torch
import numpy as np

# Using the quick visualize function
tensor = torch.randn(3, 4, 5)
fig = tensi.visualize(tensor, title="My Tensor")
fig.show()

# Using different data types
data = [[1, 2, 3], [4, 5, 6]]
fig = tensi.visualize(data, dtype="int32")
fig.show()

# Using numpy arrays
np_array = np.random.rand(2, 3, 4)
fig = tensi.visualize(np_array, dtype="float64")
fig.show()
```



### Tensor Shapes

```python
# 2D Tensor
tensor_2d = torch.randn(5, 7)  # [Rows, Cols]
fig = tensi.visualize(tensor_2d, title="2D Tensor")
fig.show()

# 3D Tensor
tensor_3d = torch.randn(3, 5, 7)  # [Batch, Rows, Cols]
fig = tensi.visualize(tensor_3d, title="3D Tensor - 3 Batches")
fig.show()

# 4D Tensor
tensor_4d = torch.randn(2, 4, 5, 6)  # [Batch, Width, Height, Depth]
fig = tensi.visualize(tensor_4d, title="4D Tensor - 2 Batches")
fig.show()
```

### Save Visualizations

```python
# Save as interactive HTML
fig = tensi.visualize(tensor)
fig.write_html("tensor_visualization.html")

# Save as static image (requires kaleido)
fig.write_image("tensor_visualization.png")
```

## Requirements

- Python >= 3.7
- PyTorch >= 1.8.0
- NumPy >= 1.19.0
- Plotly >= 5.0.0


## Contributing

Contributions are welcome! Please feel free to submit a PR.

## Links

- [Github](https://github.com/DorsaRoh/tensi)
- [PyPI](https://pypi.org/project/tensi/)