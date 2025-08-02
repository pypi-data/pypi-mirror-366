from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Distribution_Component_Constantpressuredrop(EpBunch):
    """This object defines the characteristics of a constant pressure drop component (e.g. filter)."""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this object."""

    Pressure_Difference_Across_the_Component: Annotated[float, Field(default=..., gt=0.0)]
    """Enter the pressure drop across this component."""