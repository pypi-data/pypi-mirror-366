from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Refrigeration_Subcooler(EpBunch):
    """Two types of subcoolers are modeled by the detailed refrigeration system. The"""

    Name: Annotated[str, Field(default=...)]

    Subcooler_Type: Annotated[Literal['Mechanical', 'LiquidSuction'], Field(default='LiquidSuction')]
    """plan to add ambient subcoolers at future time"""

    Liquid_Suction_Design_Subcooling_Temperature_Difference: Annotated[float, Field()]
    """Applicable only and required for liquid suction heat exchangers"""

    Design_Liquid_Inlet_Temperature: Annotated[float, Field()]
    """design inlet temperature on liquid side"""

    Design_Vapor_Inlet_Temperature: Annotated[float, Field()]
    """design inlet temperature on vapor side"""

    Capacity_Providing_System: Annotated[str, Field()]
    """Name of the Detailed Refrigeration System providing cooling capacity"""

    Outlet_Control_Temperature: Annotated[float, Field()]
    """Control Temperature Out for subcooled liquid"""