from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Schedule_File_Shading(EpBunch):
    """A Schedule:File:Shading points to a CSV file that has 8760-8784"""

    File_Name: Annotated[str, Field(default=...)]
    """The name of the file that writes all shading data."""