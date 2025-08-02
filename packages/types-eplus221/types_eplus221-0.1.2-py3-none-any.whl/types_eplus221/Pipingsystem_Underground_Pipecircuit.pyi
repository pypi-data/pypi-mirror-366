from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Pipingsystem_Underground_Pipecircuit(EpBunch):
    """The pipe circuit object in an underground piping system."""

    Name: Annotated[str, Field(default=...)]

    Pipe_Thermal_Conductivity: Annotated[float, Field(default=..., gt=0)]

    Pipe_Density: Annotated[float, Field(default=..., gt=0)]

    Pipe_Specific_Heat: Annotated[float, Field(default=..., gt=0)]

    Pipe_Inner_Diameter: Annotated[float, Field(default=..., gt=0)]

    Pipe_Outer_Diameter: Annotated[float, Field(default=..., gt=0)]

    Design_Flow_Rate: Annotated[float, Field(default=..., gt=0)]

    Circuit_Inlet_Node: Annotated[str, Field(default=...)]

    Circuit_Outlet_Node: Annotated[str, Field(default=...)]

    Convergence_Criterion_for_the_Inner_Radial_Iteration_Loop: Annotated[float, Field(ge=0.000001, le=0.5, default=0.001)]

    Maximum_Iterations_in_the_Inner_Radial_Iteration_Loop: Annotated[int, Field(ge=3, le=10000, default=500)]

    Number_of_Soil_Nodes_in_the_Inner_Radial_Near_Pipe_Mesh_Region: Annotated[int, Field(ge=1, le=15, default=3)]

    Radial_Thickness_of_Inner_Radial_Near_Pipe_Mesh_Region: Annotated[float, Field(default=..., gt=0)]
    """Required because it must be selected by user instead of being"""

    Number_of_Pipe_Segments_Entered_for_this_Pipe_Circuit: Annotated[int, Field(default=..., ge=1)]

    Pipe_Segment_1: Annotated[str, Field(default=...)]
    """Name of a pipe segment to be included in this pipe circuit"""

    Pipe_Segment_2: Annotated[str, Field()]
    """optional"""

    Pipe_Segment_3: Annotated[str, Field()]
    """optional"""

    Pipe_Segment_4: Annotated[str, Field()]
    """optional"""

    Pipe_Segment_5: Annotated[str, Field()]
    """optional"""

    Pipe_Segment_6: Annotated[str, Field()]
    """optional"""