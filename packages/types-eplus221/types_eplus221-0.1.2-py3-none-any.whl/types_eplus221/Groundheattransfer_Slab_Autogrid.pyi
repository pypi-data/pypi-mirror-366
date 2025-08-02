from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Slab_Autogrid(EpBunch):
    """AutoGrid only necessary when EquivalentSlab option not chosen."""

    SLABX_X_dimension_of_the_building_slab: Annotated[str, Field(default=...)]
    """typical values= 6 to 60.0"""

    SLABY_Y_dimension_of_the_building_slab: Annotated[str, Field(default=...)]
    """typical values= 6 to 60.0"""

    SLABDEPTH_Thickness_of_slab_on_grade: Annotated[str, Field(default='0.1')]

    CLEARANCE_Distance_from_edge_of_slab_to_domain_edge: Annotated[str, Field(default='15.0')]

    ZCLEARANCE_Distance_from_bottom_of_slab_to_domain_bottom: Annotated[str, Field(default='15.0')]