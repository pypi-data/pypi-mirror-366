from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Meter_Meterfileonly(EpBunch):
    """Each Output:Meter:MeterFileOnly command picks meters to be put only onto meter file (.mtr)."""

    Key_Name: Annotated[str, Field(default=...)]
    """Form is EnergyUseType:..., e.g. Electricity:* for all Electricity meters"""

    Reporting_Frequency: Annotated[Literal['Detailed', 'Timestep', 'Hourly', 'Daily', 'Monthly', 'RunPeriod', 'Environment', 'Annual'], Field(default='Hourly')]
    """Timestep refers to the zone Timestep/Number of Timesteps in hour value"""