"""
tensi - Interactive tensor visualization library
"""

from .vis import TensorVisualizer

__version__ = "1.0.0"
__all__ = ["TensorVisualizer", "visualize"]

def visualize(tensor, dtype="float32", title="Tensor Visualization", colorscale="Blues"):
    """
    Quick visualization function for tensor shapes.
    
    Args:
        tensor: Input tensor (PyTorch tensor, NumPy array, or nested lists)
        dtype: Data type string (e.g., "float32", "float64", "int32")
        title: Title for the visualization
        colorscale: Plotly colorscale name (e.g., "Blues", "Viridis", "RdBu")
    
    Returns:
        Plotly figure object
    
    Example:
        >>> import tensi
        >>> import torch
        >>> tensor = torch.randn(2, 3, 4)
        >>> fig = tensi.visualize(tensor)
        >>> fig.show()
    """
    viz = TensorVisualizer(colorscale=colorscale)
    return viz.visualize_tensor(tensor, dtype, title)