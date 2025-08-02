from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Material_Airgap(EpBunch):
    """Air Space in Opaque Construction"""

    Name: Annotated[str, Field(default=...)]

    Thermal_Resistance: Annotated[float, Field(default=..., gt=0)]