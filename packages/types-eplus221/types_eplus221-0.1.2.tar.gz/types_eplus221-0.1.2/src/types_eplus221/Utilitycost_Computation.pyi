from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Utilitycost_Computation(EpBunch):
    """The object lists a series of computations that are used to perform the utility bill"""

    Name: Annotated[str, Field(default=...)]

    Tariff_Name: Annotated[str, Field(default=...)]
    """The name of the UtilityCost:Tariff that is associated with this UtilityCost:Variable."""

    Compute_Step_1: Annotated[str, Field()]
    """Contain a simple language that describes the steps used in the computation process similar to a"""

    Compute_Step_2: Annotated[str, Field()]

    Compute_Step_3: Annotated[str, Field()]

    Compute_Step_4: Annotated[str, Field()]

    Compute_Step_5: Annotated[str, Field()]

    Compute_Step_6: Annotated[str, Field()]

    Compute_Step_7: Annotated[str, Field()]

    Compute_Step_8: Annotated[str, Field()]

    Compute_Step_9: Annotated[str, Field()]

    Compute_Step_10: Annotated[str, Field()]

    Compute_Step_11: Annotated[str, Field()]

    Compute_Step_12: Annotated[str, Field()]

    Compute_Step_13: Annotated[str, Field()]

    Compute_Step_14: Annotated[str, Field()]

    Compute_Step_15: Annotated[str, Field()]

    Compute_Step_16: Annotated[str, Field()]

    Compute_Step_17: Annotated[str, Field()]

    Compute_Step_18: Annotated[str, Field()]

    Compute_Step_19: Annotated[str, Field()]

    Compute_Step_20: Annotated[str, Field()]

    Compute_Step_21: Annotated[str, Field()]

    Compute_Step_22: Annotated[str, Field()]

    Compute_Step_23: Annotated[str, Field()]

    Compute_Step_24: Annotated[str, Field()]

    Compute_Step_25: Annotated[str, Field()]

    Compute_Step_26: Annotated[str, Field()]

    Compute_Step_27: Annotated[str, Field()]

    Compute_Step_28: Annotated[str, Field()]

    Compute_Step_29: Annotated[str, Field()]

    Compute_Step_30: Annotated[str, Field()]