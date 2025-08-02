from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roofceiling_Detailed(EpBunch):
    """Allows for detailed entry of roof/ceiling heat transfer surfaces."""

    Name: Annotated[str, Field(default=...)]

    Construction_Name: Annotated[str, Field(default=...)]
    """To be matched with a construction in this input file"""

    Zone_Name: Annotated[str, Field(default=...)]
    """Zone the surface is a part of"""

    Outside_Boundary_Condition: Annotated[Literal['Adiabatic', 'Surface', 'Zone', 'Outdoors', 'Ground', 'OtherSideCoefficients', 'OtherSideConditionsModel', 'GroundSlabPreprocessorAverage', 'GroundSlabPreprocessorCore', 'GroundSlabPreprocessorPerimeter', 'GroundBasementPreprocessorAverageWall', 'GroundBasementPreprocessorAverageFloor', 'GroundBasementPreprocessorUpperWall', 'GroundBasementPreprocessorLowerWall'], Field(default=...)]

    Outside_Boundary_Condition_Object: Annotated[str, Field()]
    """Non-blank only if the field Outside Boundary Condition is Surface,"""

    Sun_Exposure: Annotated[Literal['SunExposed', 'NoSun'], Field(default='SunExposed')]

    Wind_Exposure: Annotated[Literal['WindExposed', 'NoWind'], Field(default='WindExposed')]

    View_Factor_To_Ground: Annotated[float, Field(ge=0.0, le=1.0, default=autocalculate)]
    """From the exterior of the surface"""

    Number_Of_Vertices: Annotated[str, Field(default='autocalculate')]
    """shown with 10 vertex coordinates -- extensible object"""

    Vertex_1_X_Coordinate: Annotated[float, Field(default=...)]

    Vertex_1_Y_Coordinate: Annotated[float, Field(default=...)]

    Vertex_1_Z_Coordinate: Annotated[float, Field(default=...)]

    Vertex_2_X_Coordinate: Annotated[float, Field(default=...)]

    Vertex_2_Y_Coordinate: Annotated[float, Field(default=...)]

    Vertex_2_Z_Coordinate: Annotated[float, Field(default=...)]

    Vertex_3_X_Coordinate: Annotated[float, Field(default=...)]

    Vertex_3_Y_Coordinate: Annotated[float, Field(default=...)]

    Vertex_3_Z_Coordinate: Annotated[float, Field(default=...)]

    Vertex_4_X_Coordinate: Annotated[float, Field()]

    Vertex_4_Y_Coordinate: Annotated[float, Field()]

    Vertex_4_Z_Coordinate: Annotated[float, Field()]

    Vertex_5_X_Coordinate: Annotated[float, Field()]

    Vertex_5_Y_Coordinate: Annotated[float, Field()]

    Vertex_5_Z_Coordinate: Annotated[float, Field()]

    Vertex_6_X_Coordinate: Annotated[float, Field()]

    Vertex_6_Y_Coordinate: Annotated[float, Field()]

    Vertex_6_Z_Coordinate: Annotated[float, Field()]

    Vertex_7_X_Coordinate: Annotated[float, Field()]

    Vertex_7_Y_Coordinate: Annotated[float, Field()]

    Vertex_7_Z_Coordinate: Annotated[float, Field()]

    Vertex_8_X_Coordinate: Annotated[float, Field()]

    Vertex_8_Y_Coordinate: Annotated[float, Field()]

    Vertex_8_Z_Coordinate: Annotated[float, Field()]

    Vertex_9_X_Coordinate: Annotated[float, Field()]

    Vertex_9_Y_Coordinate: Annotated[float, Field()]

    Vertex_9_Z_Coordinate: Annotated[float, Field()]

    Vertex_10_X_Coordinate: Annotated[float, Field()]

    Vertex_10_Y_Coordinate: Annotated[float, Field()]

    Vertex_10_Z_Coordinate: Annotated[float, Field()]