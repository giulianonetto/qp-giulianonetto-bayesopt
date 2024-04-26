from botorch.test_functions.synthetic import SyntheticTestFunction
from torch import Tensor, log
import torch

# TODO: implement H6

class StandardizedGoldsteinPrice(SyntheticTestFunction):
    r"""GoldsteinPrice test function.

    Implementation from `DiceOptim::goldsteinprice` (in R).
    """

    dim = 2
    _bounds = [(0.0, 1.0), (0.0, 1.0)]
    _optimal_value = -3.129172
    _optimizers = [(0.5, 0.25)]
     
    def evaluate_true(self, X: Tensor) -> Tensor:
        assert X.dim() == 2, "Must be tensor of dim=2"
        m = 8.6928
        s = 2.4269
        n_inputs = X.shape[0]
        fs = torch.zeros(n_inputs, dtype=torch.double)
        for i, x in enumerate(X):
            x1 = 4.0 * X[i, 0] - 2.0
            x2 = 4.0 * X[i, 1] - 2.0
            a = 1.0 + (x1 + x2 + 1.0)**2 * (19.0 - 14.0 * x1 + 3.0 * x1**2 - 14.0 * x2 + 6.0 * x1 * x2 + 3.0 * x2**2)
            b = 30.0 + (2.0 * x1 - 3.0 * x2)**2 * (18.0 - 32.0 * x1 + 12.0 * x1**2 + 48.0 * x2 - 36.0 * x1 * x2 + 27.0 * x2**2)
            fs[i] = (log(a * b) - m) / s

        return fs

class StandardizedHartman4(SyntheticTestFunction):
    r"""Hartman 4 test function.

    Implementation from `DiceOptim::hartman4` (in R).
    """

    dim = 4
    _bounds = [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0), (0.0, 1.0)]
    _optimal_value = -3.135474
    _optimizers = [(0.1873, 0.1906, 0.5566, 0.2647)]
     
    def evaluate_true(self, X: Tensor) -> Tensor:

        assert X.dim() == 2, "Must be tensor of dim=2"

        a = torch.tensor(
            [
                [10.0, 0.05, 3.0, 17.0],
                [3.0, 10.0, 3.5, 8.0],
                [17.0, 17.0, 1.7, 0.05],
                [3.5, 0.1, 10.0, 10.0],
                [1.7, 8.0, 17.0, 0.1],
                [8.0, 14.0, 8.0, 14.0]
            ]
        )
        p = torch.tensor(
            [
                [0.1312, 0.2329, 0.2348, 0.4047],
                [0.1696, 0.4135, 0.1451, 0.8828],
                [0.5569, 0.8307, 0.3522, 0.8732],
                [0.0124, 0.3736, 0.2883, 0.5743],
                [0.8283, 0.1004, 0.3047, 0.1091], 
                [0.5886, 0.9991, 0.665, 0.0381]  
            ]
        )

        c = torch.tensor([1.0, 1.2, 3.0, 3.2])
        m = -1.1
        s = 0.8387
        _seq = torch.arange(0, 4)

        n_inputs = X.shape[0]
        fs = torch.zeros(n_inputs, dtype=torch.double)
        for k, x in enumerate(X):
            d = torch.zeros(4, dtype=torch.double)
            for i in range(4):
                d[i] = (a[_seq, i] * (x - p[_seq, i]) ** 2).sum()

            fs[k] = (-(c * torch.exp(-d)).sum() - m) / s

        return fs

class StandardizedRosenbrock4(SyntheticTestFunction):
    r"""Rosenbrock 4D test function.

    Implementation from `DiceOptim::rosenbrock4` (in R).
    """

    dim = 4
    _bounds = [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0), (0.0, 1.0)]
    _optimal_value = -1.019701
    _optimizers = [(0.4, 0.4, 0.4, 0.4)]
     
    def evaluate_true(self, X: Tensor) -> Tensor:
        assert X.dim() == 2, "Must be tensor of dim=2"
        m = 382658.057227524
        s = 375264.858362295
        n_inputs = X.shape[0]
        fs = torch.zeros(n_inputs, dtype=torch.double)
        for i, x in enumerate(X):
            x = 15 * x - 5
            x1 = x[:3]
            x2 = x[1:4]
            f = (100 * (x2 - x1**2)**2 + (1 - x1)**2).sum()
            fs[i] = (f - m) / s

        return fs