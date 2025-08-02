from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airterminal_Singleduct_Constantvolume_Noreheat(EpBunch):
    """Central air system terminal unit, single duct, constant volume, without reheat coil"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """The air-inlet node name that connects the air splitter to the individual zone air distribution"""

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """This is an air outlet node from the air distribution unit. This node name should be one of the"""

    Maximum_Air_Flow_Rate: Annotated[str, Field(default=...)]

    Design_Specification_Outdoor_Air_Object_Name: Annotated[str, Field()]
    """This field is used to modulate the terminal unit flow rate based on the specified outdoor air"""

    Per_Person_Ventilation_Rate_Mode: Annotated[Literal['CurrentOccupancy', 'DesignOccupancy'], Field(default='CurrentOccupancy')]
    """CurrentOccupancy uses current number of people in the zone which may vary"""