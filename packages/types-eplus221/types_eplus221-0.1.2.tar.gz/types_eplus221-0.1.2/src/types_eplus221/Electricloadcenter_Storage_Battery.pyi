from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Electricloadcenter_Storage_Battery(EpBunch):
    """Uses the kinetic battery model (KiBaM) to simulate rechargeable battery banks in an"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Zone_Name: Annotated[str, Field()]
    """Enter name of zone to receive electrical storage losses as heat"""

    Radiative_Fraction: Annotated[float, Field(ge=0, le=1.0, default=0)]

    Number_of_Battery_Modules_in_Parallel: Annotated[int, Field(ge=1, default=1)]
    """A module usually consists of several cells."""

    Number_of_Battery_Modules_in_Series: Annotated[int, Field(ge=1, default=1)]
    """A module usually consists of several cells."""

    Maximum_Module_Capacity: Annotated[float, Field(ge=0)]
    """The capacity is for each module."""

    Initial_Fractional_State_of_Charge: Annotated[float, Field(ge=0, le=1.0, default=1.0)]
    """The state of charge is evaluated based on the"""

    Fraction_of_Available_Charge_Capacity: Annotated[float, Field(ge=0, le=1.0)]
    """A model parameter usually derived from test data by curve fitting."""

    Change_Rate_from_Bound_Charge_to_Available_Charge: Annotated[str, Field()]
    """A model parameter usually derived from test data by curve fitting."""

    Fully_Charged_Module_Open_Circuit_Voltage: Annotated[float, Field(ge=0)]
    """The voltage is for each battery module."""

    Fully_Discharged_Module_Open_Circuit_Voltage: Annotated[float, Field(ge=0)]
    """The voltage is for each battery module."""

    Voltage_Change_Curve_Name_for_Charging: Annotated[str, Field()]
    """Determines how the open circuit voltage change with state of charge relative to the fully discharged state."""

    Voltage_Change_Curve_Name_for_Discharging: Annotated[str, Field()]
    """Determines how the open circuit voltage change with state of charge relative to the fully charged state."""

    Module_Internal_Electrical_Resistance: Annotated[float, Field(ge=0)]
    """A model parameter from manufacture or derived from test data."""

    Maximum_Module_Discharging_Current: Annotated[float, Field(ge=0)]
    """The constraint on discharging current is for each battery module."""

    Module_Cutoff_Voltage: Annotated[float, Field(ge=0)]
    """The voltage constraint is for each battery module."""

    Module_Charge_Rate_Limit: Annotated[float, Field(ge=0, default=1.0)]
    """units 1/hr"""

    Battery_Life_Calculation: Annotated[Literal['Yes', 'No'], Field(default='No')]

    Number_of_Cycle_Bins: Annotated[int, Field(ge=5, default=10)]
    """Only required when battery life calculation is activated"""

    Battery_Life_Curve_Name: Annotated[str, Field()]
    """Determines the number of cycles to failure in relation to cycle range."""