from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Daylightfactors(EpBunch):
    """Reports hourly daylight factors for each exterior window for four sky types"""

    Reporting_Days: Annotated[Literal['SizingDays', 'AllShadowCalculationDays'], Field(default=...)]