from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Slab_Matlprops(EpBunch):
    """This object contains the material properties for the materials"""

    Rho__Slab_Material_Density: Annotated[str, Field(default='2300')]
    """Density of Slab Material"""

    Rho__Soil_Density: Annotated[str, Field(default='1200')]
    """Density of Soil Material"""

    Cp__Slab_Cp: Annotated[str, Field(default='650')]
    """Specific Heat of Slab Material"""

    Cp__Soil_Cp: Annotated[str, Field(default='1200')]
    """Specific Heat of Soil Material"""

    Tcon__Slab_K: Annotated[str, Field(default='0.9')]
    """Conductivity of Slab Material"""

    Tcon__Soil_K: Annotated[str, Field(default='1.0')]
    """Conductivity of Soil Material"""