from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roomairsettings_Underfloorairdistributionexterior(EpBunch):
    """Applicable to exterior spaces that are served by an underfloor air distribution system."""

    Zone_Name: Annotated[str, Field(default=...)]
    """Name of Zone being described. Any existing zone name"""

    Number_of_Diffusers_per_Zone: Annotated[float, Field(gt=0.0, default=Autocalculate)]

    Power_per_Plume: Annotated[float, Field(ge=0.0, default=autocalculate)]

    Design_Effective_Area_of_Diffuser: Annotated[float, Field(gt=0.0, default=Autocalculate)]

    Diffuser_Slot_Angle_from_Vertical: Annotated[float, Field(ge=0.0, le=90., default=autocalculate)]

    Thermostat_Height: Annotated[float, Field(gt=0.0, default=1.2)]
    """Height of thermostat/temperature control sensor above floor"""

    Comfort_Height: Annotated[float, Field(gt=0.0, default=1.1)]
    """Height at which Air temperature is calculated for comfort purposes"""

    Temperature_Difference_Threshold_for_Reporting: Annotated[float, Field(ge=0.0, default=0.4)]
    """Minimum temperature difference between upper and lower layer"""

    Floor_Diffuser_Type: Annotated[Literal['Custom', 'Swirl', 'VariableArea', 'HorizontalSwirl', 'LinearBarGrille'], Field(default='Swirl')]

    Transition_Height: Annotated[float, Field(gt=0.0, default=1.7)]
    """User-specified height above floor of boundary between occupied and upper subzones"""

    Coefficient_A_in_formula_Kc__AGammaB__C__DGamma__EGamma2: Annotated[float, Field(default=Autocalculate)]
    """Kc is the fraction of the total zone load attributable to the lower subzone"""

    Coefficient_B_in_formula_Kc__AGammaB__C__DGamma__EGamma2: Annotated[float, Field(default=Autocalculate)]
    """Kc is the fraction of the total zone load attributable to the lower subzone"""

    Coefficient_C_in_formula_Kc__AGammaB__C__DGamma__EGamma2: Annotated[float, Field(default=Autocalculate)]
    """Kc is the fraction of the total zone load attributable to the lower subzone"""

    Coefficient_D_in_formula_Kc__AGammaB__C__DGamma__EGamma2: Annotated[float, Field(default=Autocalculate)]
    """Kc is the fraction of the total zone load attributable to the lower subzone"""

    Coefficient_E_in_formula_Kc__AGammaB__C__DGamma__EGamma2: Annotated[float, Field(default=Autocalculate)]
    """Kc is the fraction of the total zone load attributable to the lower subzone"""