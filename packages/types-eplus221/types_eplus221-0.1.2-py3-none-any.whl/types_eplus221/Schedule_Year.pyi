from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Schedule_Year(EpBunch):
    """A Schedule:Year contains from 1 to 52 week schedules"""

    Name: Annotated[str, Field(default=...)]

    Schedule_Type_Limits_Name: Annotated[str, Field()]

    ScheduleWeek_Name_1: Annotated[str, Field(default=...)]

    Start_Month_1: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_1: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_1: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_1: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_2: Annotated[str, Field(default=...)]

    Start_Month_2: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_2: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_2: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_2: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_3: Annotated[str, Field(default=...)]

    Start_Month_3: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_3: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_3: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_3: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_4: Annotated[str, Field(default=...)]

    Start_Month_4: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_4: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_4: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_4: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_5: Annotated[str, Field(default=...)]

    Start_Month_5: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_5: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_5: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_5: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_6: Annotated[str, Field(default=...)]

    Start_Month_6: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_6: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_6: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_6: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_7: Annotated[str, Field(default=...)]

    Start_Month_7: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_7: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_7: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_7: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_8: Annotated[str, Field(default=...)]

    Start_Month_8: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_8: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_8: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_8: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_9: Annotated[str, Field(default=...)]

    Start_Month_9: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_9: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_9: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_9: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_10: Annotated[str, Field(default=...)]

    Start_Month_10: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_10: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_10: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_10: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_11: Annotated[str, Field(default=...)]

    Start_Month_11: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_11: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_11: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_11: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_12: Annotated[str, Field(default=...)]

    Start_Month_12: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_12: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_12: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_12: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_13: Annotated[str, Field(default=...)]

    Start_Month_13: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_13: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_13: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_13: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_14: Annotated[str, Field(default=...)]

    Start_Month_14: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_14: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_14: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_14: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_15: Annotated[str, Field(default=...)]

    Start_Month_15: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_15: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_15: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_15: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_16: Annotated[str, Field(default=...)]

    Start_Month_16: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_16: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_16: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_16: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_17: Annotated[str, Field(default=...)]

    Start_Month_17: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_17: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_17: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_17: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_18: Annotated[str, Field(default=...)]

    Start_Month_18: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_18: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_18: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_18: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_19: Annotated[str, Field(default=...)]

    Start_Month_19: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_19: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_19: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_19: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_20: Annotated[str, Field(default=...)]

    Start_Month_20: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_20: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_20: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_20: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_21: Annotated[str, Field(default=...)]

    Start_Month_21: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_21: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_21: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_21: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_22: Annotated[str, Field(default=...)]

    Start_Month_22: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_22: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_22: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_22: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_23: Annotated[str, Field(default=...)]

    Start_Month_23: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_23: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_23: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_23: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_24: Annotated[str, Field(default=...)]

    Start_Month_24: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_24: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_24: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_24: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_25: Annotated[str, Field(default=...)]

    Start_Month_25: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_25: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_25: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_25: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_26: Annotated[str, Field(default=...)]

    Start_Month_26: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_26: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_26: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_26: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_27: Annotated[str, Field(default=...)]

    Start_Month_27: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_27: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_27: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_27: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_28: Annotated[str, Field(default=...)]

    Start_Month_28: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_28: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_28: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_28: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_29: Annotated[str, Field(default=...)]

    Start_Month_29: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_29: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_29: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_29: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_30: Annotated[str, Field(default=...)]

    Start_Month_30: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_30: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_30: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_30: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_31: Annotated[str, Field(default=...)]

    Start_Month_31: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_31: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_31: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_31: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_32: Annotated[str, Field(default=...)]

    Start_Month_32: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_32: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_32: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_32: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_33: Annotated[str, Field(default=...)]

    Start_Month_33: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_33: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_33: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_33: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_34: Annotated[str, Field(default=...)]

    Start_Month_34: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_34: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_34: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_34: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_35: Annotated[str, Field(default=...)]

    Start_Month_35: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_35: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_35: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_35: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_36: Annotated[str, Field(default=...)]

    Start_Month_36: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_36: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_36: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_36: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_37: Annotated[str, Field(default=...)]

    Start_Month_37: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_37: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_37: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_37: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_38: Annotated[str, Field(default=...)]

    Start_Month_38: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_38: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_38: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_38: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_39: Annotated[str, Field(default=...)]

    Start_Month_39: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_39: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_39: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_39: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_40: Annotated[str, Field(default=...)]

    Start_Month_40: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_40: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_40: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_40: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_41: Annotated[str, Field(default=...)]

    Start_Month_41: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_41: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_41: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_41: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_42: Annotated[str, Field(default=...)]

    Start_Month_42: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_42: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_42: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_42: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_43: Annotated[str, Field(default=...)]

    Start_Month_43: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_43: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_43: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_43: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_44: Annotated[str, Field(default=...)]

    Start_Month_44: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_44: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_44: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_44: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_45: Annotated[str, Field(default=...)]

    Start_Month_45: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_45: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_45: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_45: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_46: Annotated[str, Field(default=...)]

    Start_Month_46: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_46: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_46: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_46: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_47: Annotated[str, Field(default=...)]

    Start_Month_47: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_47: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_47: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_47: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_48: Annotated[str, Field(default=...)]

    Start_Month_48: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_48: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_48: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_48: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_49: Annotated[str, Field(default=...)]

    Start_Month_49: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_49: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_49: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_49: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_50: Annotated[str, Field(default=...)]

    Start_Month_50: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_50: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_50: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_50: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_51: Annotated[str, Field(default=...)]

    Start_Month_51: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_51: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_51: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_51: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_52: Annotated[str, Field(default=...)]

    Start_Month_52: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_52: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_52: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_52: Annotated[int, Field(default=..., ge=1, le=31)]

    ScheduleWeek_Name_53: Annotated[str, Field(default=...)]

    Start_Month_53: Annotated[int, Field(default=..., ge=1, le=12)]

    Start_Day_53: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month_53: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_53: Annotated[int, Field(default=..., ge=1, le=31)]