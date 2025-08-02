from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airterminal_Singleduct_Uncontrolled(EpBunch):
    """Central air system terminal unit, single duct, constant volume, no controls other than"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Zone_Supply_Air_Node_Name: Annotated[str, Field(default=...)]

    Maximum_Air_Flow_Rate: Annotated[str, Field(default=...)]

    Design_Specification_Outdoor_Air_Object_Name: Annotated[str, Field()]
    """When the name of a DesignSpecification:OutdoorAir object is entered, the terminal"""

    Per_Person_Ventilation_Rate_Mode: Annotated[Literal['CurrentOccupancy', 'DesignOccupancy'], Field(default='CurrentOccupancy')]
    """CurrentOccupancy models demand controlled ventilation using the current number of people"""

    Design_Specification_Air_Terminal_Sizing_Object_Name: Annotated[str, Field()]
    """This optional field is the name of a DesignSpecification:AirTerminal:Sizing object"""