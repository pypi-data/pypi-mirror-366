from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowmaterial_Gap_Equivalentlayer(EpBunch):
    """Gas material properties that are used in Windows Equivalent Layer"""

    Name: Annotated[str, Field(default=...)]

    Gas_Type: Annotated[Literal['AIR', 'ARGON', 'KRYPTON', 'XENON', 'CUSTOM'], Field(default=...)]

    Thickness: Annotated[float, Field(default=..., gt=0.0)]

    Gap_Vent_Type: Annotated[Literal['Sealed', 'VentedIndoor', 'VentedOutdoor'], Field(default=...)]
    """Sealed means the gap is enclosed and gas tight, i.e., no venting to indoor or"""

    Conductivity_Coefficient_A: Annotated[float, Field()]
    """Used only if Gas Type = Custom"""

    Conductivity_Coefficient_B: Annotated[float, Field()]
    """Used only if Gas Type = Custom"""

    Conductivity_Coefficient_C: Annotated[float, Field()]
    """Used only if Gas Type = Custom"""

    Viscosity_Coefficient_A: Annotated[float, Field(gt=0.0)]
    """Used only if Gas Type = Custom"""

    Viscosity_Coefficient_B: Annotated[float, Field()]
    """Used only if Gas Type = Custom"""

    Viscosity_Coefficient_C: Annotated[float, Field()]
    """Used only if Gas Type = Custom"""

    Specific_Heat_Coefficient_A: Annotated[float, Field(gt=0.0)]
    """Used only if Gas Type = Custom"""

    Specific_Heat_Coefficient_B: Annotated[float, Field()]
    """Used only if Gas Type = Custom"""

    Specific_Heat_Coefficient_C: Annotated[float, Field()]
    """Used only if Gas Type = Custom"""

    Molecular_Weight: Annotated[float, Field(ge=20.0, le=200.0)]
    """Used only if Gas Type = Custom"""

    Specific_Heat_Ratio: Annotated[float, Field(gt=1.0)]
    """Used only if Gas Type = Custom"""