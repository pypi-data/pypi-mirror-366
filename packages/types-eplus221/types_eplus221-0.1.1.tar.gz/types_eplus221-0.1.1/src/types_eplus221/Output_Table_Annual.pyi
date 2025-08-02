from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Table_Annual(EpBunch):
    """Provides a generic method of setting up tables of annual results with one row per object."""

    Name: Annotated[str, Field(default=...)]

    Filter: Annotated[str, Field()]
    """An optional text string that is compared to the names of the objects referenced by the"""

    Schedule_Name: Annotated[str, Field()]
    """Optional schedule name. If left blank, aggregation is performed for all hours simulated. If"""

    Variable_Or_Meter_Or_Ems_Variable_Or_Field_1_Name: Annotated[str, Field()]
    """contain the name of a variable (see Output:Variable and eplusout.rdd), meter (see Output:Meter"""

    Aggregation_Type_For_Variable_Or_Meter_1: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'HourInTenBinsMinToMax', 'HourInTenBinsZeroToMax', 'HourInTenBinsMinToZero', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]
    """The method of aggregation for the selected variable or meter."""

    Digits_After_Decimal_1: Annotated[int, Field(ge=0, le=10, default=2)]

    Variable_Or_Meter_Or_Ems_Variable_Or_Field_2_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_2: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'HourInTenBinsMinToMax', 'HourInTenBinsZeroToMax', 'HourInTenBinsMinToZero', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]

    Digits_After_Decimal_2: Annotated[int, Field(ge=0, le=10, default=2)]

    Variable_Or_Meter_Or_Ems_Variable_Or_Field_3_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_3: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'HourInTenBinsMinToMax', 'HourInTenBinsZeroToMax', 'HourInTenBinsMinToZero', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]

    Digits_After_Decimal_3: Annotated[int, Field(ge=0, le=10, default=2)]

    Variable_Or_Meter_Or_Ems_Variable_Or_Field_4_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_4: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'HourInTenBinsMinToMax', 'HourInTenBinsZeroToMax', 'HourInTenBinsMinToZero', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]

    Digits_After_Decimal_4: Annotated[int, Field(ge=0, le=10, default=2)]

    Variable_Or_Meter_Or_Ems_Variable_Or_Field_5_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_5: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'HourInTenBinsMinToMax', 'HourInTenBinsZeroToMax', 'HourInTenBinsMinToZero', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]

    Digits_After_Decimal_5: Annotated[int, Field(ge=0, le=10, default=2)]

    Variable_Or_Meter_Or_Ems_Variable_Or_Field_6_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_6: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'HourInTenBinsMinToMax', 'HourInTenBinsZeroToMax', 'HourInTenBinsMinToZero', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]

    Digits_After_Decimal_6: Annotated[int, Field(ge=0, le=10, default=2)]

    Variable_Or_Meter_Or_Ems_Variable_Or_Field_7_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_7: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'HourInTenBinsMinToMax', 'HourInTenBinsZeroToMax', 'HourInTenBinsMinToZero', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]

    Digits_After_Decimal_7: Annotated[int, Field(ge=0, le=10, default=2)]

    Variable_Or_Meter_Or_Ems_Variable_Or_Field_8_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_8: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'HourInTenBinsMinToMax', 'HourInTenBinsZeroToMax', 'HourInTenBinsMinToZero', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]

    Digits_After_Decimal_8: Annotated[int, Field(ge=0, le=10, default=2)]

    Variable_Or_Meter_Or_Ems_Variable_Or_Field_9_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_9: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'HourInTenBinsMinToMax', 'HourInTenBinsZeroToMax', 'HourInTenBinsMinToZero', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]

    Digits_After_Decimal_9: Annotated[int, Field(ge=0, le=10, default=2)]

    Variable_Or_Meter_Or_Ems_Variable_Or_Field_10_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_10: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'HourInTenBinsMinToMax', 'HourInTenBinsZeroToMax', 'HourInTenBinsMinToZero', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]

    Digits_After_Decimal_10: Annotated[int, Field(ge=0, le=10, default=2)]

    Variable_Or_Meter_Or_Ems_Variable_Or_Field_11_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_11: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'HourInTenBinsMinToMax', 'HourInTenBinsZeroToMax', 'HourInTenBinsMinToZero', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]

    Digits_After_Decimal_11: Annotated[int, Field(ge=0, le=10, default=2)]

    Variable_Or_Meter_Or_Ems_Variable_Or_Field_12_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_12: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'HourInTenBinsMinToMax', 'HourInTenBinsZeroToMax', 'HourInTenBinsMinToZero', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]

    Digits_After_Decimal_12: Annotated[int, Field(ge=0, le=10, default=2)]

    Variable_Or_Meter_Or_Ems_Variable_Or_Field_13_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_13: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'HourInTenBinsMinToMax', 'HourInTenBinsZeroToMax', 'HourInTenBinsMinToZero', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]

    Digits_After_Decimal_13: Annotated[int, Field(ge=0, le=10, default=2)]

    Variable_Or_Meter_Or_Ems_Variable_Or_Field_14_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_14: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'HourInTenBinsMinToMax', 'HourInTenBinsZeroToMax', 'HourInTenBinsMinToZero', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]

    Digits_After_Decimal_14: Annotated[int, Field(ge=0, le=10, default=2)]

    Variable_Or_Meter_Or_Ems_Variable_Or_Field_15_Name: Annotated[str, Field()]

    Aggregation_Type_For_Variable_Or_Meter_15: Annotated[Literal['SumOrAverage', 'Maximum', 'Minimum', 'ValueWhenMaximumOrMinimum', 'HoursNonZero', 'HoursZero', 'HoursPositive', 'HoursNonPositive', 'HoursNegative', 'HoursNonNegative', 'HourInTenBinsMinToMax', 'HourInTenBinsZeroToMax', 'HourInTenBinsMinToZero', 'SumOrAverageDuringHoursShown', 'MaximumDuringHoursShown', 'MinimumDuringHoursShown'], Field()]

    Digits_After_Decimal_15: Annotated[int, Field(ge=0, le=10, default=2)]