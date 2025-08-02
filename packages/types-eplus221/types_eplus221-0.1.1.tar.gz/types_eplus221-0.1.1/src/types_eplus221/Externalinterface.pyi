from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Externalinterface(EpBunch):
    """This object activates the external interface of EnergyPlus. If the object"""

    Name_Of_External_Interface: Annotated[Literal['PtolemyServer', 'FunctionalMockupUnitImport', 'FunctionalMockupUnitExport'], Field(default=...)]
    """Name of External Interface"""