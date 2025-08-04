import torch
import numpy as np
import matplotlib.pyplot as plt

def plot_objective_1D(ax, f, x_boundaries: tuple[float]) -> None:
    x = np.linspace(*x_boundaries, 100)
    z = f(torch.from_numpy(x).float()).detach().numpy()
    ax.plot(x, z)

def plot_point_1D(ax, f, x_highlight: float = None):
    if x_highlight is not None:
        z = f(torch.tensor([x_highlight])).item()
        ax.set_title(f"({x_highlight:.4f}) -> {z:.4f}")
        ax.scatter(x_highlight, z, marker='.', color='k', s=30)
    plt.pause(0.05)

def plot_objective_2D(ax, f, x_boundaries: tuple[int], y_boundaries: tuple[int]) -> None:
    x = np.linspace(*x_boundaries, 100)
    y = np.linspace(*y_boundaries, 100)
    X, Y = np.meshgrid(x, y)
    Z = f(torch.from_numpy(X).float(), torch.from_numpy(Y).float()).detach().numpy()
    ax.plot_surface(X, Y, Z, cmap='plasma', alpha=0.3)

def plot_point_2D(ax, f, x_highlight: float = None, y_highlight: float = None):
    if x_highlight is not None and y_highlight is not None:
        z = f(torch.tensor([x_highlight]), torch.tensor([y_highlight])).item()
        ax.set_title(f"({x_highlight:.4f}, {y_highlight:.4f}) -> {z:.4f}")
        ax.scatter(x_highlight, y_highlight, z, marker='.', color='k', s=30)
    plt.pause(0.05)