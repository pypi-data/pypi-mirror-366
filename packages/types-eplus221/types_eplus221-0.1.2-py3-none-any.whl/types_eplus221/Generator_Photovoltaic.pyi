from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Generator_Photovoltaic(EpBunch):
    """Describes an array of photovoltaic (PV) modules. A series of different PV arrays"""

    Name: Annotated[str, Field(default=...)]

    Surface_Name: Annotated[str, Field(default=...)]

    Photovoltaic_Performance_Object_Type: Annotated[Literal['PhotovoltaicPerformance:Simple', 'PhotovoltaicPerformance:EquivalentOne-Diode', 'PhotovoltaicPerformance:Sandia'], Field()]

    Module_Performance_Name: Annotated[str, Field()]
    """PV array modeling details"""

    Heat_Transfer_Integration_Mode: Annotated[Literal['Decoupled', 'DecoupledUllebergDynamic', 'IntegratedSurfaceOutsideFace', 'IntegratedTranspiredCollector', 'IntegratedExteriorVentedCavity', 'PhotovoltaicThermalSolarCollector'], Field(default='Decoupled')]

    Number_of_Series_Strings_in_Parallel: Annotated[str, Field(default='1')]
    """number of series-wired strings of PV modules that are in parallel"""

    Number_of_Modules_in_Series: Annotated[str, Field(default='1')]
    """Number of PV modules wired in series for each string."""