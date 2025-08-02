from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Slab_Matlprops(EpBunch):
    """This object contains the material properties for the materials"""

    RHO_Slab_Material_density: Annotated[str, Field(default='2300')]
    """Density of Slab Material"""

    RHO_Soil_Density: Annotated[str, Field(default='1200')]
    """Density of Soil Material"""

    CP_Slab_CP: Annotated[str, Field(default='650')]
    """Specific Heat of Slab Material"""

    CP_Soil_CP: Annotated[str, Field(default='1200')]
    """Specific Heat of Soil Material"""

    TCON_Slab_k: Annotated[str, Field(default='0.9')]
    """Conductivity of Slab Material"""

    TCON_Soil_k: Annotated[str, Field(default='1.0')]
    """Conductivity of Soil Material"""