import matplotlib.pyplot as plt
import numpy as np


def plot_signal(
    signal: np.ndarray,
    title: str = "Signal",
    ax: plt.Axes = None,
    **kwargs,
) -> tuple[plt.Figure, plt.Axes]:
    """
    Plot the real and imaginary parts of a pulse-shaped signal.

    Args:
        signal: Complex signal array
        start_idx: Starting sample index
        end_idx: Ending sample index
        title_prefix: Prefix for plot titles
    """
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(10, 3))
    else:
        fig = ax[0].figure

    ax.plot(np.real(signal), **kwargs, label="Real Part")
    ax.plot(np.imag(signal), **kwargs, label="Imaginary Part")
    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Amplitude")
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    return fig, ax


def plot_symbols(
    signal: np.ndarray,
    title: str = "Signal in Complex Plane",
    ax: plt.Axes = None,
    **kwargs,
) -> tuple[plt.Figure, plt.Axes]:
    """
    Plot the signal in the complex plane.
    Args:
        signal: Complex signal array
        title: Title for the plot
        ax: Optional matplotlib Axes object to plot on
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(5, 5))
    else:
        fig = ax.figure

    ax.scatter(signal.real, signal.imag, **kwargs)
    ax.axhline(y=0, color="k", linestyle="-", alpha=0.3)
    ax.axvline(x=0, color="k", linestyle="-", alpha=0.3)
    ax.grid(True, alpha=0.5)
    ax.set_xlabel("Real Part")
    ax.set_ylabel("Imaginary Part")
    ax.axis("equal")  # Equal aspect ratio ensures the plot is not distorted
    ax.set_title(title)

    plt.tight_layout()
    return fig, ax