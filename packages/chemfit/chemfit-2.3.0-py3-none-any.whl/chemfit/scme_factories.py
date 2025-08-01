from .scme_setup import (
    setup_calculator,
    check_water_is_in_OHH_order,
    arrange_water_in_OHH_order,
)
from ase import Atoms
from pathlib import Path
from typing import Any


class SCMECalculatorFactory:
    def __init__(
        self,
        default_scme_params: dict,
        path_to_scme_expansions: Path,
        parametrization_key: str,
    ):
        self.default_scme_params = default_scme_params
        self.path_to_scme_expansions = path_to_scme_expansions
        self.parametrization_key = parametrization_key

    def __call__(self, atoms: Atoms) -> Any:
        # Attach a fresh copy of default SCME parameters to this Atoms object
        if not check_water_is_in_OHH_order(atoms=atoms):
            atoms = arrange_water_in_OHH_order(atoms)

        setup_calculator(
            atoms,
            params=self.default_scme_params,
            parametrization_key=self.parametrization_key,
            path_to_scme_expansions=self.path_to_scme_expansions,
        )


class SCMEParameterApplier:
    def __call__(self, atoms: Atoms, params: dict) -> None:
        """
        Assign SCME parameter values to the attached calculator.
        """
        atoms.calc.apply_params(params)
