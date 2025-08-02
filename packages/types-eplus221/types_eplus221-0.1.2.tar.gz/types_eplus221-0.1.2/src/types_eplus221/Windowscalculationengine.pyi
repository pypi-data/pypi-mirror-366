from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowscalculationengine(EpBunch):
    """Describes which window model will be used in calculations. Built in windows model will use algorithms that are part of EnergyPlus,"""

    Windows_engine: Annotated[Literal['BuiltInWindowsModel', 'ExternalWindowsModel'], Field(default='BuiltInWindowsModel')]