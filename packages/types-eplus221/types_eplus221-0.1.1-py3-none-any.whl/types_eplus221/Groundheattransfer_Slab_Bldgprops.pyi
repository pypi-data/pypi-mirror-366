from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Slab_Bldgprops(EpBunch):
    """Object provides information about the building and its operating conditions"""

    Iyrs__Number_Of_Years_To_Iterate: Annotated[str, Field(default='10')]
    """This field specifies the number of years to iterate."""

    Shape__Slab_Shape: Annotated[str, Field()]
    """Use only the value 0 here. Only a rectangular shape is implemented."""

    Hbldg__Building_Height: Annotated[str, Field()]
    """This field supplies the building height. This is used to calculate"""

    Tin1__January_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    Tin2__February_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    Tin3__March_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    Tin4__April_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    Tin5__May_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    Tin6__June_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    Tin7__July_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    Tin8__August_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    Tin9__September_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    Tin10__October_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    Tin11__November_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    Tin12__December_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    Tinamp__Daily_Indoor_Sine_Wave_Variation_Amplitude: Annotated[str, Field(default='0')]
    """This field permits imposing a daily sinusoidal variation"""

    Convtol__Convergence_Tolerance: Annotated[str, Field(default='0.1')]
    """This field specifies the convergence tolerance used to"""