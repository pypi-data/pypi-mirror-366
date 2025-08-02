from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Utilitycost_Variable(EpBunch):
    """Allows for the direct entry of monthly values into a utility tariff variable."""

    Name: Annotated[str, Field(default=...)]

    Tariff_Name: Annotated[str, Field(default=...)]
    """The name of the UtilityCost:Tariff that is associated with this UtilityCost:Variable."""

    Variable_Type: Annotated[Literal['Energy', 'Power', 'Dimensionless', 'Currency'], Field(default='Dimensionless')]

    January_Value: Annotated[str, Field()]

    February_Value: Annotated[str, Field()]

    March_Value: Annotated[str, Field()]

    April_Value: Annotated[str, Field()]

    May_Value: Annotated[str, Field()]

    June_Value: Annotated[str, Field()]

    July_Value: Annotated[str, Field()]

    August_Value: Annotated[str, Field()]

    September_Value: Annotated[str, Field()]

    October_Value: Annotated[str, Field()]

    November_Value: Annotated[str, Field()]

    December_Value: Annotated[str, Field()]