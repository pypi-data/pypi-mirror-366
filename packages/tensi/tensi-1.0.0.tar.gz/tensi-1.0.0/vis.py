import torch
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class TensorVisualizer:
    def __init__(self, colorscale='Blues'):
        self.colorscale = colorscale
    
    def visualize_tensor(self, tensor, dtype, title):
        """Visualize tensors based on dimensions:
        - 2D/3D [B, S, D]: 2D grids (S×D) for each batch
        - 4D [B, W, H, D]: 3D cubes (W×H×D) for each batch
        - 5D+ : Reshaped to 4D and visualized as 3D cubes
        """
        tensor = torch.tensor(tensor, dtype=getattr(torch, dtype))
        original_shape = tensor.shape
        ndim = len(original_shape)
        
        if ndim == 1:
            # 1D -> 2D (add batch and feature dims)
            tensor = tensor.view(1, 1, -1)
            return self._visualize_2d_grids(tensor, title, original_shape)
        elif ndim == 2:
            tensor = tensor.unsqueeze(0)
            return self._visualize_2d_grids(tensor, title, original_shape)
        elif ndim == 3:
            return self._visualize_2d_grids(tensor, title, original_shape)
        elif ndim == 4:
            return self._visualize_3d_cubes(tensor, title, original_shape)
        else:
            # 5D and higher -> reshape to 4D
            return self._visualize_high_dim(tensor, title, original_shape)
    
    def _visualize_2d_grids(self, tensor, title, original_shape):
        """Visualize 3D tensor [B, S, D] as 2D grids"""
        B, S, D = tensor.shape
        
        # Subplot layout
        cols = min(B, 4)
        rows = (B + cols - 1) // cols
        
        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=[f'Batch {i+1}' for i in range(B)],
            specs=[[{'type': 'heatmap'}] * cols] * rows,
            horizontal_spacing=0.1,
            vertical_spacing=0.1
        )
        
        # Add heatmaps
        for b in range(B):
            row, col = b // cols + 1, b % cols + 1
            
            fig.add_trace(
                go.Heatmap(
                    z=tensor[b].numpy(),
                    colorscale=self.colorscale,
                    showscale=(b == B-1),
                    hovertemplate=f'Batch {b+1}<br>S: %{{y}}<br>D: %{{x}}<br>Value: %{{z:.3f}}<extra></extra>'
                ),
                row=row, col=col
            )
            
            fig.update_xaxes(title_text="D", row=row, col=col)
            fig.update_yaxes(title_text="S", row=row, col=col)
        
        # Dynamic sizing
        cell_size = 40
        margin = 120
        height = max(300, S * cell_size + margin) * rows
        width = max(250, D * cell_size + margin) * cols
        
        fig.update_layout(
            title=f"{title}<br>Shape: {list(original_shape)} | Batches: {B}",
            height=height,
            width=width,
            showlegend=False
        )
        
        return fig
    
    def _visualize_3d_cubes(self, tensor, title, original_shape):
        """Visualize 4D tensor [B, W, H, D] as 3D cubes"""
        B, W, H, D = tensor.shape
        fig = go.Figure()
        
        # Determine dimension labels based on original shape
        ndim = len(original_shape)
        if ndim == 4:
            dim_labels = ["dim 1", "dim 2", "dim 3"]
            batch_label = "Batch"
        else:
            # For reshaped high-dim tensors
            dim_labels = [f"dim {ndim-3}", f"dim {ndim-2}", f"dim {ndim-1}"]
            batch_label = "Merged dims"
        
        for b in range(B):
            x_off = b * (W + 2)
            self._add_cube_wireframe(fig, x_off, 0, 0, W, H, D)
            self._add_grid_lines(fig, x_off, 0, 0, W, H, D)
            self._add_axis_labels(fig, x_off, 0, 0, W, H, D, dim_labels)
            
            # Add batch label above each cube
            fig.add_trace(go.Scatter3d(
                x=[x_off + W/2], y=[0], z=[D + 1],
                mode='text',
                text=[f'{batch_label} {b+1}'],
                textfont=dict(size=16, color='black', family='Arial'),
                hoverinfo='skip', showlegend=False
            ))
        
        # Scene setup
        axis_cfg = dict(showgrid=False, zeroline=False, showticklabels=False)
        
        # Add shape info to title if not already present
        if "Shape:" not in title:
            title = f"{title}<br>Shape: {list(original_shape)} | Batches: {B}"
        
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis=axis_cfg, yaxis=axis_cfg, zaxis=axis_cfg,
                camera=dict(eye=dict(x=2, y=1.8, z=1.6)),
                aspectmode='manual', 
                aspectratio=dict(x=2, y=1, z=1)
            ),
            width=900, height=600
        )
        
        return fig
    
    def _add_cube_wireframe(self, fig, x0, y0, z0, W, H, D):
        """Add wireframe cube with filled faces"""
        # Vertices
        xs = [x0, x0+W, x0+W, x0, x0, x0+W, x0+W, x0]
        ys = [y0, y0, y0+H, y0+H, y0, y0, y0+H, y0+H]
        zs = [z0, z0, z0, z0, z0+D, z0+D, z0+D, z0+D]
        
        # Face quads
        quads = [(0,1,2,3), (4,5,6,7), (0,1,5,4), 
                 (1,2,6,5), (2,3,7,6), (3,0,4,7)]
        
        # Build triangles
        tri_i, tri_j, tri_k = [], [], []
        for a,b,c,d in quads:
            # Both orientations for visibility
            tri_i.extend([a, a, a, a])
            tri_j.extend([b, c, c, b])
            tri_k.extend([c, d, d, c])
        
        fig.add_trace(go.Mesh3d(
            x=xs, y=ys, z=zs,
            i=tri_i, j=tri_j, k=tri_k,
            color='lightblue',
            opacity=1.0,
            flatshading=True,
            lighting=dict(ambient=1, diffuse=0, specular=0, roughness=1),
            hoverinfo='skip',
            showscale=False,
            showlegend=False
        ))
        
        # Edges
        edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),
                 (0,4),(1,5),(2,6),(3,7)]
        for u,v in edges:
            fig.add_trace(go.Scatter3d(
                x=[xs[u],xs[v]], y=[ys[u],ys[v]], z=[zs[u],zs[v]],
                mode='lines', line=dict(color='black', width=3),
                hoverinfo='skip', showlegend=False))
    
    def _add_grid_lines(self, fig, x0, y0, z0, W, H, D):
        """Add internal grid lines"""
        line_cfg = dict(mode='lines', line=dict(color='darkgray', width=2), 
                       hoverinfo='skip', showlegend=False)
        
        # Front/back faces
        for z in [z0, z0+D]:
            for w in range(1, W):
                fig.add_trace(go.Scatter3d(
                    x=[x0+w, x0+w], y=[y0, y0+H], z=[z, z], **line_cfg))
            for h in range(1, H):
                fig.add_trace(go.Scatter3d(
                    x=[x0, x0+W], y=[y0+h, y0+h], z=[z, z], **line_cfg))
        
        # Left/right faces
        for y in [y0, y0+H]:
            for w in range(1, W):
                fig.add_trace(go.Scatter3d(
                    x=[x0+w, x0+w], y=[y, y], z=[z0, z0+D], **line_cfg))
            for d in range(1, D):
                fig.add_trace(go.Scatter3d(
                    x=[x0, x0+W], y=[y, y], z=[z0+d, z0+d], **line_cfg))
        
        # Bottom/top faces
        for x in [x0, x0+W]:
            for h in range(1, H):
                fig.add_trace(go.Scatter3d(
                    x=[x, x], y=[y0+h, y0+h], z=[z0, z0+D], **line_cfg))
            for d in range(1, D):
                fig.add_trace(go.Scatter3d(
                    x=[x, x], y=[y0, y0+H], z=[z0+d, z0+d], **line_cfg))
    
    def _add_axis_labels(self, fig, x0, y0, z0, W, H, D, dim_labels, fontsize=14):
        """Add axis tick labels and dimension names"""
        pad = 0.15 * max(W, H, D)
        text_cfg = dict(mode="text", textfont=dict(size=fontsize, color="black", 
                       family="Courier New"), hoverinfo="skip", showlegend=False)
        label_cfg = dict(mode="text", textfont=dict(size=fontsize+2, color="darkblue", 
                        family="Arial"), hoverinfo="skip", showlegend=False)
        
        # X axis (W) - dim 1
        for w in range(W + 1):
            fig.add_trace(go.Scatter3d(
                x=[x0+w], y=[y0-pad], z=[z0-pad], text=[str(w)], **text_cfg))
        # Add dimension label
        fig.add_trace(go.Scatter3d(
            x=[x0+W/2], y=[y0-pad*2], z=[z0-pad], text=[dim_labels[0]], **label_cfg))
        
        # Y axis (H) - dim 2
        for h in range(H + 1):
            fig.add_trace(go.Scatter3d(
                x=[x0-pad], y=[y0+h], z=[z0-pad], text=[str(h)], **text_cfg))
        # Add dimension label
        fig.add_trace(go.Scatter3d(
            x=[x0-pad*2], y=[y0+H/2], z=[z0-pad], text=[dim_labels[1]], **label_cfg))
        
        # Z axis (D) - dim 3
        for d in range(D + 1):
            fig.add_trace(go.Scatter3d(
                x=[x0-pad], y=[y0-pad], z=[z0+d], text=[str(d)], **text_cfg))
        # Add dimension label
        fig.add_trace(go.Scatter3d(
            x=[x0-pad], y=[y0-pad*2], z=[z0+D/2], text=[dim_labels[2]], **label_cfg))
    
    def _visualize_high_dim(self, tensor, title, original_shape):
        """Visualize high-dimensional tensors by reshaping to 4D"""
        ndim = len(original_shape)
        
        if ndim == 5:
            # 5D [B, C, W, H, D] -> merge B*C as new batch dimension
            B, C, W, H, D = tensor.shape
            tensor = tensor.view(B * C, W, H, D)
            subtitle = f"5D→4D: {list(original_shape)} → [{B}×{C}, {W}, {H}, {D}]"
        elif ndim == 6:
            # 6D [B1, B2, C, W, H, D] -> merge B1*B2*C as batch
            B1, B2, C, W, H, D = tensor.shape
            tensor = tensor.view(B1 * B2 * C, W, H, D)
            subtitle = f"6D→4D: {list(original_shape)} → [{B1}×{B2}×{C}, {W}, {H}, {D}]"
        else:
            # General case: keep last 3 dims, merge rest as batch
            *batch_dims, W, H, D = tensor.shape
            batch_size = torch.prod(torch.tensor(batch_dims)).item()
            tensor = tensor.view(batch_size, W, H, D)
            batch_str = '×'.join(map(str, batch_dims))
            subtitle = f"{ndim}D→4D: {list(original_shape)} → [{batch_str}, {W}, {H}, {D}]"
        
        # Limit number of batches shown
        max_batches = 8
        if tensor.shape[0] > max_batches:
            tensor = tensor[:max_batches]
            subtitle += f" (showing first {max_batches} of {tensor.shape[0]} batches)"
        
        full_title = f"{title}<br>{subtitle}"
        return self._visualize_3d_cubes(tensor, full_title, original_shape)

