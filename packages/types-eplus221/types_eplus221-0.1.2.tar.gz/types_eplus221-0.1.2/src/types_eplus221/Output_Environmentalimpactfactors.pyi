from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Environmentalimpactfactors(EpBunch):
    """This is used to Automatically report the facility meters and turn on the Environmental Impact Report calculations"""

    Reporting_Frequency: Annotated[Literal['Timestep', 'Hourly', 'Daily', 'Monthly', 'RunPeriod', 'Environment', 'Annual'], Field()]
    """Timestep refers to the zone Timestep/Number of Timesteps in hour value"""