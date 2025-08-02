from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfacecontaminantsourceandsink_Generic_Boundarylayerdiffusion(EpBunch):
    """Simulate generic contaminant source driven by the boundary layer diffusion controlled model."""

    Name: Annotated[str, Field(default=...)]

    Surface_Name: Annotated[str, Field(default=...)]

    Mass_Transfer_Coefficient: Annotated[float, Field(ge=0.0)]

    Schedule_Name: Annotated[str, Field(default=...)]
    """Value in this schedule should be a fraction (generally 0.0 - 1.0) applied to the"""

    Henry_Adsorption_Constant_Or_Partition_Coefficient: Annotated[float, Field(gt=0.0)]