# Demo
def demo():
    viz = TensorVisualizer()
    
    print("=== Tensor Visualization Demo ===\n")
    
    # 1D tensor
    print("1D Tensor [5]")
    tensor_1d = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
    fig_1d = viz.visualize_tensor(tensor_1d, "float32", "1D Tensor")
    fig_1d.show()
    
    # 2D tensor
    print("\n2D Tensor [3, 2]")
    tensor_2d = [[1.2, 2.3], [3.1, 4.3], [5.2, 6.2]]
    fig_2d = viz.visualize_tensor(tensor_2d, "float32", "2D Tensor")
    fig_2d.show()
    
    # 3D tensor
    print("\n3D Tensor [2, 3, 4]")
    tensor_3d = torch.randn(2, 3, 4)
    fig_3d = viz.visualize_tensor(tensor_3d, "float32", "3D Tensor")
    fig_3d.show()
    
    # 4D tensor
    print("\n4D Tensor [2, 2, 3, 4]")
    tensor_4d = torch.randn(2, 2, 3, 4)
    fig_4d = viz.visualize_tensor(tensor_4d, "float32", "4D Tensor")
    fig_4d.show()
    
    # 5D tensor
    print("\n5D Tensor [2, 3, 4, 5, 6]")
    tensor_5d = torch.randn(2, 3, 4, 5, 6)
    fig_5d = viz.visualize_tensor(tensor_5d, "float32", "5D Tensor")
    fig_5d.show()
    
    # 6D tensor
    print("\n6D Tensor [2, 2, 2, 3, 4, 5]")
    tensor_6d = torch.randn(2, 2, 2, 3, 4, 5)
    fig_6d = viz.visualize_tensor(tensor_6d, "float32", "6D Tensor")
    fig_6d.show()
    
    # 7D tensor
    print("\n7D Tensor [2, 2, 2, 2, 3, 4, 5]")
    tensor_7d = torch.randn(2, 2, 2, 2, 3, 4, 5)
    fig_7d = viz.visualize_tensor(tensor_7d, "float32", "7D Tensor")
    fig_7d.show()

if __name__ == "__main__":
    demo()