from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Illuminancemap(EpBunch):
    """reference points are given in coordinates specified in the GlobalGeometryRules object"""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Z_Height: Annotated[float, Field(default=0.0)]

    X_Minimum_Coordinate: Annotated[float, Field(default=0.0)]

    X_Maximum_Coordinate: Annotated[float, Field(default=1.0)]

    Number_Of_X_Grid_Points: Annotated[int, Field(ge=1, default=2)]
    """Maximum number of total grid points must be <= 2500 (X*Y)"""

    Y_Minimum_Coordinate: Annotated[float, Field(default=0.0)]

    Y_Maximum_Coordinate: Annotated[float, Field(default=1.0)]

    Number_Of_Y_Grid_Points: Annotated[int, Field(ge=1, default=2)]
    """Maximum number of total grid points must be <= 2500 (X*Y)"""