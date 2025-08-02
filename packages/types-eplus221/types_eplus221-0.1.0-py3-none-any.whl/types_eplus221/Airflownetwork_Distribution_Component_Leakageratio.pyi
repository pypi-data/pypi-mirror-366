from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Distribution_Component_Leakageratio(EpBunch):
    """This object is used to define supply and return air leaks with respect to the fan's maximum"""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this object."""

    Effective_Leakage_Ratio: Annotated[float, Field(gt=0.0, le=1.0)]
    """Defined as a ratio of leak flow rate to the maximum flow rate."""

    Maximum_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Enter the maximum air flow rate in this air loop."""

    Reference_Pressure_Difference: Annotated[float, Field(default=..., gt=0.0)]
    """Enter the pressure corresponding to the Effective leakage ratio entered above."""

    Air_Mass_Flow_Exponent: Annotated[float, Field(ge=0.5, le=1.0, default=0.65)]
    """Enter the exponent used in the air mass flow equation."""