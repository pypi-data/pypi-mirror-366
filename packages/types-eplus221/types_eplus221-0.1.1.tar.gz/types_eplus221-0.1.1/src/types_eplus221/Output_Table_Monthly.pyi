from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Table_Monthly(EpBunch):
    """Provides a generic method of setting up tables of monthly results. The report"""

    Name: Annotated[str, Field(default=...)]

    Digits_After_Decimal: Annotated[int, Field(ge=0, le=10, default=2)]

    Variable_Or_Meter_1_Name: Annotated[str, Field()]
    """The name of an output variable or meter that is available in the RDD file."""

    Aggregation_Type_For_Variable_Or_Meter_1: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """The method of aggregation for the selected variable or meter."""

    Variable_Or_Meter_2_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_2: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_3_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_3: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_4_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_4: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_5_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_5: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_6_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_6: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_7_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_7: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_8_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_8: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_9_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_9: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_10_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_10: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_11_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_11: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_12_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_12: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_13_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_13: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_14_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_14: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_15_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_15: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_16_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_16: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_17_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_17: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_18_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_18: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_19_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_19: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_20_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_20: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_21_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_21: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_22_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_22: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_23_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_23: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_24_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_24: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""

    Variable_Or_Meter_25_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_25: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """See instructions under AggregationType01"""