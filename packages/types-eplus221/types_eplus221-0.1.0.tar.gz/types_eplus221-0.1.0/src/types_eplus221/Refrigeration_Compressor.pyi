from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Refrigeration_Compressor(EpBunch):
    """Refrigeration system compressor. Data is available for many compressors"""

    Name: Annotated[str, Field(default=...)]

    Refrigeration_Compressor_Power_Curve_Name: Annotated[str, Field(default=...)]
    """the input order for the Curve:Bicubic does not"""

    Refrigeration_Compressor_Capacity_Curve_Name: Annotated[str, Field(default=...)]
    """the input order for the Curve:Bicubic does not"""

    Rated_Superheat: Annotated[float, Field()]
    """Use this input field OR the next, not both"""

    Rated_Return_Gas_Temperature: Annotated[float, Field()]
    """Use this input field OR the previous, not both"""

    Rated_Liquid_Temperature: Annotated[float, Field()]
    """Use this input field OR the next, not both"""

    Rated_Subcooling: Annotated[float, Field()]
    """Use this input field OR the previous, not both"""

    End_Use_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""

    Mode_Of_Operation: Annotated[Literal['Subcritical', 'Transcritical'], Field(default='Subcritical')]

    Transcritical_Compressor_Power_Curve_Name: Annotated[str, Field()]

    Transcritical_Compressor_Capacity_Curve_Name: Annotated[str, Field()]