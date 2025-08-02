from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_Plant_Tower(EpBunch):
    """This object adds a cooling tower to an HVACTemplate:Plant:ChilledWaterLoop or MixedWaterLoop."""

    Name: Annotated[str, Field(default=...)]

    Tower_Type: Annotated[Literal['SingleSpeed', 'TwoSpeed'], Field(default=...)]

    High_Speed_Nominal_Capacity: Annotated[str, Field(default='autosize')]
    """Applicable for tower type SingleSpeed and TwoSpeed"""

    High_Speed_Fan_Power: Annotated[str, Field(default='autosize')]
    """Applicable for tower type SingleSpeed and TwoSpeed"""

    Low_Speed_Nominal_Capacity: Annotated[str, Field(default='autosize')]
    """Applicable only for Tower Type TwoSpeed"""

    Low_Speed_Fan_Power: Annotated[str, Field(default='autosize')]
    """Applicable only for Tower Type TwoSpeed"""

    Free_Convection_Capacity: Annotated[str, Field(default='autosize')]
    """Applicable for Tower Type SingleSpeed and TwoSpeed"""

    Priority: Annotated[str, Field()]
    """Applicable for all Tower Types"""

    Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized capacity and flow rates"""

    Template_Plant_Loop_Type: Annotated[Literal['ChilledWater', 'MixedWater'], Field()]
    """Specifies if this tower serves a template chilled water loop or mixed water loop"""