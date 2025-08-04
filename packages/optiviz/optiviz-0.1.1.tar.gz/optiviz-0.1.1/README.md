# OptiViz
OptiViz enables effortless visualisation of the optimisation sequence of *any* PyTorch optimiser on *any* differentiable function in one or two variables. OptiViz might find educational use in an introductory nonlinear optimisation or deep learning class.

![Vanilla gradient descent minimising a convex quadratic form.](https://github.com/ronitkunk/optiviz/blob/main/sgd.png)

# Installation
To install OptiViz, please use:
```sh
pip install optiviz
```

# Usage
All functionality of OptiViz is exposed through the `optiviz.optimise` function.
```python
import torch
from optiviz import optimise
```
Any optimisation problem has an objective function. OptiViz works with differentiable, real-valued objective functions in one or two variables.
```math
f : \mathbb{R} \rightarrow \mathbb{R}
```
```math
g : \mathbb{R}^2 \rightarrow \mathbb{R}
```
In code, every input and output to the objective function must be a `torch.Tensor` of shape `(1,)`
```python
def f(x: torch.Tensor) -> torch.Tensor:
    """
    Example of an objective function in one variable.
    """
    return x ** 2
def g(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """
    Example of an objective function in two variables.
    """
    return x ** 2 + y ** 2 + x.sin() * y.sin()
```
The `optiviz.optimise` function (please see docstring) is used to visualise the optimisation sequence of the objective function using a PyTorch optimiser.
```python
arg_g_min = optimise(
        g, # objective function
        (12.5, 12.5), # initial values of the parameters being adjusted
        plot_boundary=25,
        iters=100,
        optimiser=torch.optim.Adam, # PyTorch-compatible optimiser
        lr=5e-1
    )
```