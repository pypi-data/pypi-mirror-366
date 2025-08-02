from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Lifecyclecost_Nonrecurringcost(EpBunch):
    """A non-recurring cost happens only once during the study period. For costs that occur"""

    Name: Annotated[str, Field(default=...)]

    Category: Annotated[Literal['Construction', 'Salvage', 'OtherCapital'], Field(default='Construction')]

    Cost: Annotated[float, Field()]
    """Enter the non-recurring cost value. For construction and other capital costs the value"""

    Start_of_Costs: Annotated[Literal['ServicePeriod', 'BasePeriod'], Field(default='ServicePeriod')]
    """Enter when the costs start. The First Year of Cost is based on the number of years past the"""

    Years_from_Start: Annotated[int, Field(ge=0, le=100)]
    """This field and the Months From Start field together represent the time from either the start"""

    Months_from_Start: Annotated[int, Field(ge=0, le=1200)]
    """This field and the Years From Start field together represent the time from either the start"""