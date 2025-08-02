from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowmaterial_Gas(EpBunch):
    """Gas material properties that are used in Windows or Glass Doors"""

    Name: Annotated[str, Field(default=...)]

    Gas_Type: Annotated[Literal['Air', 'Argon', 'Krypton', 'Xenon', 'Custom'], Field(default=...)]

    Thickness: Annotated[float, Field(default=..., gt=0.0)]

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