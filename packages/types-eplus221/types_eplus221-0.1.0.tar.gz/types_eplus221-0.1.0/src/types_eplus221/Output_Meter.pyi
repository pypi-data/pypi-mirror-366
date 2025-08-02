from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Meter(EpBunch):
    """Each Output:Meter command picks meters to be put onto the standard output file (.eso)"""

    Key_Name: Annotated[str, Field(default=...)]
    """Form is EnergyUseType:..., e.g. Electricity:* for all Electricity meters"""

    Reporting_Frequency: Annotated[Literal['Detailed', 'Timestep', 'Hourly', 'Daily', 'Detailed', 'Monthly', 'RunPeriod', 'Environment', 'Annual'], Field(default='Hourly')]
    """Timestep refers to the zone Timestep/Number of Timesteps in hour value"""