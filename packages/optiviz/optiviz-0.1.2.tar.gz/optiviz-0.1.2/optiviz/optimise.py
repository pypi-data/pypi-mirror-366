import torch
from typing import Type
import inspect
import matplotlib.pyplot as plt

from .visualise import plot_objective_1D, plot_point_1D, plot_objective_2D, plot_point_2D

def optimise(fn, init_vector: tuple[float], plot_boundary: float=25, iters: int=1000, optimiser: Type[torch.optim.Optimizer]=torch.optim.Adam, **kwargs) -> tuple[float]:
    """
    Visualises the minimisation sequence of the given differentiable function `fn` using the given optimiser.
    Arguments:
        `fn` : The differentiable function to be minimised. Must take exactly 1 or 2 non-default arguments. Return value and each argument must be a `torch.Tensor` with shape (1,).
        `init_vector`: A tuple of the same dimension as the number of arguments of `fn`, specifying the initial values of the function parameters.
        `plot_boundary`: Length of the the plot boundary in all dimensions in the parameter space.
        `iters`: Number of optimiser iterations; defaults to 1000.
        `optimiser`: Optimisation algorithm to use. Must be a `torch.optim.Optimizer` subclass (not instance); defaults to Adam (https://arxiv.org/abs/1412.6980).
        `**kwargs`: any keyword arguments for the optimiser; e.g. lr

    Returns:
        Depending on fn, a 1-tuple or 2-tuple of the estimated optimal parameters.
    """
    sig = inspect.signature(fn)
    input_dim = sum(p.default == inspect._empty for p in sig.parameters.values())

    assert input_dim==1 or input_dim==2, f"'fn' must take either 1 or 2 non-default arguments (received {input_dim})."
    assert input_dim==len(init_vector), f"Number of non-default arguments of 'fn' ({input_dim}) does not match number of initial values in 'init_vector' ({len(init_vector)})."

    x = tuple([torch.tensor([x_i], requires_grad=True) for x_i in init_vector])

    plt.ion()
    ax = None
    if input_dim==1:
        ax = plt.figure().add_subplot()
        plot_objective_1D(ax, fn, (init_vector[0]-plot_boundary/2, init_vector[0]+plot_boundary/2))
    elif input_dim==2:
        ax = plt.figure().add_subplot(projection='3d')
        plot_objective_2D(ax, fn, (init_vector[0]-plot_boundary/2, init_vector[0]+plot_boundary/2), (init_vector[1]-plot_boundary/2, init_vector[1]+plot_boundary/2))

    optimiser = optimiser(list(x), **kwargs)

    for _ in range(iters):
        objective = fn(*x)

        if input_dim==1:
            plot_point_1D(ax, fn, x[0].item())
        elif input_dim==2:
            plot_point_2D(ax, fn, x[0].item(), x[1].item())

        optimiser.zero_grad()
        objective.backward()
        optimiser.step()
    
    plt.ioff()
    return tuple([x_i.item() for x_i in x])