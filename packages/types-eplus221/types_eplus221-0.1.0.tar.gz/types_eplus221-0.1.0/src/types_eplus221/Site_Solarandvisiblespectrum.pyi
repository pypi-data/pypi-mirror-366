from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Solarandvisiblespectrum(EpBunch):
    """If this object is omitted, the default solar and visible spectrum data will be used."""

    Name: Annotated[str, Field(default=...)]

    Spectrum_Data_Method: Annotated[Literal['Default', 'UserDefined'], Field(default='Default')]
    """The method specifies which of the solar and visible spectrum data to use in the calculations."""

    Solar_Spectrum_Data_Object_Name: Annotated[str, Field()]

    Visible_Spectrum_Data_Object_Name: Annotated[str, Field()]