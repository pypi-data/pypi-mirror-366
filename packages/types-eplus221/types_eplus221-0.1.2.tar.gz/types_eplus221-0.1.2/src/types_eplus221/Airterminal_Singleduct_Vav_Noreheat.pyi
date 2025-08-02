from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airterminal_Singleduct_Vav_Noreheat(EpBunch):
    """Central air system terminal unit, single duct, variable volume, with no reheat coil."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Maximum_Air_Flow_Rate: Annotated[str, Field(default=...)]

    Zone_Minimum_Air_Flow_Input_Method: Annotated[Literal['Constant', 'FixedFlowRate', 'Scheduled'], Field(default='Constant')]
    """Constant = Constant Minimum Air Flow Fraction (a fraction of Maximum Air Flow Rate)"""

    Constant_Minimum_Air_Flow_Fraction: Annotated[float, Field(default=autosize)]
    """This field is used if the field Zone Minimum Air Flow Input Method is Constant"""

    Fixed_Minimum_Air_Flow_Rate: Annotated[float, Field(default=autosize)]
    """This field is used if the field Zone Minimum Air Flow Input Method is FixedFlowRate."""

    Minimum_Air_Flow_Fraction_Schedule_Name: Annotated[str, Field()]
    """This field is used if the field Zone Minimum Air Flow Input Method is Scheduled"""

    Design_Specification_Outdoor_Air_Object_Name: Annotated[str, Field()]
    """When the name of a DesignSpecification:OutdoorAir object is entered, the terminal"""