from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowthermalmodel_Params(EpBunch):
    """object is used to select which thermal model should be used in tarcog simulations"""

    Name: Annotated[str, Field(default=...)]

    Standard: Annotated[Literal['ISO15099', 'EN673Declared', 'EN673Design'], Field(default='ISO15099')]

    Thermal_Model: Annotated[Literal['ISO15099', 'ScaledCavityWidth', 'ConvectiveScalarModel_NoSDThickness', 'ConvectiveScalarModel_withSDThickness'], Field(default='ISO15099')]

    Sdscalar: Annotated[float, Field(ge=0.0, le=1.0, default=1)]

    Deflection_Model: Annotated[Literal['NoDeflection', 'TemperatureAndPressureInput', 'MeasuredDeflection'], Field(default='NoDeflection')]

    Vacuum_Pressure_Limit: Annotated[float, Field(gt=0, default=13.238)]

    Initial_Temperature: Annotated[float, Field(gt=0, default=25)]
    """This is temperature in time of window fabrication"""

    Initial_Pressure: Annotated[float, Field(gt=0, default=101325)]
    """This is pressure in time of window fabrication"""