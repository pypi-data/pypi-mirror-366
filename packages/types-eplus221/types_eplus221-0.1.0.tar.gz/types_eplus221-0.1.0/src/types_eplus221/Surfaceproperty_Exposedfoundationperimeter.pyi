from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceproperty_Exposedfoundationperimeter(EpBunch):
    """Defines the perimeter of a foundation floor that is exposed to the"""

    Surface_Name: Annotated[str, Field(default=...)]

    Exposed_Perimeter_Calculation_Method: Annotated[Literal['TotalExposedPerimeter', 'ExposedPerimeterFraction', 'BySegment'], Field(default=...)]
    """Choices: TotalExposedPerimeter => total exposed perimeter in meters"""

    Total_Exposed_Perimeter: Annotated[float, Field(ge=0.0)]

    Exposed_Perimeter_Fraction: Annotated[float, Field(ge=0.0, le=1.0)]

    Surface_Segment_1_Exposed: Annotated[Literal['Yes', 'No'], Field()]
    """Surface Segment N is the perimeter between the Nth and (N+1)th"""

    Surface_Segment_2_Exposed: Annotated[Literal['Yes', 'No'], Field()]

    Surface_Segment_3_Exposed: Annotated[Literal['Yes', 'No'], Field()]

    Surface_Segment_4_Exposed: Annotated[Literal['Yes', 'No'], Field()]

    Surface_Segment_5_Exposed: Annotated[Literal['Yes', 'No'], Field()]

    Surface_Segment_6_Exposed: Annotated[Literal['Yes', 'No'], Field()]

    Surface_Segment_7_Exposed: Annotated[Literal['Yes', 'No'], Field()]

    Surface_Segment_8_Exposed: Annotated[Literal['Yes', 'No'], Field()]

    Surface_Segment_9_Exposed: Annotated[Literal['Yes', 'No'], Field()]

    Surface_Segment_10_Exposed: Annotated[Literal['Yes', 'No'], Field()]