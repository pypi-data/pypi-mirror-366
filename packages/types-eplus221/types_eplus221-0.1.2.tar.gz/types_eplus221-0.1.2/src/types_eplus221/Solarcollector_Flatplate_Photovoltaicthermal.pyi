from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Solarcollector_Flatplate_Photovoltaicthermal(EpBunch):
    """Models hybrid photovoltaic-thermal (PVT) solar collectors that convert incident solar"""

    Name: Annotated[str, Field()]

    Surface_Name: Annotated[str, Field(default=...)]

    PhotovoltaicThermal_Model_Performance_Name: Annotated[str, Field()]

    Photovoltaic_Name: Annotated[str, Field()]
    """Enter the name of a Generator:Photovoltaic object."""

    Thermal_Working_Fluid_Type: Annotated[Literal['Water', 'Air'], Field()]

    Water_Inlet_Node_Name: Annotated[str, Field()]

    Water_Outlet_Node_Name: Annotated[str, Field()]

    Air_Inlet_Node_Name: Annotated[str, Field()]

    Air_Outlet_Node_Name: Annotated[str, Field()]

    Design_Flow_Rate: Annotated[str, Field()]