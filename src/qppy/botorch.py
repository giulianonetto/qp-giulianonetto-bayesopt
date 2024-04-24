import torch
from botorch.test_functions import Hartmann
from botorch.models.gp_regression import SingleTaskGP
from botorch.models.transforms.outcome import Standardize
from gpytorch.mlls import ExactMarginalLogLikelihood
from botorch.optim import optimize_acqf
from botorch.acquisition.analytic import ExpectedImprovement, ExpectedImprovement
from botorch import fit_gpytorch_mll
import time
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

device = torch.device("cuda:3" if torch.cuda.is_available() else "cpu")
dtype = torch.double

bounds = torch.tensor([[0.0] * 6, [1.0] * 6], device=device, dtype=dtype)


neg_hartmann6 = Hartmann(negate=True)

def objective(X):
    return neg_hartmann6(X).unsqueeze(-1)  # add output dimension

def generate_initial_data(n=10):
    # generate training data
    train_x = torch.rand(n, 6, device=device, dtype=dtype)
    train_obj = objective(train_x)
    best_observed_value = train_obj.max().item()
    return train_x, train_obj, best_observed_value

    
def initialize_model(train_x, train_obj, state_dict=None):
    # define models for objective and constraint
    train_yvar = torch.full_like(train_obj, 1e-6)
    outcome_transform = Standardize(m=1)
    model = SingleTaskGP(
        train_X=train_x,
        train_Y=train_obj,
        outcome_transform=outcome_transform,
        train_Yvar=train_yvar).to(train_x)

    # load state dict if it is passed
    if state_dict is not None:
        model.load_state_dict(state_dict)

    return ExactMarginalLogLikelihood(model.likelihood, model), model

def run_botorch(initial_data, random_x=False, n_trials=100, verbose=False):
    warnings.filterwarnings("ignore", category=UserWarning)
    model = None
    train_x, train_obj, best_value = initial_data
    best_values = [best_value]
    t0 = time.monotonic()
    for trial in range(1, n_trials + 1):
        # get marginal log-lklh and model with current data
        mll, model = initialize_model(
            train_x, train_obj,
            state_dict=model.state_dict() if model else None
        )
        # fit model
        fit_gpytorch_mll(mll)
        # update acquisition function definition with best f so far
        acquisition_function = ExpectedImprovement(model=model, best_f=train_obj.max().item())
        # optimize acquisition function to get new x
        if not random_x:
            candidate, _ = optimize_acqf(
                acq_function=acquisition_function,
                bounds=bounds,
                q=1,
                num_restarts=1,
                raw_samples=1,
                options={"maxiter": 200},
            )
            new_x = candidate.detach()  # x that maximizes acquisition function
        else:
            new_x = torch.rand(1, 6)

        new_obj = objective(new_x)  # objetive at new x
        # update current data
        train_x = torch.cat([train_x, new_x])
        train_obj = torch.cat([train_obj, new_obj])
        objective_values = objective(train_x)
        best_value = objective_values.max().item()
        best_x = train_x[torch.argmax(objective_values), :]
        best_values.append(best_value)    
        
        if verbose:
            msg = f"Trial {trial}, current f={new_obj.item():>4.5}, best f={best_value:>4.5}"
            print(msg)
        
        best_values.append(best_value)

    t1 = time.monotonic()
    if verbose:
        print(f"Time: {t1-t0:>4.2f}")
    return best_value, best_x