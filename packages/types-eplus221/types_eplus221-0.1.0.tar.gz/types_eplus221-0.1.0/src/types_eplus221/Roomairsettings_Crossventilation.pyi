from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roomairsettings_Crossventilation(EpBunch):
    """This UCSD Cross Ventilation Room Air Model provides a simple model for heat transfer"""

    Zone_Name: Annotated[str, Field(default=...)]
    """Name of Zone being described. Any existing zone name"""

    Gain_Distribution_Schedule_Name: Annotated[str, Field(default=...)]
    """Distribution of the convective heat gains between the jet and recirculation zones."""

    Airflow_Region_Used_For_Thermal_Comfort_Evaluation: Annotated[Literal['Jet', 'Recirculation'], Field()]
    """Required field whenever thermal comfort is predicted"""