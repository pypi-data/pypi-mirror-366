from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Meter_Customdecrement(EpBunch):
    """Used to allow users to combine specific variables and/or meters into"""

    Name: Annotated[str, Field(default=...)]

    Fuel_Type: Annotated[Literal['Electricity', 'NaturalGas', 'PropaneGas', 'FuelOil#1', 'FuelOil#2', 'Coal', 'Diesel', 'Gasoline', 'Water', 'Generic', 'OtherFuel1', 'OtherFuel2'], Field()]

    Source_Meter_Name: Annotated[str, Field(default=...)]

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