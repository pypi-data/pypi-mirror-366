from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheatexchanger_System(EpBunch):
    """Models vertical ground heat exchangers systems using the response factor approach"""

    Name: Annotated[str, Field(default=...)]

    Inlet_Node_Name: Annotated[str, Field(default=...)]

    Outlet_Node_Name: Annotated[str, Field(default=...)]

    Design_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Undisturbed_Ground_Temperature_Model_Type: Annotated[Literal['Site:GroundTemperature:Undisturbed:FiniteDifference', 'Site:GroundTemperature:Undisturbed:KusudaAchenbach', 'Site:GroundTemperature:Undisturbed:Xing'], Field(default=...)]

    Undisturbed_Ground_Temperature_Model_Name: Annotated[str, Field(default=...)]

    Ground_Thermal_Conductivity: Annotated[float, Field(default=..., gt=0.0)]

    Ground_Thermal_Heat_Capacity: Annotated[float, Field(default=..., gt=0.0)]

    GHEVerticalResponseFactors_Object_Name: Annotated[str, Field()]

    GHEVerticalArray_Object_Name: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_1: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_2: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_3: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_4: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_5: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_6: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_7: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_8: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_9: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_10: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_11: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_12: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_13: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_14: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_15: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_16: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_17: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_18: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_19: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_20: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_21: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_22: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_23: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_24: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_25: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_26: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_27: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_28: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_29: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_30: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_31: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_32: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_33: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_34: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_35: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_36: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_37: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_38: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_39: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_40: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_41: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_42: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_43: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_44: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_45: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_46: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_47: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_48: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_49: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_50: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_51: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_52: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_53: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_54: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_55: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_56: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_57: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_58: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_59: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_60: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_61: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_62: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_63: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_64: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_65: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_66: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_67: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_68: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_69: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_70: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_71: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_72: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_73: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_74: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_75: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_76: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_77: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_78: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_79: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_80: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_81: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_82: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_83: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_84: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_85: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_86: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_87: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_88: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_89: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_90: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_91: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_92: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_93: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_94: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_95: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_96: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_97: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_98: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_99: Annotated[str, Field()]

    GHEVerticalSingle_Object_Name_100: Annotated[str, Field()]