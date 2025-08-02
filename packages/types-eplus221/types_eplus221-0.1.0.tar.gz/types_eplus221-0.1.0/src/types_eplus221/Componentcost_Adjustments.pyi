from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Componentcost_Adjustments(EpBunch):
    """Used to perform various modifications to the construction costs to arrive at an"""

    Miscellaneous_Cost_Per_Conditioned_Area: Annotated[float, Field()]
    """based on conditioned floor area"""

    Design_And_Engineering_Fees: Annotated[float, Field()]

    Contractor_Fee: Annotated[float, Field()]

    Contingency: Annotated[float, Field()]

    Permits__Bonding_And_Insurance: Annotated[float, Field()]

    Commissioning_Fee: Annotated[float, Field()]

    Regional_Adjustment_Factor: Annotated[float, Field()]
    """for use with average data in line item and Misc cost models"""