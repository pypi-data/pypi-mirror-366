from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Compliance_Building(EpBunch):
    """Building level inputs related to compliance to building standards, building codes, and beyond energy code programs."""

    Building_Rotation_For_Appendix_G: Annotated[float, Field(default=0.0)]
    """Additional degrees of rotation to be used with the requirement in ASHRAE Standard 90.1 Appendix G"""