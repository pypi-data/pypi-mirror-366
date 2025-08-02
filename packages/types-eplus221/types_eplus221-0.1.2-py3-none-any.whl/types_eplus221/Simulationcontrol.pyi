from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Simulationcontrol(EpBunch):
    """Note that the following 3 fields are related to the Sizing:Zone, Sizing:System,"""

    Do_Zone_Sizing_Calculation: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """If Yes, Zone sizing is accomplished from corresponding Sizing:Zone objects"""

    Do_System_Sizing_Calculation: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """If Yes, System sizing is accomplished from corresponding Sizing:System objects"""

    Do_Plant_Sizing_Calculation: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """If Yes, Plant sizing is accomplished from corresponding Sizing:Plant objects"""

    Run_Simulation_for_Sizing_Periods: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """If Yes, SizingPeriod:* objects are executed and results from those may be displayed.."""

    Run_Simulation_for_Weather_File_Run_Periods: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """If Yes, RunPeriod:* objects are executed and results from those may be displayed.."""

    Do_HVAC_Sizing_Simulation_for_Sizing_Periods: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """If Yes, SizingPeriod:* objects are exectuted additional times for advanced sizing."""

    Maximum_Number_of_HVAC_Sizing_Simulation_Passes: Annotated[int, Field(ge=1, default=1)]
    """the entire set of SizingPeriod:* objects may be repeated to fine tune size results"""