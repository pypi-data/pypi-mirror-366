from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Controller_Mechanicalventilation(EpBunch):
    """This object is used in conjunction with Controller:OutdoorAir to specify outdoor"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """If this field is blank, the controller uses the values from the associated Controller:OutdoorAir."""

    Demand_Controlled_Ventilation: Annotated[Literal['Yes', 'No'], Field(default='No')]

    System_Outdoor_Air_Method: Annotated[Literal['ZoneSum', 'VentilationRateProcedure', 'IndoorAirQualityProcedure', 'ProportionalControlBasedOnDesignOccupancy', 'ProportionalControlBasedonOccupancySchedule', 'IndoorAirQualityProcedureGenericContaminant', 'IndoorAirQualityProcedureCombined', 'ProportionalControlBasedOnDesignOARate'], Field(default='VentilationRateProcedure')]

    Zone_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(gt=0.0, default=1.0)]

    Zone_1_Name: Annotated[str, Field(default=...)]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_1: Annotated[str, Field()]
    """If left blank, the name will be taken from the Sizing:Zone object for this zone."""

    Design_Specification_Zone_Air_Distribution_Object_Name_1: Annotated[str, Field()]
    """If left blank, the name will be taken from the Sizing:Zone object for this zone."""

    Zone_2_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_2: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_2: Annotated[str, Field()]

    Zone_3_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_3: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_3: Annotated[str, Field()]

    Zone_4_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_4: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_4: Annotated[str, Field()]

    Zone_5_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_5: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_5: Annotated[str, Field()]

    Zone_6_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_6: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_6: Annotated[str, Field()]

    Zone_7_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_7: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_7: Annotated[str, Field()]

    Zone_8_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_8: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_8: Annotated[str, Field()]

    Zone_9_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_9: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_9: Annotated[str, Field()]

    Zone_10_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_10: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_10: Annotated[str, Field()]

    Zone_11_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_11: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_11: Annotated[str, Field()]

    Zone_12_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_12: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_12: Annotated[str, Field()]

    Zone_13_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_13: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_13: Annotated[str, Field()]

    Zone_14_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_14: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_14: Annotated[str, Field()]

    Zone_15_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_15: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_15: Annotated[str, Field()]

    Zone_16_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_16: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_16: Annotated[str, Field()]

    Zone_17_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_17: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_17: Annotated[str, Field()]

    Zone_18_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_18: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_18: Annotated[str, Field()]

    Zone_19_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_19: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_19: Annotated[str, Field()]

    Zone_20_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_20: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_20: Annotated[str, Field()]

    Zone_21_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_21: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_21: Annotated[str, Field()]

    Zone_22_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_22: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_22: Annotated[str, Field()]

    Zone_23_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_23: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_23: Annotated[str, Field()]

    Zone_24_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_24: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_24: Annotated[str, Field()]

    Zone_25_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_25: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_25: Annotated[str, Field()]

    Zone_26_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_26: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_26: Annotated[str, Field()]

    Zone_27_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_27: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_27: Annotated[str, Field()]

    Zone_28_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_28: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_28: Annotated[str, Field()]

    Zone_29_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_29: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_29: Annotated[str, Field()]

    Zone_30_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_30: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_30: Annotated[str, Field()]

    Zone_31_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_31: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_31: Annotated[str, Field()]

    Zone_32_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_32: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_32: Annotated[str, Field()]

    Zone_33_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_33: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_33: Annotated[str, Field()]

    Zone_34_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_34: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_34: Annotated[str, Field()]

    Zone_35_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_35: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_35: Annotated[str, Field()]

    Zone_36_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_36: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_36: Annotated[str, Field()]

    Zone_37_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_37: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_37: Annotated[str, Field()]

    Zone_38_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_38: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_38: Annotated[str, Field()]

    Zone_39_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_39: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_39: Annotated[str, Field()]

    Zone_40_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_40: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_40: Annotated[str, Field()]

    Zone_41_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_41: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_41: Annotated[str, Field()]

    Zone_42_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_42: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_42: Annotated[str, Field()]

    Zone_43_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_43: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_43: Annotated[str, Field()]

    Zone_44_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_44: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_44: Annotated[str, Field()]

    Zone_45_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_45: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_45: Annotated[str, Field()]

    Zone_46_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_46: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_46: Annotated[str, Field()]

    Zone_47_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_47: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_47: Annotated[str, Field()]

    Zone_48_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_48: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_48: Annotated[str, Field()]

    Zone_49_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_49: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_49: Annotated[str, Field()]

    Zone_50_Name: Annotated[str, Field()]
    """A zone name or a zone list name may be used here"""

    Design_Specification_Outdoor_Air_Object_Name_50: Annotated[str, Field()]

    Design_Specification_Zone_Air_Distribution_Object_Name_50: Annotated[str, Field()]