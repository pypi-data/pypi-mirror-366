from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Lifecyclecost_Recurringcosts(EpBunch):
    """Recurring costs are costs that repeat over time on a regular schedule during the"""

    Name: Annotated[str, Field(default=...)]

    Category: Annotated[Literal['Maintenance', 'Repair', 'Operation', 'Replacement', 'MinorOverhaul', 'MajorOverhaul', 'OtherOperational'], Field(default='Maintenance')]

    Cost: Annotated[float, Field()]
    """Enter the cost in dollars (or the appropriate monetary unit) for the recurring costs. Enter"""

    Start_Of_Costs: Annotated[Literal['ServicePeriod', 'BasePeriod'], Field(default='ServicePeriod')]
    """Enter when the costs start. The First Year of Cost is based on the number of years past the"""

    Years_From_Start: Annotated[int, Field(ge=0, le=100)]
    """This field and the Months From Start field together represent the time from either the start"""

    Months_From_Start: Annotated[int, Field(ge=0, le=1200)]
    """This field and the Years From Start field together represent the time from either the start"""

    Repeat_Period_Years: Annotated[int, Field(ge=0, le=100, default=1)]
    """This field and the Repeat Period Months field indicate how much time elapses between"""

    Repeat_Period_Months: Annotated[int, Field(ge=0, le=1200, default=0)]
    """This field and the Repeat Period Years field indicate how much time elapses between"""

    Annual_Escalation_Rate: Annotated[float, Field(ge=-0.3, le=0.3)]
    """Enter the annual escalation rate as a decimal. For a 1% rate enter the value 0.01."""