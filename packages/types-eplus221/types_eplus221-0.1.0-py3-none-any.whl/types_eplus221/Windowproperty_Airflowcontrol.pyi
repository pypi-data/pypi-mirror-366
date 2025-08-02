from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowproperty_Airflowcontrol(EpBunch):
    """Used to control forced airflow through a gap between glass layers"""

    Name: Annotated[str, Field(default=...)]
    """Name must be that of an exterior window with two or three glass layers."""

    Airflow_Source: Annotated[Literal['IndoorAir', 'OutdoorAir'], Field(default='IndoorAir')]

    Airflow_Destination: Annotated[Literal['IndoorAir', 'OutdoorAir', 'ReturnAir'], Field(default='OutdoorAir')]
    """If ReturnAir is selected, the name of the Return Air Node may be specified below."""

    Maximum_Flow_Rate: Annotated[str, Field(default='0.0')]
    """Above is m3/s per m of glazing width"""

    Airflow_Control_Type: Annotated[Literal['AlwaysOnAtMaximumFlow', 'AlwaysOff', 'ScheduledOnly'], Field(default='AlwaysOnAtMaximumFlow')]
    """ScheduledOnly requires that Airflow Has Multiplier Schedule Name = Yes"""

    Airflow_Is_Scheduled: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """If Yes, then Airflow Multiplier Schedule Name must be specified"""

    Airflow_Multiplier_Schedule_Name: Annotated[str, Field()]
    """Required if Airflow Is Scheduled = Yes."""

    Airflow_Return_Air_Node_Name: Annotated[str, Field()]
    """Name of the return air node for this airflow window if the Airflow Destination is ReturnAir."""