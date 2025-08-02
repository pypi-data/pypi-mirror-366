from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Slab_Bldgprops(EpBunch):
    """Object provides information about the building and its operating conditions"""

    IYRS_Number_of_years_to_iterate: Annotated[str, Field(default='10')]
    """This field specifies the number of years to iterate."""

    Shape_Slab_shape: Annotated[str, Field()]
    """Use only the value 0 here. Only a rectangular shape is implemented."""

    HBLDG_Building_height: Annotated[str, Field()]
    """This field supplies the building height. This is used to calculate"""

    TIN1_January_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    TIN2_February_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    TIN3_March_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    TIN4_April_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    TIN5_May_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    TIN6_June_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    TIN7_July_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    TIN8_August_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    TIN9_September_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    TIN10_October_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    TIN11_November_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    TIN12_December_Indoor_Average_Temperature_Setpoint: Annotated[str, Field(default='22')]
    """see memo on object for more information"""

    TINAmp_Daily_Indoor_sine_wave_variation_amplitude: Annotated[str, Field(default='0')]
    """This field permits imposing a daily sinusoidal variation"""

    ConvTol_Convergence_Tolerance: Annotated[str, Field(default='0.1')]
    """This field specifies the convergence tolerance used to"""