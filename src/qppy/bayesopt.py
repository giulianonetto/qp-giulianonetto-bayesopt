import warnings
import torch
import time
from botorch.test_functions import Hartmann
from gpytorch.likelihoods.noise_models import NumericalWarning
from .test_functions import *
from botorch.models.gp_regression import SingleTaskGP
from botorch.models.transforms.outcome import Standardize
from gpytorch.mlls import ExactMarginalLogLikelihood
from botorch.optim import optimize_acqf
from botorch.acquisition import ExpectedImprovement, qKnowledgeGradient
from botorch.acquisition.analytic import LogProbabilityOfImprovement
from botorch import fit_gpytorch_mll

def get_objective_function(name: str = "h6"):
    if name == "h6":
        _objective_function = StandardizedHartman4(negate=True)
    elif name == "gp":
        _objective_function = StandardizedGoldsteinPrice(negate=True)
    elif name == "ros":
        _objective_function = StandardizedRosenbrock4(negate=True)
    else:
        raise ValueError(f"Invalid objective function name: {name}")

    return _objective_function

def generate_initial_data(objective_function, n: int = 10):
    # generate training data
    input_data = torch.rand(n, objective_function.dim, device="cpu", dtype=torch.double)
    observed_f = objective_function(input_data).unsqueeze(-1)
    return input_data, observed_f

    
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
    elif acquisition_name == "kg":
        _acquisition_function = qKnowledgeGradient(model=model, num_fantasies=128)
    elif acquisition_name == "lpi":
        _acquisition_function = LogProbabilityOfImprovement(model=model, best_f=best_f)
    else:
        raise NotImplementedError("Only EI acquisition implemented so far :(")

    return _acquisition_function

def compute_gap(incumbent, initial_f, global_optimum):
    return ((incumbent - initial_f) / (global_optimum - initial_f)).item()

def run_botorch(acquisition_name: str, objective_name: str, n_trials: int = 100, random_x: bool = False, initial_n: int = 1, verbose: bool = False):
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=NumericalWarning)
    model, state_dict = None, None
    objective_function = get_objective_function(name=objective_name)
    input_data, observed_f = generate_initial_data(n=initial_n, objective_function=objective_function)
    gaps = torch.zeros(n_trials)
    t0 = time.monotonic()
    for trial in range(n_trials):
        if random_x:
            # baseline: don't use BayesOpt at all, just sample x uniformly at random
            new_x = (objective_function.bounds[0] - objective_function.bounds[1]) * torch.rand(1, objective_function.dim) + objective_function.bounds[1]
        else:
            # get marginal log-lklh and model with current data
            if model:
                state_dict = model.state_dict()

            mll, model = initialize_model(
                input_data=input_data,
                observed_f=observed_f,
                state_dict=state_dict
            )
            # fit model
            fit_gpytorch_mll(mll)
            # update acquisition function definition with best f so far
            acquisition_function = get_acquisition_function(
                acquisition_name=acquisition_name,
                model=model,
                best_f=observed_f.max().item()
            )
            num_restarts, raw_samples = 1, 1
            if acquisition_name in ["kg"]:
                num_restarts, raw_samples = 10, 512

            # optimize acquisition function to get new x
            candidate, _ = optimize_acqf(
                acq_function=acquisition_function,
                bounds=objective_function.bounds,
                q=1,
                num_restarts=num_restarts,
                raw_samples=raw_samples,
                options={"maxiter": 200}
            )
            new_x = candidate.detach()

        new_obj = objective_function(new_x).unsqueeze(-1)

        # update current data
        input_data = torch.cat([input_data, new_x])
        observed_f = torch.cat([observed_f, new_obj])

        # check incumbent (best value so far)
        incumbent = observed_f.max().item()
        
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