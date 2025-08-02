from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Utilitycost_Ratchet(EpBunch):
    """Allows the modeling of tariffs that include some type of seasonal ratcheting."""

    Name: Annotated[str, Field(default=...)]
    """Ratchet Variable Name"""

    Tariff_Name: Annotated[str, Field(default=...)]
    """The name of the UtilityCost:Tariff that is associated with this UtilityCost:Ratchet."""

    Baseline_Source_Variable: Annotated[str, Field(default=...)]
    """When the ratcheted value exceeds the baseline value for a month the ratcheted value is used but when the"""

    Adjustment_Source_Variable: Annotated[str, Field(default=...)]
    """The variable that the ratchet is calculated from. It is often but not always the same as the baseline"""

    Season_From: Annotated[Literal['Annual', 'Summer', 'Winter', 'Spring', 'Fall', 'Monthly'], Field()]
    """The name of the season that is being examined. The maximum value for all of the months in the named"""

    Season_To: Annotated[Literal['Annual', 'Summer', 'Winter', 'Spring', 'Fall'], Field()]
    """The name of the season when the ratchet would be calculated. This is most commonly Winter. The ratchet"""

    Multiplier_Value_Or_Variable_Name: Annotated[str, Field()]
    """Often the ratchet has a clause such as "the current month demand or 90% of the summer month demand". For"""

    Offset_Value_Or_Variable_Name: Annotated[str, Field()]
    """A less common strategy is to say that the ratchet must be all demand greater than a value in this case"""