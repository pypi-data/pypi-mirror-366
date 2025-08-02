from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Generator_Fuelcell_Electricalstorage(EpBunch):
    """Used to describe the electrical storage subsystem for a fuel cell power generator."""

    Name: Annotated[str, Field(default=...)]

    Choice_of_Model: Annotated[Literal['SimpleEfficiencyWithConstraints'], Field()]

    Nominal_Charging_Energetic_Efficiency: Annotated[str, Field()]

    Nominal_Discharging_Energetic_Efficiency: Annotated[str, Field()]

    Simple_Maximum_Capacity: Annotated[str, Field()]

    Simple_Maximum_Power_Draw: Annotated[str, Field()]

    Simple_Maximum_Power_Store: Annotated[str, Field()]

    Initial_Charge_State: Annotated[str, Field()]