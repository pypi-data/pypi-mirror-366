from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Sqlite(EpBunch):
    """Output from EnergyPlus can be written to an SQLite format file."""

    Option_Type: Annotated[Literal['Simple', 'SimpleAndTabular'], Field()]