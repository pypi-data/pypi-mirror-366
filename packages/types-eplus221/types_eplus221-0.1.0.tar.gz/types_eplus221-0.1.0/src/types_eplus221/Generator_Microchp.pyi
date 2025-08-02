from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Generator_Microchp(EpBunch):
    """Small-scale combined heat and power (micro CHP) electric generator using the model"""

    Name: Annotated[str, Field()]

    Performance_Parameters_Name: Annotated[str, Field()]
    """Enter the name of a Generator:MicroCHP:NonNormalizedParameters object."""

    Zone_Name: Annotated[str, Field()]

    Cooling_Water_Inlet_Node_Name: Annotated[str, Field()]

    Cooling_Water_Outlet_Node_Name: Annotated[str, Field()]

    Air_Inlet_Node_Name: Annotated[str, Field()]

    Air_Outlet_Node_Name: Annotated[str, Field()]

    Generator_Fuel_Supply_Name: Annotated[str, Field()]
    """Enter the name of a Generator:FuelSupply object."""

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""