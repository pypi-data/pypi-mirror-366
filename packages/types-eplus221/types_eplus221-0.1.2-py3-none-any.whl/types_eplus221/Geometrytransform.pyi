from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Geometrytransform(EpBunch):
    """Provides a simple method of altering the footprint geometry of a model. The intent"""

    Plane_of_Transform: Annotated[Literal['XY'], Field(default='XY')]
    """only current allowed value is "XY""""

    Current_Aspect_Ratio: Annotated[str, Field(default=...)]
    """Aspect ratio of building as described in idf"""

    New_Aspect_Ratio: Annotated[str, Field(default=...)]
    """Aspect ratio to transform to during run"""