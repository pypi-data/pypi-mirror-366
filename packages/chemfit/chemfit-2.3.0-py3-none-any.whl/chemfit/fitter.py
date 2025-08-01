import logging
import numpy as np
from typing import Optional, Callable, Any
import time

from numbers import Real
from functools import wraps

from chemfit.exceptions import FactoryException

from dataclasses import dataclass

import math

from pydictnest import (
    flatten_dict,
    unflatten_dict,
)

logger = logging.getLogger(__name__)


@dataclass
class FitInfo:
    initial_value: float = -1.0
    final_value: float = -1.0
    time_taken: float = -1.0
    n_evals: int = 0


class Fitter:
    """
    Fits parameters by minimizing an objective function.
    """

    def __init__(
        self,
        objective_function: Callable[[dict], float],
        initial_params: dict,
        bounds: Optional[dict] = None,
    ):
        """
        Args:
           objective_function (Callable[[dict], float]):
               The objective function to be minimized.
            initial_params (dict):
                Initial values of the parameters
            bound (Optional[dict]):
                Dictionary of parameter bounds
        """

        self.objective_function = self.ob_func_wrapper(objective_function)

        self.initial_parameters = initial_params

        if bounds is None:
            self.bounds = {}
        else:
            self.bounds = bounds

        self.value_bad_params = 1e5

        self.info = FitInfo()

    def ob_func_wrapper(self, ob_func: Any) -> float:
        """Wraps the objective function and applies some checks plus logging"""

        @wraps(ob_func)
        def wrapped_ob_func(params: dict):
            # first we try if we can get a value at all
            try:
                value = ob_func(params)
                self.info.n_evals += 1
            except FactoryException as e:
                # If we catch a factory exception we should just crash the code, therefore we re-raise
                logger.exception(
                    "Caught factory exception while evaluating objective function.",
                    stack_info=True,
                    stacklevel=2,
                )
                raise e
            except Exception:
                # On a general exception we continue execution, since it might just be a bad parameter region
                logger.debug(
                    f"Caught exception with {params = }. Clipping loss to {self.value_bad_params}",
                    exc_info=True,
                    stack_info=True,
                    stacklevel=2,
                )
                value = self.value_bad_params

            # then we make sure that the value is a float
            if not isinstance(value, Real):
                logger.debug(
                    f"Objective function did not return a single float, but returned `{value}` with type {type(value)}. Clipping loss to {self.value_bad_params}"
                )
                value = self.value_bad_params

            if math.isnan(value):
                logger.debug(
                    f"Objective function returned NaN. Clipping loss to {self.value_bad_params}"
                )
                value = self.value_bad_params

            return value

        return wrapped_ob_func

    def hook_pre_fit(self):
        self.info = FitInfo()

        logger.info("Start fitting")
        logger.info(f"    Initial parameters: {self.initial_parameters}")
        logger.info(f"    Bounds: {self.bounds}")

        self.info.initial_value = self.objective_function(self.initial_parameters)
        logger.info(f"    Initial obj func: {self.info.initial_value}")

        if self.info.initial_value == self.value_bad_params:
            logger.warning(
                f"Starting optimization in a `bad` region. Objective function could not be evaluated properly. Loss has been set to {self.value_bad_params = }"
            )
        elif self.info.initial_value > self.value_bad_params:
            new_value_bad_params = 1.1 * self.info.initial_value
            logger.warning(
                f"Starting optimization in a high loss region. Loss is {self.info.initial_value}, which is greater than {self.value_bad_params = }. Adjusting to {new_value_bad_params = }."
            )
            self.value_bad_params = new_value_bad_params

        self.info.n_evals = 0
        self.time_fit_start = time.time()

    def hook_post_fit(self, opt_params: dict):
        self.time_fit_end = time.time()
        self.info.time_taken = self.time_fit_end - self.time_fit_start

        if self.info.final_value >= self.value_bad_params:
            logger.warning(
                f"Ending optimization in a `bad` region. Loss is greater or equal to {self.value_bad_params = }"
            )

        logger.info("End fitting")
        logger.info(f"    Final objective function {self.info.final_value}")
        logger.info(f"    Optimal parameters {opt_params}")
        logger.info(f"    Time taken {self.info.time_taken} seconds")

    def fit_nevergrad(
        self, budget: int, optimizer_str: str = "NgIohTuned", **kwargs
    ) -> dict:
        import nevergrad as ng

        self.hook_pre_fit()

        flat_bounds = flatten_dict(self.bounds)
        flat_initial_params = flatten_dict(self.initial_parameters)

        ng_params = ng.p.Dict()

        for k, v in flat_initial_params.items():
            # If `k` is in bounds, fetch the lower and upper bound
            # It `k` is not in bounds just put lower=None and upper=None
            lower, upper = flat_bounds.get(k, (None, None))
            ng_params[k] = ng.p.Scalar(init=v, lower=lower, upper=upper)

        instru = ng.p.Instrumentation(ng_params)

        try:
            OptimizerCls = ng.optimizers.registry[optimizer_str]
        except KeyError as e:
            e.add_note(f"Available solvers: {list(ng.optimizers.registry.keys())}")
            raise e

        optimizer = OptimizerCls(parametrization=instru, budget=budget)

        def f_ng(p):
            params = unflatten_dict(p)
            return self.objective_function(params)

        for i in range(budget):
            if i == 0:
                flat_params = flat_initial_params
                p = optimizer.parametrization.spawn_child()
                p.value = (
                    (flat_params,),
                    {},
                )
                optimizer.tell(p, self.info.initial_value)
            else:
                p = optimizer.ask()
                args, kwargs = p.value
                flat_params = args[0]

                optimizer.tell(p, f_ng(flat_params))

        recommendation = optimizer.provide_recommendation()
        args, kwargs = recommendation.value

        # Our optimal params are the first positional argument
        opt_params = args[0]

        # loss is an optional field in the recommendation so we have to test if it has been written
        if recommendation.loss is not None:
            self.info.final_value = recommendation.loss
        else:  # otherwise we compute the optimal loss
            self.info.final_value = self.objective_function(opt_params)

        opt_params = unflatten_dict(opt_params)

        self.hook_post_fit(opt_params)

        return opt_params

    def fit_scipy(self, **kwargs) -> dict:
        """
        Optimize parameters using SciPy's minimize function.

        Parameters
        ----------
        initial_parameters : dict
            Initial guess for each parameter, as a mapping from name to value.
        **kwargs
            Additional keyword arguments passed directly to scipy.optimize.minimize.

        Returns
        -------
        dict
            Dictionary of optimized parameter values.

        Warnings
        --------
        If the optimizer does not converge, a warning is logged.

        Example
        -------
        >>> def objective_function(idx: int, params: dict):
        ...     return 2.0 * (params["x"] - 2) ** 2 + 3.0 * (params["y"] + 1) ** 2
        >>> fitter = Fitter(objective_function=objective_function)
        >>> initial_params = dict(x=0.0, y=0.0)
        >>> optimal_params = fitter.fit_scipy(initial_parameters=initial_params)
        >>> print(optimal_params)
        {'x': 2.0, 'y': -1.0}
        """

        from scipy.optimize import minimize

        self.hook_pre_fit()

        # Scipy expects a function with n real-valued parameters f(x)
        # but our objective function takes a dictionary of parameters.
        # Moreover, the dictionary might not be flat but nested

        # Therefore, as a first step, we flatten the bounds and
        # initial parameter dicts
        flat_params = flatten_dict(self.initial_parameters)
        flat_bounds = flatten_dict(self.bounds)

        # We then capture the order of keys in the flattened dictionary
        self._keys = flat_params.keys()

        # The initial value of x and the bounds are derived from that order
        x0 = np.array([flat_params[k] for k in self._keys])
        bounds = np.array([flat_bounds.get(k, (None, None)) for k in self._keys])

        if len(bounds) == 0:
            bounds = None

        # The local objective function first creates a flat dictionary from the `x` array
        # by zipping it with the captured flattened keys and then unflattens the dictionary
        # to pass it to the objective functions
        def f_scipy(x):
            p = unflatten_dict(dict(zip(self._keys, x)))
            return self.objective_function(p)

        # ob = partial(self.ob_func_wrapper, ob_func=f_scipy)
        res = minimize(f_scipy, x0, bounds=bounds, **kwargs)

        if not res.success:
            logger.warning(f"Fit did not converge: {res.message}")

        self.info.final_value = res.fun
        opt_params = dict(zip(self._keys, res.x))

        opt_params = unflatten_dict(opt_params)

        self.hook_post_fit(opt_params)

        return opt_params
