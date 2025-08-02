from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowmaterial_Gasmixture(EpBunch):
    """Gas mixtures that are used in Windows or Glass Doors"""

    Name: Annotated[str, Field(default=...)]

    Thickness: Annotated[float, Field(default=..., gt=0.0)]

    Number_of_Gases_in_Mixture: Annotated[int, Field(default=..., ge=1, le=4)]

    Gas_1_Type: Annotated[Literal['Air', 'Argon', 'Krypton', 'Xenon'], Field(default=...)]

    Gas_1_Fraction: Annotated[float, Field(default=..., gt=0.0, le=1.0)]

    Gas_2_Type: Annotated[Literal['Air', 'Argon', 'Krypton', 'Xenon'], Field(default=...)]

    Gas_2_Fraction: Annotated[float, Field(default=..., gt=0.0, le=1.0)]

    Gas_3_Type: Annotated[Literal['Air', 'Argon', 'Krypton', 'Xenon'], Field()]

    Gas_3_Fraction: Annotated[float, Field(gt=0.0, le=1.0)]

    Gas_4_Type: Annotated[Literal['Air', 'Argon', 'Krypton', 'Xenon'], Field()]

    Gas_4_Fraction: Annotated[float, Field(gt=0.0, le=1.0)]