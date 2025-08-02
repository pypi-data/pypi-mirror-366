from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Humidifier_Steam_Gas(EpBunch):
    """Natural gas fired steam humidifier with optional blower fan."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Rated_Capacity: Annotated[float, Field(ge=0.0)]
    """Capacity is m3/s of water at 5.05 C"""

    Rated_Gas_Use_Rate: Annotated[float, Field(ge=0.0)]
    """if auto-sized, the rated gas use rate is calculated from the rated"""

    Thermal_Efficiency: Annotated[float, Field(gt=0.0, le=1.0, default=0.80)]
    """Based on the higher heating value of fuel."""

    Thermal_Efficiency_Modifier_Curve_Name: Annotated[str, Field()]
    """Linear, Quadratic and Cubic efficiency curves are solely a function of PLR."""

    Rated_Fan_Power: Annotated[float, Field(ge=0.0)]
    """The nominal full capacity electric power input to the blower fan in Watts. If no"""

    Auxiliary_Electric_Power: Annotated[float, Field(ge=0.0, default=0.0)]
    """The auxiliary electric power input in watts. This amount of power will be consumed"""

    Air_Inlet_Node_Name: Annotated[str, Field()]

    Air_Outlet_Node_Name: Annotated[str, Field()]

    Water_Storage_Tank_Name: Annotated[str, Field()]

    Inlet_Water_Temperature_Option: Annotated[Literal['FixedInletWaterTemperature', 'VariableInletWaterTemperature'], Field(default='FixedInletWaterTemperature')]
    """The inlet water temperature can be fixed at 20C as it is done for electric steam"""