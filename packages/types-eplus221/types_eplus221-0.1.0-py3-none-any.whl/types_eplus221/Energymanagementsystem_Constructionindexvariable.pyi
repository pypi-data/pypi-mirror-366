from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Energymanagementsystem_Constructionindexvariable(EpBunch):
    """Declares EMS variable that identifies a construction"""

    Name: Annotated[str, Field(default=...)]
    """This name becomes a variable for use in Erl programs"""

    Construction_Object_Name: Annotated[str, Field(default=...)]