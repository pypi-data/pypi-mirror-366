from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Multizone_Component_Detailedopening(EpBunch):
    """This object specifies the properties of airflow through windows and doors (window, door and"""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this object."""

    Air_Mass_Flow_Coefficient_When_Opening_is_Closed: Annotated[float, Field(default=..., gt=0)]
    """Defined at 1 Pa per meter of crack length. Enter the coefficient used in the following"""

    Air_Mass_Flow_Exponent_When_Opening_is_Closed: Annotated[float, Field(ge=0.5, le=1.0, default=0.65)]
    """Enter the exponent used in the following equation:"""

    Type_of_Rectangular_Large_Vertical_Opening_LVO: Annotated[Literal['NonPivoted', 'HorizontallyPivoted'], Field(default='NonPivoted')]
    """Select the type of vertical opening: Non-pivoted opening or Horizontally pivoted opening."""

    Extra_Crack_Length_or_Height_of_Pivoting_Axis: Annotated[float, Field(ge=0, default=0)]
    """Extra crack length is used for LVO Non-pivoted type with multiple openable parts."""

    Number_of_Sets_of_Opening_Factor_Data: Annotated[int, Field(default=..., ge=2, le=4)]
    """Enter the number of the following sets of data for opening factor,"""

    Opening_Factor_1: Annotated[float, Field(ge=0, le=0, default=0)]
    """This value must be specified as 0."""

    Discharge_Coefficient_for_Opening_Factor_1: Annotated[float, Field(gt=0, le=1, default=0.001)]
    """The Discharge Coefficient indicates the fractional effectiveness"""

    Width_Factor_for_Opening_Factor_1: Annotated[float, Field(ge=0, le=1, default=0)]
    """The Width Factor is the opening width divided by the window or door width."""

    Height_Factor_for_Opening_Factor_1: Annotated[float, Field(ge=0, le=1, default=0)]
    """The Height Factor is the opening height divided by the window or door height."""

    Start_Height_Factor_for_Opening_Factor_1: Annotated[float, Field(ge=0, le=1, default=0)]
    """The Start Height Factor is the Start Height divided by the window or door height."""

    Opening_Factor_2: Annotated[float, Field(default=..., gt=0, le=1)]
    """If Number of Sets of Opening Factor Data = 2, this value must be 1.0."""

    Discharge_Coefficient_for_Opening_Factor_2: Annotated[float, Field(gt=0, le=1, default=1)]
    """The Discharge Coefficient indicates the fractional effectiveness"""

    Width_Factor_for_Opening_Factor_2: Annotated[float, Field(gt=0, le=1, default=1)]
    """The Width Factor is the opening width divided by the window or door width."""

    Height_Factor_for_Opening_Factor_2: Annotated[float, Field(gt=0, le=1, default=1)]
    """The Height Factor is the opening height divided by the window or door height."""

    Start_Height_Factor_for_Opening_Factor_2: Annotated[float, Field(ge=0, lt=1, default=0)]
    """The Start Height Factor is the Start Height divided by the window or door height."""

    Opening_Factor_3: Annotated[float, Field(ge=0, le=1)]
    """If Number of Sets of Opening Factor Data = 3, this value must be 1.0."""

    Discharge_Coefficient_for_Opening_Factor_3: Annotated[float, Field(ge=0, le=1, default=0)]
    """The Discharge Coefficient indicates the fractional effectiveness"""

    Width_Factor_for_Opening_Factor_3: Annotated[float, Field(ge=0, le=1, default=0)]
    """The Width Factor is the opening width divided by the window or door width."""

    Height_Factor_for_Opening_Factor_3: Annotated[float, Field(ge=0, le=1, default=0)]
    """The Height Factor is the opening height divided by the window or door height."""

    Start_Height_Factor_for_Opening_Factor_3: Annotated[float, Field(ge=0, le=1, default=0)]
    """The Start Height Factor is the Start Height divided by the window or door height."""

    Opening_Factor_4: Annotated[float, Field(ge=0, le=1)]
    """If Number of Sets of Opening Factor Data = 4, this value must be 1.0"""

    Discharge_Coefficient_for_Opening_Factor_4: Annotated[float, Field(ge=0, le=1, default=0)]
    """The Discharge Coefficient indicates the fractional effectiveness"""

    Width_Factor_for_Opening_Factor_4: Annotated[float, Field(ge=0, le=1, default=0)]
    """The Width Factor is the opening width divided by the window or door width."""

    Height_Factor_for_Opening_Factor_4: Annotated[float, Field(ge=0, le=1, default=0)]
    """The Height Factor is the opening height divided by the window or door height."""

    Start_Height_Factor_for_Opening_Factor_4: Annotated[float, Field(ge=0, le=1, default=0)]
    """The Start Height Factor is the Start Height divided by the window or door height."""