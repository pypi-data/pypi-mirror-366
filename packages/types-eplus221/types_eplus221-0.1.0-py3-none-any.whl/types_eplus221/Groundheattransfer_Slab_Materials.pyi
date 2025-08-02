from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Slab_Materials(EpBunch):
    """Object gives an overall description of the slab ground heat transfer model."""

    Nmat__Number_Of_Materials: Annotated[str, Field(default=...)]
    """This field specifies the number of different materials that will be used in the model."""

    Albedo__Surface_Albedo__No_Snow: Annotated[str, Field(default='0.16')]
    """Two fields specify the albedo value of the surface: first for no snow coverage days;"""

    Albedo__Surface_Albedo__Snow: Annotated[str, Field(default='0.40')]

    Epslw__Surface_Emissivity__No_Snow: Annotated[str, Field(default='0.94')]
    """EPSLW (No Snow and Snow) specifies the long wavelength (thermal) emissivity of the ground surface."""

    Epslw__Surface_Emissivity__Snow: Annotated[str, Field(default='0.86')]

    Z0__Surface_Roughness__No_Snow: Annotated[str, Field(default='.75')]
    """fields Z0 (No Snow and Snow) describe the height at which an experimentally velocity profile goes to zero."""

    Z0__Surface_Roughness__Snow: Annotated[str, Field(default='0.25')]
    """typical value= .05 cm"""

    Hin__Indoor_Hconv__Downward_Flow: Annotated[str, Field(default='6.13')]
    """These fields specify the combined convective and radiative heat transfer coefficient between"""

    Hin__Indoor_Hconv__Upward: Annotated[str, Field(default='9.26')]
    """typical value= 4-10"""