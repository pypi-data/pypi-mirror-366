from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Utilitycost_Charge_Block(EpBunch):
    """Used to compute energy and demand charges (or any other charges) that are structured"""

    Utility_Cost_Charge_Block_Name: Annotated[str, Field(default=...)]
    """Charge Variable Name"""

    Tariff_Name: Annotated[str, Field(default=...)]
    """The name of the UtilityCost:Tariff that is associated with this UtilityCost:Charge:Block."""

    Source_Variable: Annotated[str, Field(default=...)]
    """The name of the source used by the UtilityCost:Charge:Block. This is usually the name of the variable"""

    Season: Annotated[Literal['Annual', 'Summer', 'Winter', 'Spring', 'Fall'], Field(default='Annual')]
    """If this is set to annual the calculations are performed for the UtilityCost:Charge:Block for the entire"""

    Category_Variable_Name: Annotated[Literal['EnergyCharges', 'DemandCharges', 'ServiceCharges', 'Basis', 'Adjustment', 'Surcharge', 'Subtotal', 'Taxes', 'Total', 'NotIncluded'], Field(default=...)]
    """This field shows where the charge should be added. The reason to enter this field appropriately is so"""

    Remaining_Into_Variable: Annotated[str, Field()]
    """If the blocks do not use all of the energy or demand from the source some energy and demand remains"""

    Block_Size_Multiplier_Value_Or_Variable_Name: Annotated[str, Field()]
    """The sizes of the blocks are usually used directly but if a value or a variable is entered here the block"""

    Block_Size_1_Value_Or_Variable_Name: Annotated[str, Field()]
    """The size of the block of the charges is entered here. For most rates that use multiple blocks this will"""

    Block_1_Cost_Per_Unit_Value_Or_Variable_Name: Annotated[str, Field()]
    """The cost of the block. This field is unusual for the EnergyPlus syntax because it can be either a number"""

    Block_Size_2_Value_Or_Variable_Name: Annotated[str, Field()]
    """The size of the block of the charges is entered here. For most rates that use multiple blocks this will"""

    Block_2_Cost_Per_Unit_Value_Or_Variable_Name: Annotated[str, Field()]
    """The cost of the block. This field is unusual for the EnergyPlus syntax because it can be either a number"""

    Block_Size_3_Value_Or_Variable_Name: Annotated[str, Field()]
    """The size of the block of the charges is entered here. For most rates that use multiple blocks this will"""

    Block_3_Cost_Per_Unit_Value_Or_Variable_Name: Annotated[str, Field()]
    """The cost of the block. This field is unusual for the EnergyPlus syntax because it can be either a number"""

    Block_Size_4_Value_Or_Variable_Name: Annotated[str, Field()]
    """The size of the block of the charges is entered here. For most rates that use multiple blocks this will"""

    Block_4_Cost_Per_Unit_Value_Or_Variable_Name: Annotated[str, Field()]
    """The cost of the block. This field is unusual for the EnergyPlus syntax because it can be either a number"""

    Block_Size_5_Value_Or_Variable_Name: Annotated[str, Field()]
    """The size of the block of the charges is entered here. For most rates that use multiple blocks this will"""

    Block_5_Cost_Per_Unit_Value_Or_Variable_Name: Annotated[str, Field()]
    """The cost of the block. This field is unusual for the EnergyPlus syntax because it can be either a number"""

    Block_Size_6_Value_Or_Variable_Name: Annotated[str, Field()]
    """The size of the block of the charges is entered here. For most rates that use multiple blocks this will"""

    Block_6_Cost_Per_Unit_Value_Or_Variable_Name: Annotated[str, Field()]
    """The cost of the block. This field is unusual for the EnergyPlus syntax because it can be either a number"""

    Block_Size_7_Value_Or_Variable_Name: Annotated[str, Field()]
    """The size of the block of the charges is entered here. For most rates that use multiple blocks this will"""

    Block_7_Cost_Per_Unit_Value_Or_Variable_Name: Annotated[str, Field()]
    """The cost of the block. This field is unusual for the EnergyPlus syntax because it can be either a number"""

    Block_Size_8_Value_Or_Variable_Name: Annotated[str, Field()]
    """The size of the block of the charges is entered here. For most rates that use multiple blocks this will"""

    Block_8_Cost_Per_Unit_Value_Or_Variable_Name: Annotated[str, Field()]
    """The cost of the block. This field is unusual for the EnergyPlus syntax because it can be either a number"""

    Block_Size_9_Value_Or_Variable_Name: Annotated[str, Field()]
    """The size of the block of the charges is entered here. For most rates that use multiple blocks this will"""

    Block_9_Cost_Per_Unit_Value_Or_Variable_Name: Annotated[str, Field()]
    """The cost of the block. This field is unusual for the EnergyPlus syntax because it can be either a number"""

    Block_Size_10_Value_Or_Variable_Name: Annotated[str, Field()]
    """The size of the block of the charges is entered here. For most rates that use multiple blocks this will"""

    Block_10_Cost_Per_Unit_Value_Or_Variable_Name: Annotated[str, Field()]
    """The cost of the block. This field is unusual for the EnergyPlus syntax because it can be either a number"""

    Block_Size_11_Value_Or_Variable_Name: Annotated[str, Field()]
    """The size of the block of the charges is entered here. For most rates that use multiple blocks this will"""

    Block_11_Cost_Per_Unit_Value_Or_Variable_Name: Annotated[str, Field()]
    """The cost of the block. This field is unusual for the EnergyPlus syntax because it can be either a number"""

    Block_Size_12_Value_Or_Variable_Name: Annotated[str, Field()]
    """The size of the block of the charges is entered here. For most rates that use multiple blocks this will"""

    Block_12_Cost_Per_Unit_Value_Or_Variable_Name: Annotated[str, Field()]
    """The cost of the block. This field is unusual for the EnergyPlus syntax because it can be either a number"""

    Block_Size_13_Value_Or_Variable_Name: Annotated[str, Field()]
    """The size of the block of the charges is entered here. For most rates that use multiple blocks this will"""

    Block_13_Cost_Per_Unit_Value_Or_Variable_Name: Annotated[str, Field()]
    """The cost of the block. This field is unusual for the EnergyPlus syntax because it can be either a number"""

    Block_Size_14_Value_Or_Variable_Name: Annotated[str, Field()]
    """The size of the block of the charges is entered here. For most rates that use multiple blocks this will"""

    Block_14_Cost_Per_Unit_Value_Or_Variable_Name: Annotated[str, Field()]
    """The cost of the block. This field is unusual for the EnergyPlus syntax because it can be either a number"""

    Block_Size_15_Value_Or_Variable_Name: Annotated[str, Field()]
    """The size of the block of the charges is entered here. For most rates that use multiple blocks this will"""

    Block_15_Cost_Per_Unit_Value_Or_Variable_Name: Annotated[str, Field()]
    """The cost of the block. This field is unusual for the EnergyPlus syntax because it can be either a number"""