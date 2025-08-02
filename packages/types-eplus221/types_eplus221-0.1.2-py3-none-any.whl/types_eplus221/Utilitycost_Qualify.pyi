from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Utilitycost_Qualify(EpBunch):
    """The qualify object allows only tariffs to be selected based on limits which may apply"""

    Utility_Cost_Qualify_Name: Annotated[str, Field(default=...)]
    """Displayed in the report if the tariff does not qualify"""

    Tariff_Name: Annotated[str, Field(default=...)]
    """The name of the UtilityCost:Tariff that is associated with this UtilityCost:Qualify."""

    Variable_Name: Annotated[str, Field(default=...)]
    """The name of the variable used. For energy and demand the automatically created variables totalEnergy"""

    Qualify_Type: Annotated[Literal['Minimum', 'Maximum'], Field(default='Maximum')]

    Threshold_Value_or_Variable_Name: Annotated[str, Field(default=...)]
    """The minimum or maximum value for the qualify. If the variable has values that are less than this value"""

    Season: Annotated[Literal['Annual', 'Summer', 'Winter', 'Spring', 'Fall'], Field()]
    """If the UtilityCost:Qualify only applies to a season enter the season name. If this field is left blank"""

    Threshold_Test: Annotated[Literal['Count', 'Consecutive'], Field(default='Consecutive')]
    """Uses the number in Number of Months in one of two different ways depending on the Threshold Test. If"""

    Number_of_Months: Annotated[str, Field()]
    """A number from 1 to 12. If no value entered 12 is assumed when the qualify type is minimum and 1 when"""