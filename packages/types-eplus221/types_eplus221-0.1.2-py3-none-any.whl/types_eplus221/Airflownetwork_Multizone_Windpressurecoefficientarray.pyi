from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Multizone_Windpressurecoefficientarray(EpBunch):
    """Used only if Wind Pressure Coefficient (WPC) Type = Input in the AirflowNetwork:SimulationControl"""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for the object."""

    Wind_Direction_1: Annotated[float, Field(default=..., ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 1st WPC Array value."""

    Wind_Direction_2: Annotated[float, Field(default=..., ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 2nd WPC Array value."""

    Wind_Direction_3: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 3rd WPC Array value."""

    Wind_Direction_4: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 4th WPC Array value."""

    Wind_Direction_5: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 5th WPC Array value."""

    Wind_Direction_6: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 6th WPC Array value."""

    Wind_Direction_7: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 7th WPC Array value."""

    Wind_Direction_8: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 8th WPC Array value."""

    Wind_Direction_9: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 9th WPC Array value."""

    Wind_Direction_10: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 10th WPC Array value."""

    Wind_Direction_11: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 11th WPC Array value."""

    Wind_Direction_12: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 12th WPC Array value."""

    Wind_Direction_13: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 13th WPC Array value."""

    Wind_Direction_14: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 14th WPC Array value."""

    Wind_Direction_15: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 15th WPC Array value."""

    Wind_Direction_16: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 16th WPC Array value."""

    Wind_Direction_17: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 17th WPC Array value."""

    Wind_Direction_18: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 18th WPC Array value."""

    Wind_Direction_19: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 19th WPC Array value."""

    Wind_Direction_20: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 20th WPC Array value."""

    Wind_Direction_21: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 21st WPC Array value."""

    Wind_Direction_22: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 22nd WPC Array value."""

    Wind_Direction_23: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 23rd WPC Array value."""

    Wind_Direction_24: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 24th WPC Array value."""

    Wind_Direction_25: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 25th WPC Array value."""

    Wind_Direction_26: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 26th WPC Array value."""

    Wind_Direction_27: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 27th WPC Array value."""

    Wind_Direction_28: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 28th WPC Array value."""

    Wind_Direction_29: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 29th WPC Array value."""

    Wind_Direction_30: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 30th WPC Array value."""

    Wind_Direction_31: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 31st WPC Array value."""

    Wind_Direction_32: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 32nd WPC Array value."""

    Wind_Direction_33: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 33rd WPC Array value."""

    Wind_Direction_34: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 34th WPC Array value."""

    Wind_Direction_35: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 35th WPC Array value."""

    Wind_Direction_36: Annotated[float, Field(ge=0.0, le=360.0)]
    """Enter the wind direction corresponding to the 36th WPC Array value."""