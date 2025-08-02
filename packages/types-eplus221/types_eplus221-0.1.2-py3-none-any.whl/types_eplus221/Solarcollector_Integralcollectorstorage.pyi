from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Solarcollector_Integralcollectorstorage(EpBunch):
    """Glazed solar collector with integral storage unit. Thermal and optical properties are"""

    Name: Annotated[str, Field(default=...)]

    IntegralCollectorStorageParameters_Name: Annotated[str, Field(default=...)]

    Surface_Name: Annotated[str, Field(default=...)]

    Bottom_Surface_Boundary_Conditions_Type: Annotated[Literal['OtherSideConditionsModel', 'AmbientAir'], Field(default='AmbientAir')]

    Boundary_Condition_Model_Name: Annotated[str, Field()]
    """Enter the name of a SurfaceProperty:OtherSideConditionsModel"""

    Inlet_Node_Name: Annotated[str, Field(default=...)]

    Outlet_Node_Name: Annotated[str, Field(default=...)]

    Maximum_Flow_Rate: Annotated[float, Field(gt=0)]