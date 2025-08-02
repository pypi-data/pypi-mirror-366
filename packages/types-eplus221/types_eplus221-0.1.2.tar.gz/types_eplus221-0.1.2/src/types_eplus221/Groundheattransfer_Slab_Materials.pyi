from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Slab_Materials(EpBunch):
    """Object gives an overall description of the slab ground heat transfer model."""

    NMAT_Number_of_materials: Annotated[str, Field(default=...)]
    """This field specifies the number of different materials that will be used in the model."""

    ALBEDO_Surface_Albedo_No_Snow: Annotated[str, Field(default='0.16')]
    """Two fields specify the albedo value of the surface: first for no snow coverage days;"""

    ALBEDO_Surface_Albedo_Snow: Annotated[str, Field(default='0.40')]

    EPSLW_Surface_Emissivity_No_Snow: Annotated[str, Field(default='0.94')]
    """EPSLW (No Snow and Snow) specifies the long wavelength (thermal) emissivity of the ground surface."""

    EPSLW_Surface_Emissivity_Snow: Annotated[str, Field(default='0.86')]

    Z0_Surface_Roughness_No_Snow: Annotated[str, Field(default='.75')]
    """fields Z0 (No Snow and Snow) describe the height at which an experimentally velocity profile goes to zero."""

    Z0_Surface_Roughness_Snow: Annotated[str, Field(default='0.25')]
    """typical value= .05 cm"""

    HIN_Indoor_HConv_Downward_Flow: Annotated[str, Field(default='6.13')]
    """These fields specify the combined convective and radiative heat transfer coefficient between"""

    HIN_Indoor_HConv_Upward: Annotated[str, Field(default='9.26')]
    """typical value= 4-10"""