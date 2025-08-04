import torch
from optiviz import optimise

X = [-2.0, -1.0, 0.0, 1.0, 2.0]
Y = [2.0, 3.0, 4.0, 5.0, 6.0]

def MSE(w: torch.Tensor, b: torch.Tensor, x=torch.tensor(X), y=torch.tensor(Y)):
    errors = [((w * x[i] + b - y[i]) ** 2) for i in range(x.shape[0])]
    return torch.stack(errors).mean(dim=0) / 2

def test_ols_optimisation():
    w_opt, b_opt = optimise(
        MSE,
        (12.5, 12.5),
        plot_boundary=50,
        iters=100,
        optimiser=torch.optim.SGD,
        lr=1e-1
    )
    assert abs(w_opt - 1) < 0.05 and abs(b_opt - 4) < 0.05
