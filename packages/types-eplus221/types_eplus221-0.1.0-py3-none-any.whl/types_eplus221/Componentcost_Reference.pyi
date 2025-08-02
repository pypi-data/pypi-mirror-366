from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Componentcost_Reference(EpBunch):
    """Used to allow comparing the current cost estimate to the results of a previous"""

    Reference_Building_Line_Item_Costs: Annotated[float, Field()]
    """should be comparable to the components in current line item cost model"""

    Reference_Building_Miscellaneous_Cost_Per_Conditioned_Area: Annotated[float, Field()]
    """based on conditioned floor area"""

    Reference_Building_Design_And_Engineering_Fees: Annotated[float, Field()]

    Reference_Building_Contractor_Fee: Annotated[float, Field()]

    Reference_Building_Contingency: Annotated[float, Field()]

    Reference_Building_Permits__Bonding_And_Insurance: Annotated[float, Field()]

    Reference_Building_Commissioning_Fee: Annotated[float, Field()]

    Reference_Building_Regional_Adjustment_Factor: Annotated[float, Field()]
    """for use with average data in line item and Misc cost models"""