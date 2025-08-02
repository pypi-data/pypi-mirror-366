from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Floor_Detailed(EpBunch):
    """Allows for detailed entry of floor heat transfer surfaces."""

    Name: Annotated[str, Field(default=...)]

    Construction_Name: Annotated[str, Field(default=...)]
    """To be matched with a construction in this input file"""

    Zone_Name: Annotated[str, Field(default=...)]
    """Zone the surface is a part of"""

    Outside_Boundary_Condition: Annotated[Literal['Adiabatic', 'Surface', 'Zone', 'Outdoors', 'Foundation', 'Ground', 'GroundFCfactorMethod', 'OtherSideCoefficients', 'OtherSideConditionsModel', 'GroundSlabPreprocessorAverage', 'GroundSlabPreprocessorCore', 'GroundSlabPreprocessorPerimeter', 'GroundBasementPreprocessorAverageWall', 'GroundBasementPreprocessorAverageFloor', 'GroundBasementPreprocessorUpperWall', 'GroundBasementPreprocessorLowerWall'], Field(default=...)]

    Outside_Boundary_Condition_Object: Annotated[str, Field()]
    """Non-blank only if the field Outside Boundary Condition is Surface,"""

    Sun_Exposure: Annotated[Literal['SunExposed', 'NoSun'], Field(default='SunExposed')]

    Wind_Exposure: Annotated[Literal['WindExposed', 'NoWind'], Field(default='WindExposed')]

    View_Factor_to_Ground: Annotated[float, Field(ge=0.0, le=1.0, default=autocalculate)]
    """From the exterior of the surface"""

    Number_of_Vertices: Annotated[str, Field(default='autocalculate')]
    """shown with 10 vertex coordinates -- extensible object"""

    Vertex_1_Xcoordinate: Annotated[float, Field(default=...)]

    Vertex_1_Ycoordinate: Annotated[float, Field(default=...)]

    Vertex_1_Zcoordinate: Annotated[float, Field(default=...)]

    Vertex_2_Xcoordinate: Annotated[float, Field(default=...)]

    Vertex_2_Ycoordinate: Annotated[float, Field(default=...)]

    Vertex_2_Zcoordinate: Annotated[float, Field(default=...)]

    Vertex_3_Xcoordinate: Annotated[float, Field(default=...)]

    Vertex_3_Ycoordinate: Annotated[float, Field(default=...)]

    Vertex_3_Zcoordinate: Annotated[float, Field(default=...)]

    Vertex_4_Xcoordinate: Annotated[float, Field()]

    Vertex_4_Ycoordinate: Annotated[float, Field()]

    Vertex_4_Zcoordinate: Annotated[float, Field()]

    Vertex_5_Xcoordinate: Annotated[float, Field()]

    Vertex_5_Ycoordinate: Annotated[float, Field()]

    Vertex_5_Zcoordinate: Annotated[float, Field()]

    Vertex_6_Xcoordinate: Annotated[float, Field()]

    Vertex_6_Ycoordinate: Annotated[float, Field()]

    Vertex_6_Zcoordinate: Annotated[float, Field()]

    Vertex_7_Xcoordinate: Annotated[float, Field()]

    Vertex_7_Ycoordinate: Annotated[float, Field()]

    Vertex_7_Zcoordinate: Annotated[float, Field()]

    Vertex_8_Xcoordinate: Annotated[float, Field()]

    Vertex_8_Ycoordinate: Annotated[float, Field()]

    Vertex_8_Zcoordinate: Annotated[float, Field()]

    Vertex_9_Xcoordinate: Annotated[float, Field()]

    Vertex_9_Ycoordinate: Annotated[float, Field()]

    Vertex_9_Zcoordinate: Annotated[float, Field()]

    Vertex_10_Xcoordinate: Annotated[float, Field()]

    Vertex_10_Ycoordinate: Annotated[float, Field()]

    Vertex_10_Zcoordinate: Annotated[float, Field()]