from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Parametric_Runcontrol(EpBunch):
    """Controls which parametric runs are simulated. This object is optional. If it is not"""

    Name: Annotated[str, Field()]

    Perform_Run_1: Annotated[Literal['Yes', 'No'], Field(default='Yes')]

    Perform_Run_2: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_3: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_4: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_5: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_6: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_7: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_8: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_9: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_10: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_11: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_12: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_13: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_14: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_15: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_16: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_17: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_18: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_19: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_20: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_21: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_22: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_23: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_24: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_25: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_26: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_27: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_28: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_29: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_30: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_31: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_32: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_33: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_34: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_35: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_36: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_37: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_38: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_39: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_40: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_41: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_42: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_43: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_44: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_45: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_46: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_47: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_48: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_49: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_50: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_51: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_52: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_53: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_54: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_55: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_56: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_57: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_58: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_59: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_60: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_61: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_62: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_63: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_64: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_65: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_66: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_67: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_68: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_69: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_70: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_71: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_72: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_73: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_74: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_75: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_76: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_77: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_78: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_79: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_80: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_81: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_82: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_83: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_84: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_85: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_86: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_87: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_88: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_89: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_90: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_91: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_92: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_93: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_94: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_95: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_96: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_97: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_98: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_99: Annotated[Literal['Yes', 'No'], Field()]

    Perform_Run_100: Annotated[Literal['Yes', 'No'], Field()]