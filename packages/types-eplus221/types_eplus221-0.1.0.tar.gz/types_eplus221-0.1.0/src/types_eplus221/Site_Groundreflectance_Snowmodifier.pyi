from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Groundreflectance_Snowmodifier(EpBunch):
    """Specifies ground reflectance multipliers when snow resident on the ground."""

    Ground_Reflected_Solar_Modifier: Annotated[str, Field(default='1.0')]
    """Value for modifying the "normal" ground reflectance when Snow is on ground"""

    Daylighting_Ground_Reflected_Solar_Modifier: Annotated[str, Field(default='1.0')]
    """Value for modifying the "normal" daylighting ground reflectance when Snow is on ground"""