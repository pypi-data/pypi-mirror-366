from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Generator_Fuelcell_Inverter(EpBunch):
    """Used to describe the power condition unit subsystem of a fuel cell power generator."""

    Name: Annotated[str, Field(default=...)]

    Inverter_Efficiency_Calculation_Mode: Annotated[Literal['Quadratic', 'Constant'], Field()]

    Inverter_Efficiency: Annotated[str, Field()]

    Efficiency_Function_Of_Dc_Power_Curve_Name: Annotated[str, Field()]