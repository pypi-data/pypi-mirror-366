from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Table_Independentvariablelist(EpBunch):
    """A sorted list of independent variables used by one or more Table:Lookup"""

    Name: Annotated[str, Field(default=...)]

    Independent_Variable_1_Name: Annotated[str, Field(default=...)]

    Independent_Variable_2_Name: Annotated[str, Field(default=...)]

    Independent_Variable_3_Name: Annotated[str, Field(default=...)]

    Independent_Variable_4_Name: Annotated[str, Field(default=...)]

    Independent_Variable_5_Name: Annotated[str, Field(default=...)]

    Independent_Variable_6_Name: Annotated[str, Field(default=...)]