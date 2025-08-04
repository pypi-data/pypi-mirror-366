import torch
from optiviz import optimise

def f(x: torch.Tensor) -> torch.Tensor:
    return x ** 2

def g(x: torch.Tensor) -> torch.Tensor:
    return x ** 2 + x.sin() ** 2

def test_f_minimizer_1d():
    arg_f_min = optimise(
        f,
        init_vector=(12.5,),
        plot_boundary=25,
        iters=100,
        optimiser=torch.optim.SGD,
        lr=1e-1
    )
    assert abs(arg_f_min[0]) < 0.05

def test_g_minimizer_1d():
    arg_g_min = optimise(
        g,
        init_vector=(12.5,),
        plot_boundary=25,
        iters=100,
        optimiser=torch.optim.Adam,
        lr=5e-1
    )
    assert abs(arg_g_min[0]) < 0.05
