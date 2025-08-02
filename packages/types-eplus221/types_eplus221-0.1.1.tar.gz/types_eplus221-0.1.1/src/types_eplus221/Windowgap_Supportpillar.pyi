from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowgap_Supportpillar(EpBunch):
    """used to define pillar geometry for support pillars"""

    Name: Annotated[str, Field(default=...)]

    Spacing: Annotated[float, Field(gt=0.0, default=0.04)]

    Radius: Annotated[float, Field(gt=0.0, default=0.0004)]