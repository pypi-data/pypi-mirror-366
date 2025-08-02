from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Meter_Custom(EpBunch):
    """Used to allow users to combine specific variables and/or meters into"""

    Name: Annotated[str, Field(default=...)]

    Fuel_Type: Annotated[Literal['Electricity', 'NaturalGas', 'PropaneGas', 'FuelOil#1', 'FuelOil#2', 'Coal', 'Diesel', 'Gasoline', 'Water', 'Generic', 'OtherFuel1', 'OtherFuel2'], Field()]

    Key_Name_1: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_1: Annotated[str, Field()]

    Key_Name_2: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_2: Annotated[str, Field()]

    Key_Name_3: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_3: Annotated[str, Field()]

    Key_Name_4: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_4: Annotated[str, Field()]

    Key_Name_5: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_5: Annotated[str, Field()]

    Key_Name_6: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_6: Annotated[str, Field()]

    Key_Name_7: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_7: Annotated[str, Field()]

    Key_Name_8: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_8: Annotated[str, Field()]

    Key_Name_9: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_9: Annotated[str, Field()]

    Key_Name_10: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_10: Annotated[str, Field()]

    Key_Name_11: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_11: Annotated[str, Field()]

    Key_Name_12: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_12: Annotated[str, Field()]

    Key_Name_13: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_13: Annotated[str, Field()]

    Key_Name_14: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_14: Annotated[str, Field()]

    Key_Name_15: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_15: Annotated[str, Field()]

    Key_Name_16: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_16: Annotated[str, Field()]

    Key_Name_17: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_17: Annotated[str, Field()]

    Key_Name_18: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_18: Annotated[str, Field()]

    Key_Name_19: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_19: Annotated[str, Field()]

    Key_Name_20: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_20: Annotated[str, Field()]

    Key_Name_21: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_21: Annotated[str, Field()]

    Key_Name_22: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_22: Annotated[str, Field()]

    Key_Name_23: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_23: Annotated[str, Field()]

    Key_Name_24: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_24: Annotated[str, Field()]

    Key_Name_25: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_25: Annotated[str, Field()]

    Key_Name_26: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_26: Annotated[str, Field()]

    Key_Name_27: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_27: Annotated[str, Field()]

    Key_Name_28: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_28: Annotated[str, Field()]

    Key_Name_29: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_29: Annotated[str, Field()]

    Key_Name_30: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_30: Annotated[str, Field()]

    Key_Name_31: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_31: Annotated[str, Field()]

    Key_Name_32: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_32: Annotated[str, Field()]

    Key_Name_33: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_33: Annotated[str, Field()]

    Key_Name_34: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_34: Annotated[str, Field()]

    Key_Name_35: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_35: Annotated[str, Field()]

    Key_Name_36: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_36: Annotated[str, Field()]

    Key_Name_37: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_37: Annotated[str, Field()]

    Key_Name_38: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_38: Annotated[str, Field()]

    Key_Name_39: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_39: Annotated[str, Field()]

    Key_Name_40: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_40: Annotated[str, Field()]

    Key_Name_41: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_41: Annotated[str, Field()]

    Key_Name_42: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_42: Annotated[str, Field()]

    Key_Name_43: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_43: Annotated[str, Field()]

    Key_Name_44: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_44: Annotated[str, Field()]

    Key_Name_45: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_45: Annotated[str, Field()]

    Key_Name_46: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_46: Annotated[str, Field()]

    Key_Name_47: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_47: Annotated[str, Field()]

    Key_Name_48: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_48: Annotated[str, Field()]

    Key_Name_49: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_49: Annotated[str, Field()]

    Key_Name_50: Annotated[str, Field()]

    Output_Variable_or_Meter_Name_50: Annotated[str, Field()]