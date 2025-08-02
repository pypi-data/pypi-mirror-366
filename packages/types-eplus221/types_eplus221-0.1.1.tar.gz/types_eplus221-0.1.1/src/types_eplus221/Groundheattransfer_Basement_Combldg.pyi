from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Combldg(EpBunch):
    """ComBldg contains the monthly average temperatures (C) and possibility of daily variation amplitude"""

    January_Average_Temperature: Annotated[str, Field(default='22')]

    February_Average_Temperature: Annotated[str, Field(default='22')]

    March_Average_Temperature: Annotated[str, Field(default='22')]

    April_Average_Temperature: Annotated[str, Field(default='22')]

    May_Average_Temperature: Annotated[str, Field(default='22')]

    June_Average_Temperature: Annotated[str, Field(default='22')]

    July_Average_Temperature: Annotated[str, Field(default='22')]

    August_Average_Temperature: Annotated[str, Field(default='22')]

    September_Average_Temperature: Annotated[str, Field(default='22')]

    October_Average_Temperature: Annotated[str, Field(default='22')]

    November_Average_Temperature: Annotated[str, Field(default='22')]

    December_Average_Temperature: Annotated[str, Field(default='22')]

    Daily_Variation_Sine_Wave_Amplitude: Annotated[str, Field(default='0')]
    """(Normally zero, just for checking)"""