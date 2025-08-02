from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Combldg(EpBunch):
    """ComBldg contains the monthly average temperatures (C) and possibility of daily variation amplitude"""

    January_average_temperature: Annotated[str, Field(default='22')]

    February_average_temperature: Annotated[str, Field(default='22')]

    March_average_temperature: Annotated[str, Field(default='22')]

    April_average_temperature: Annotated[str, Field(default='22')]

    May_average_temperature: Annotated[str, Field(default='22')]

    June_average_temperature: Annotated[str, Field(default='22')]

    July_average_temperature: Annotated[str, Field(default='22')]

    August_average_temperature: Annotated[str, Field(default='22')]

    September_average_temperature: Annotated[str, Field(default='22')]

    October_average_temperature: Annotated[str, Field(default='22')]

    November_average_temperature: Annotated[str, Field(default='22')]

    December_average_temperature: Annotated[str, Field(default='22')]

    Daily_variation_sine_wave_amplitude: Annotated[str, Field(default='0')]
    """(Normally zero, just for checking)"""