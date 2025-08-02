from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Construction_Internalsource(EpBunch):
    """Start with outside layer and work your way to the inside Layer"""

    Name: Annotated[str, Field(default=...)]

    Source_Present_After_Layer_Number: Annotated[int, Field(default=..., ge=1)]
    """refers to the list of materials which follows"""

    Temperature_Calculation_Requested_After_Layer_Number: Annotated[int, Field(default=...)]
    """refers to the list of materials which follows"""

    Dimensions_for_the_CTF_Calculation: Annotated[int, Field(default=..., ge=1, le=2)]
    """1 = 1-dimensional calculation, 2 = 2-dimensional calculation"""

    Tube_Spacing: Annotated[float, Field(default=...)]
    """uniform spacing between tubes or resistance wires in direction"""

    Outside_Layer: Annotated[str, Field(default=...)]

    Layer_2: Annotated[str, Field()]

    Layer_3: Annotated[str, Field()]

    Layer_4: Annotated[str, Field()]

    Layer_5: Annotated[str, Field()]

    Layer_6: Annotated[str, Field()]

    Layer_7: Annotated[str, Field()]

    Layer_8: Annotated[str, Field()]

    Layer_9: Annotated[str, Field()]

    Layer_10: Annotated[str, Field()]