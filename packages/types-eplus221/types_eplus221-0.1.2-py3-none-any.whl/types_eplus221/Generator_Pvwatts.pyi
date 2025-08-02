from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Generator_Pvwatts(EpBunch):
    """Describes a simple set of inputs for an array of photovoltaic (PV) modules as described"""

    Name: Annotated[str, Field(default=...)]

    PVWatts_Version: Annotated[Literal['5'], Field()]

    DC_System_Capacity: Annotated[float, Field(default=..., gt=0)]
    """Nameplate rated DC system capacity in watts"""

    Module_Type: Annotated[Literal['Standard', 'Premium', 'ThinFilm'], Field(default=...)]

    Array_Type: Annotated[Literal['FixedOpenRack', 'FixedRoofMounted', 'OneAxis', 'OneAxisBacktracking', 'TwoAxis'], Field(default=...)]

    System_Losses: Annotated[float, Field(ge=0, le=1, default=0.14)]

    Array_Geometry_Type: Annotated[Literal['TiltAzimuth', 'Surface'], Field(default='TiltAzimuth')]
    """TiltAzimuth - The tilt and azimuth angles are specified in the next two fields."""

    Tilt_Angle: Annotated[float, Field(ge=0, le=90, default=20)]
    """The tilt angle is the angle from horizontal of the photovoltaic modules in the array."""

    Azimuth_Angle: Annotated[float, Field(ge=0, lt=360, default=180)]
    """For a fixed array, the azimuth angle is the angle clockwise from true north describing"""

    Surface_Name: Annotated[str, Field()]

    Ground_Coverage_Ratio: Annotated[float, Field(ge=0, le=1, default=0.4)]
    """Applies only to arrays with one-axis tracking and is the ratio of module surface area"""