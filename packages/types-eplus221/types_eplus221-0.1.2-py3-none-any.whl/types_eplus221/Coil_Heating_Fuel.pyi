from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Heating_Fuel(EpBunch):
    """Gas or other fuel heating coil. If the coil is located directly in an air loop branch or"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Fuel_Type: Annotated[Literal['Gas', 'NaturalGas', 'Propane', 'Diesel', 'Gasoline', 'FuelOil#1', 'FuelOil#2', 'OtherFuel1', 'OtherFuel2'], Field(default='Gas')]

    Burner_Efficiency: Annotated[str, Field(default='0.8')]

    Nominal_Capacity: Annotated[str, Field()]

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Temperature_Setpoint_Node_Name: Annotated[str, Field()]
    """optional, used if coil is temperature control and not load-base controlled"""

    Parasitic_Electric_Load: Annotated[str, Field()]
    """parasitic electric load associated with the coil operation"""

    Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field()]
    """quadratic curve, PLF = a + b*PLR + c*PLR**2"""

    Parasitic_Fuel_Load: Annotated[str, Field()]
    """parasitic fuel load associated with the coil operation (i.e., standing pilot)"""