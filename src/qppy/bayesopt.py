import warnings
import torch
import time
from botorch.test_functions import Hartmann
from gpytorch.likelihoods.noise_models import NumericalWarning
from .test_functions import StandardizedGoldsteinPrice, StandardizedHartman4
from botorch.models.gp_regression import SingleTaskGP
from botorch.models.transforms.outcome import Standardize
from gpytorch.mlls import ExactMarginalLogLikelihood
from botorch.optim import optimize_acqf
from botorch.acquisition.analytic import ExpectedImprovement
from botorch import fit_gpytorch_mll

warnings.filterwarnings("ignore", category=UserWarning)

def get_objective_function(name: str = "h6"):
    if name == "h6":
        _objective_function = StandardizedHartman4(negate=True)
    elif name == "gp":
        _objective_function = StandardizedGoldsteinPrice(negate=True)
    elif name == "br":
        raise NotImplementedError("Branin test function not implemented yet")
    else:
        raise ValueError(f"Invalid objective function name: {name}")

    return _objective_function

def generate_initial_data(objective_function, n: int = 10):
    # generate training data
    input_data = torch.rand(n, objective_function.dim, device="cpu", dtype=torch.double)
    observed_f = objective_function(input_data).unsqueeze(-1)
    best_observed_value = observed_f.max().item()
    return input_data, observed_f, best_observed_value

    
def initialize_model(input_data, observed_f, state_dict=None):
    # define models for objective and constraint
    train_yvar = torch.full_like(observed_f, 1e-6)
    outcome_transform = Standardize(m=1)
    model = SingleTaskGP(
        train_X=input_data,
        train_Y=observed_f,
        outcome_transform=outcome_transform,
        train_Yvar=train_yvar).to(input_data)

    # load state dict if it is passed
    if state_dict is not None:
        model.load_state_dict(state_dict)

    # return ExactMarginalLogLikelihood(model.likelihood, model), model
    return ExactMarginalLogLikelihood(model.likelihood, model), model

def get_acquisition_function(model, best_f, acquisition_name: str):
    if acquisition_name == "ei":
        _acquisition_function = ExpectedImprovement(model=model, best_f=best_f)
    else:
        raise NotImplementedError("Only EI acquisition implemented so far :(")

    return _acquisition_function

def compute_gap(incumbent, initial_f, global_optimum):
    return ((incumbent - initial_f) / (global_optimum - initial_f)).item()

def run_botorch(acquisition_name: str, objective_name: str, n_trials: int = 100, random_x: bool = False, initial_n: int = 1, verbose: bool = False):
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=NumericalWarning)
    model = None
    objective_function = get_objective_function(name=objective_name)
    input_data, observed_f, best_value = generate_initial_data(n=initial_n, objective_function=objective_function)
    best_values = [best_value]
    gaps = torch.zeros(n_trials)
    t0 = time.monotonic()
    for trial in range(n_trials):
        # get marginal log-lklh and model with current data
        mll, model = initialize_model(
            input_data=input_data,
            observed_f=observed_f,
            state_dict=model.state_dict() if model else None
        )
        # fit model
        fit_gpytorch_mll(mll)
        # update acquisition function definition with best f so far
        acquisition_function = get_acquisition_function(
            acquisition_name=acquisition_name,
            model=model,
            best_f=observed_f.max().item()
        )
        # optimize acquisition function to get new x
        if random_x:
            new_x = torch.rand(1, objective_function.dim)
        else:
            candidate, _ = optimize_acqf(
                acq_function=acquisition_function,
                bounds=objective_function.bounds,
                q=1,
                num_restarts=1,
                raw_samples=1,
                options={"maxiter": 200}
            )
            new_x = candidate.detach()

        new_obj = objective_function(new_x).unsqueeze(-1)

        # update current data
        input_data = torch.cat([input_data, new_x])
        observed_f = torch.cat([observed_f, new_obj])

        # check incumbent (best value so far)
        incumbent = observed_f.max().item()
        best_x = input_data[torch.argmax(observed_f), :]
        
        if verbose:
            msg = f"Trial {trial}, current f={new_obj.item():>4.5}, best f={incumbent:>4.5}"
            print(msg)
        
        gaps[trial] = compute_gap(
            incumbent=incumbent,
            initial_f=observed_f[0],
            global_optimum=objective_function.optimal_value
        )

    t1 = time.monotonic()
    if verbose:
        print(f"Time: {t1-t0:>4.2f}, best x: {best_x.tolist()}")

    return gaps