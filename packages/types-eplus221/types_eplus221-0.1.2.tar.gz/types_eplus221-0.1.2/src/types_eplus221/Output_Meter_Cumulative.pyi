from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Meter_Cumulative(EpBunch):
    """Each Output:Meter:Cumulative command picks meters to be reported cumulatively onto the"""

    Key_Name: Annotated[str, Field(default=...)]
    """Form is EnergyUseType:..., e.g. Electricity:* for all Electricity meters"""

    Reporting_Frequency: Annotated[Literal['Detailed', 'Timestep', 'Hourly', 'Daily', 'Monthly', 'RunPeriod', 'Environment', 'Annual'], Field(default='Hourly')]
    """Timestep refers to the zone Timestep/Number of Timesteps in hour value"""