from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Construction_Windowdatafile(EpBunch):
    """Initiates search of the Window data file for a window called Name."""

    Name: Annotated[str, Field(default=...)]

    File_Name: Annotated[str, Field()]
    """default file name is "Window5DataFile.dat""""