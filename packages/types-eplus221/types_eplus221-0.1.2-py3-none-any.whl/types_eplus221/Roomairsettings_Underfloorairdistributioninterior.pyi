from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roomairsettings_Underfloorairdistributioninterior(EpBunch):
    """This Room Air Model is applicable to interior spaces that are served by an underfloor"""

    Zone_Name: Annotated[str, Field(default=...)]
    """Name of Zone with underfloor air distribution"""

    Number_of_Diffusers: Annotated[float, Field(gt=0.0, default=autocalculate)]
    """Total number of diffusers in this zone"""

    Power_per_Plume: Annotated[float, Field(ge=0.0, default=autocalculate)]

    Design_Effective_Area_of_Diffuser: Annotated[float, Field(gt=0.0, default=Autocalculate)]

    Diffuser_Slot_Angle_from_Vertical: Annotated[float, Field(ge=0.0, le=90., default=Autocalculate)]

    Thermostat_Height: Annotated[float, Field(gt=0.0, default=1.2)]
    """Height of thermostat/temperature control sensor above floor"""

    Comfort_Height: Annotated[float, Field(gt=0.0, default=1.1)]
    """Height at which air temperature is calculated for comfort purposes"""

    Temperature_Difference_Threshold_for_Reporting: Annotated[float, Field(ge=0.0, default=0.4)]
    """Minimum temperature difference between predicted upper and lower layer"""

    Floor_Diffuser_Type: Annotated[Literal['Custom', 'Swirl', 'VariableArea', 'HorizontalSwirl', 'LinearBarGrille'], Field(default='Swirl')]

    Transition_Height: Annotated[float, Field(gt=0.0, default=1.7)]
    """user-specified height above floor of boundary between occupied and upper subzones"""

    Coefficient_A: Annotated[float, Field(default=Autocalculate)]
    """Coefficient A in Formula Kc = A*Gamma**B + C + D*Gamma + E*Gamma**2"""

    Coefficient_B: Annotated[float, Field(default=Autocalculate)]
    """Coefficient B in Formula Kc = A*Gamma**B + C + D*Gamma + E*Gamma**2"""

    Coefficient_C: Annotated[float, Field(default=Autocalculate)]
    """Coefficient C in Formula Kc = A*Gamma**B + C + D*Gamma + E*Gamma**2"""

    Coefficient_D: Annotated[float, Field(default=Autocalculate)]
    """Coefficient D in Formula Kc = A*Gamma**B + C + D*Gamma + E*Gamma**2"""

    Coefficient_E: Annotated[float, Field(default=Autocalculate)]
    """Coefficient E in Formula Kc = A*Gamma**B + C + D*Gamma + E*Gamma**2"""