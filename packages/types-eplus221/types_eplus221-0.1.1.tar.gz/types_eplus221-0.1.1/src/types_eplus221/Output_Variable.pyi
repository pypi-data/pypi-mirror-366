from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Variable(EpBunch):
    """each Output:Variable command picks variables to be put onto the standard output file (.eso)"""

    Key_Value: Annotated[str, Field(default='*')]
    """use '*' (without quotes) to apply this variable to all keys"""

    Variable_Name: Annotated[str, Field(default=...)]

    Reporting_Frequency: Annotated[Literal['Detailed', 'Timestep', 'Hourly', 'Daily', 'Monthly', 'RunPeriod', 'Environment', 'Annual'], Field(default='Hourly')]
    """Detailed lists every instance (i.e. HVAC variable timesteps)"""

    Schedule_Name: Annotated[str, Field()]