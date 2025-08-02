from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Utilitycost_Charge_Simple(EpBunch):
    """UtilityCost:Charge:Simple is one of the most often used objects for tariff"""

    Utility_Cost_Charge_Simple_Name: Annotated[str, Field(default=...)]
    """Charge Variable Name"""

    Tariff_Name: Annotated[str, Field(default=...)]
    """The name of the UtilityCost:Tariff that is associated with this UtilityCost:Charge:Simple."""

    Source_Variable: Annotated[str, Field(default=...)]
    """The name of the source used by the UtilityCost:Charge:Simple. This is usually the name of the variable"""

    Season: Annotated[Literal['Annual', 'Summer', 'Winter', 'Spring', 'Fall'], Field()]
    """If this is set to annual the calculations are performed for the UtilityCost:Charge:Simple for the entire"""

    Category_Variable_Name: Annotated[Literal['EnergyCharges', 'DemandCharges', 'ServiceCharges', 'Basis', 'Adjustment', 'Surcharge', 'Subtotal', 'Taxes', 'Total', 'NotIncluded'], Field(default=...)]
    """This field shows where the charge should be added. The reason to enter this field appropriately is so"""

    Cost_Per_Unit_Value_Or_Variable_Name: Annotated[str, Field(default=...)]
    """This field contains either a single number or the name of a variable. The number is multiplied with"""