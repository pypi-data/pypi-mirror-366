from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roomairsettings_Underfloorairdistributionexterior(EpBunch):
    """Applicable to exterior spaces that are served by an underfloor air distribution system."""

    Zone_Name: Annotated[str, Field(default=...)]
    """Name of Zone being described. Any existing zone name"""

    Number_Of_Diffusers_Per_Zone: Annotated[float, Field(gt=0.0, default=Autocalculate)]

    Power_Per_Plume: Annotated[float, Field(ge=0.0, default=autocalculate)]

    Design_Effective_Area_Of_Diffuser: Annotated[float, Field(gt=0.0, default=Autocalculate)]

    Diffuser_Slot_Angle_From_Vertical: Annotated[float, Field(ge=0.0, le=90., default=autocalculate)]

    Thermostat_Height: Annotated[float, Field(gt=0.0, default=1.2)]
    """Height of thermostat/temperature control sensor above floor"""

    Comfort_Height: Annotated[float, Field(gt=0.0, default=1.1)]
    """Height at which Air temperature is calculated for comfort purposes"""

    Temperature_Difference_Threshold_For_Reporting: Annotated[float, Field(ge=0.0, default=0.4)]
    """Minimum temperature difference between upper and lower layer"""

    Floor_Diffuser_Type: Annotated[Literal['Custom', 'Swirl', 'VariableArea', 'HorizontalSwirl', 'LinearBarGrille'], Field(default='Swirl')]

    Transition_Height: Annotated[float, Field(gt=0.0, default=1.7)]
    """User-specified height above floor of boundary between occupied and upper subzones"""

    Coefficient_A_In_Formula_Kc___A_Gamma__B___C___D_Gamma___E_Gamma__2: Annotated[float, Field(default=Autocalculate)]
    """Kc is the fraction of the total zone load attributable to the lower subzone"""

    Coefficient_B_In_Formula_Kc___A_Gamma__B___C___D_Gamma___E_Gamma__2: Annotated[float, Field(default=Autocalculate)]
    """Kc is the fraction of the total zone load attributable to the lower subzone"""

    Coefficient_C_In_Formula_Kc___A_Gamma__B___C___D_Gamma___E_Gamma__2: Annotated[float, Field(default=Autocalculate)]
    """Kc is the fraction of the total zone load attributable to the lower subzone"""

    Coefficient_D_In_Formula_Kc___A_Gamma__B___C___D_Gamma___E_Gamma__2: Annotated[float, Field(default=Autocalculate)]
    """Kc is the fraction of the total zone load attributable to the lower subzone"""

    Coefficient_E_In_Formula_Kc___A_Gamma__B___C___D_Gamma___E_Gamma__2: Annotated[float, Field(default=Autocalculate)]
    """Kc is the fraction of the total zone load attributable to the lower subzone"""