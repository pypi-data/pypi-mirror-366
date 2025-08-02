from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Fluidproperties_Concentration(EpBunch):
    """fluid properties for water/other fluid mixtures"""

    Fluid_Name: Annotated[str, Field()]
    """should not be any of the defaults (Water, EthyleneGlycol, or PropyleneGlycol)"""

    Fluid_Property_Type: Annotated[Literal['Density', 'SpecificHeat', 'Conductivity', 'Viscosity'], Field()]
    """Density Units are kg/m3"""

    Temperature_Values_Name: Annotated[str, Field()]
    """Enter the name of a FluidProperties:Temperatures object."""

    Concentration: Annotated[float, Field(ge=0.0, le=1.0)]
    """Glycol concentration for this list of properties entered as a fraction"""

    Property_Value_1: Annotated[float, Field()]

    Property_Value_2: Annotated[float, Field()]

    Property_Value_3: Annotated[float, Field()]

    Property_Value_4: Annotated[float, Field()]

    Property_Value_5: Annotated[float, Field()]

    Property_Value_6: Annotated[float, Field()]

    Property_Value_7: Annotated[float, Field()]

    Property_Value_8: Annotated[float, Field()]

    Property_Value_9: Annotated[float, Field()]

    Property_Value_10: Annotated[float, Field()]

    Property_Value_11: Annotated[float, Field()]

    Property_Value_12: Annotated[float, Field()]

    Property_Value_13: Annotated[float, Field()]

    Property_Value_14: Annotated[float, Field()]

    Property_Value_15: Annotated[float, Field()]

    Property_Value_16: Annotated[float, Field()]

    Property_Value_17: Annotated[float, Field()]

    Property_Value_18: Annotated[float, Field()]

    Property_Value_19: Annotated[float, Field()]

    Property_Value_20: Annotated[float, Field()]

    Property_Value_21: Annotated[float, Field()]

    Property_Value_22: Annotated[float, Field()]

    Property_Value_23: Annotated[float, Field()]

    Property_Value_24: Annotated[float, Field()]

    Property_Value_25: Annotated[float, Field()]

    Property_Value_26: Annotated[float, Field()]

    Property_Value_27: Annotated[float, Field()]

    Property_Value_28: Annotated[float, Field()]

    Property_Value_29: Annotated[float, Field()]

    Property_Value_30: Annotated[float, Field()]

    Property_Value_31: Annotated[float, Field()]

    Property_Value_32: Annotated[float, Field()]

    Property_Value_33: Annotated[float, Field()]

    Property_Value_34: Annotated[float, Field()]

    Property_Value_35: Annotated[float, Field()]

    Property_Value_36: Annotated[float, Field()]

    Property_Value_37: Annotated[float, Field()]

    Property_Value_38: Annotated[float, Field()]

    Property_Value_39: Annotated[float, Field()]

    Property_Value_40: Annotated[float, Field()]

    Property_Value_41: Annotated[float, Field()]

    Property_Value_42: Annotated[float, Field()]

    Property_Value_43: Annotated[float, Field()]

    Property_Value_44: Annotated[float, Field()]

    Property_Value_45: Annotated[float, Field()]

    Property_Value_46: Annotated[float, Field()]

    Property_Value_47: Annotated[float, Field()]

    Property_Value_48: Annotated[float, Field()]

    Property_Value_49: Annotated[float, Field()]

    Property_Value_50: Annotated[float, Field()]

    Property_Value_51: Annotated[float, Field()]

    Property_Value_52: Annotated[float, Field()]

    Property_Value_53: Annotated[float, Field()]

    Property_Value_54: Annotated[float, Field()]

    Property_Value_55: Annotated[float, Field()]

    Property_Value_56: Annotated[float, Field()]

    Property_Value_57: Annotated[float, Field()]

    Property_Value_58: Annotated[float, Field()]

    Property_Value_59: Annotated[float, Field()]

    Property_Value_60: Annotated[float, Field()]

    Property_Value_61: Annotated[float, Field()]

    Property_Value_62: Annotated[float, Field()]

    Property_Value_63: Annotated[float, Field()]

    Property_Value_64: Annotated[float, Field()]

    Property_Value_65: Annotated[float, Field()]

    Property_Value_66: Annotated[float, Field()]

    Property_Value_67: Annotated[float, Field()]

    Property_Value_68: Annotated[float, Field()]

    Property_Value_69: Annotated[float, Field()]

    Property_Value_70: Annotated[float, Field()]

    Property_Value_71: Annotated[float, Field()]

    Property_Value_72: Annotated[float, Field()]

    Property_Value_73: Annotated[float, Field()]

    Property_Value_74: Annotated[float, Field()]

    Property_Value_75: Annotated[float, Field()]

    Property_Value_76: Annotated[float, Field()]

    Property_Value_77: Annotated[float, Field()]

    Property_Value_78: Annotated[float, Field()]

    Property_Value_79: Annotated[float, Field()]

    Property_Value_80: Annotated[float, Field()]

    Property_Value_81: Annotated[float, Field()]

    Property_Value_82: Annotated[float, Field()]

    Property_Value_83: Annotated[float, Field()]

    Property_Value_84: Annotated[float, Field()]

    Property_Value_85: Annotated[float, Field()]

    Property_Value_86: Annotated[float, Field()]

    Property_Value_87: Annotated[float, Field()]

    Property_Value_88: Annotated[float, Field()]

    Property_Value_89: Annotated[float, Field()]

    Property_Value_90: Annotated[float, Field()]

    Property_Value_91: Annotated[float, Field()]

    Property_Value_92: Annotated[float, Field()]

    Property_Value_93: Annotated[float, Field()]

    Property_Value_94: Annotated[float, Field()]

    Property_Value_95: Annotated[float, Field()]

    Property_Value_96: Annotated[float, Field()]

    Property_Value_97: Annotated[float, Field()]

    Property_Value_98: Annotated[float, Field()]

    Property_Value_99: Annotated[float, Field()]

    Property_Value_100: Annotated[float, Field()]

    Property_Value_101: Annotated[float, Field()]

    Property_Value_102: Annotated[float, Field()]

    Property_Value_103: Annotated[float, Field()]

    Property_Value_104: Annotated[float, Field()]

    Property_Value_105: Annotated[float, Field()]

    Property_Value_106: Annotated[float, Field()]

    Property_Value_107: Annotated[float, Field()]

    Property_Value_108: Annotated[float, Field()]

    Property_Value_109: Annotated[float, Field()]

    Property_Value_110: Annotated[float, Field()]

    Property_Value_111: Annotated[float, Field()]

    Property_Value_112: Annotated[float, Field()]

    Property_Value_113: Annotated[float, Field()]

    Property_Value_114: Annotated[float, Field()]

    Property_Value_115: Annotated[float, Field()]

    Property_Value_116: Annotated[float, Field()]

    Property_Value_117: Annotated[float, Field()]

    Property_Value_118: Annotated[float, Field()]

    Property_Value_119: Annotated[float, Field()]

    Property_Value_120: Annotated[float, Field()]

    Property_Value_121: Annotated[float, Field()]

    Property_Value_122: Annotated[float, Field()]

    Property_Value_123: Annotated[float, Field()]

    Property_Value_124: Annotated[float, Field()]

    Property_Value_125: Annotated[float, Field()]

    Property_Value_126: Annotated[float, Field()]

    Property_Value_127: Annotated[float, Field()]

    Property_Value_128: Annotated[float, Field()]

    Property_Value_129: Annotated[float, Field()]

    Property_Value_130: Annotated[float, Field()]

    Property_Value_131: Annotated[float, Field()]

    Property_Value_132: Annotated[float, Field()]

    Property_Value_133: Annotated[float, Field()]

    Property_Value_134: Annotated[float, Field()]

    Property_Value_135: Annotated[float, Field()]

    Property_Value_136: Annotated[float, Field()]

    Property_Value_137: Annotated[float, Field()]

    Property_Value_138: Annotated[float, Field()]

    Property_Value_139: Annotated[float, Field()]

    Property_Value_140: Annotated[float, Field()]

    Property_Value_141: Annotated[float, Field()]

    Property_Value_142: Annotated[float, Field()]

    Property_Value_143: Annotated[float, Field()]

    Property_Value_144: Annotated[float, Field()]

    Property_Value_145: Annotated[float, Field()]

    Property_Value_146: Annotated[float, Field()]

    Property_Value_147: Annotated[float, Field()]

    Property_Value_148: Annotated[float, Field()]

    Property_Value_149: Annotated[float, Field()]

    Property_Value_150: Annotated[float, Field()]

    Property_Value_151: Annotated[float, Field()]

    Property_Value_152: Annotated[float, Field()]

    Property_Value_153: Annotated[float, Field()]

    Property_Value_154: Annotated[float, Field()]

    Property_Value_155: Annotated[float, Field()]

    Property_Value_156: Annotated[float, Field()]

    Property_Value_157: Annotated[float, Field()]

    Property_Value_158: Annotated[float, Field()]

    Property_Value_159: Annotated[float, Field()]

    Property_Value_160: Annotated[float, Field()]

    Property_Value_161: Annotated[float, Field()]

    Property_Value_162: Annotated[float, Field()]

    Property_Value_163: Annotated[float, Field()]

    Property_Value_164: Annotated[float, Field()]

    Property_Value_165: Annotated[float, Field()]

    Property_Value_166: Annotated[float, Field()]

    Property_Value_167: Annotated[float, Field()]

    Property_Value_168: Annotated[float, Field()]

    Property_Value_169: Annotated[float, Field()]

    Property_Value_170: Annotated[float, Field()]

    Property_Value_171: Annotated[float, Field()]

    Property_Value_172: Annotated[float, Field()]

    Property_Value_173: Annotated[float, Field()]

    Property_Value_174: Annotated[float, Field()]

    Property_Value_175: Annotated[float, Field()]

    Property_Value_176: Annotated[float, Field()]

    Property_Value_177: Annotated[float, Field()]

    Property_Value_178: Annotated[float, Field()]

    Property_Value_179: Annotated[float, Field()]

    Property_Value_180: Annotated[float, Field()]

    Property_Value_181: Annotated[float, Field()]

    Property_Value_182: Annotated[float, Field()]

    Property_Value_183: Annotated[float, Field()]

    Property_Value_184: Annotated[float, Field()]

    Property_Value_185: Annotated[float, Field()]

    Property_Value_186: Annotated[float, Field()]

    Property_Value_187: Annotated[float, Field()]

    Property_Value_188: Annotated[float, Field()]

    Property_Value_189: Annotated[float, Field()]

    Property_Value_190: Annotated[float, Field()]

    Property_Value_191: Annotated[float, Field()]

    Property_Value_192: Annotated[float, Field()]

    Property_Value_193: Annotated[float, Field()]

    Property_Value_194: Annotated[float, Field()]

    Property_Value_195: Annotated[float, Field()]

    Property_Value_196: Annotated[float, Field()]

    Property_Value_197: Annotated[float, Field()]

    Property_Value_198: Annotated[float, Field()]

    Property_Value_199: Annotated[float, Field()]

    Property_Value_200: Annotated[float, Field()]

    Property_Value_201: Annotated[float, Field()]

    Property_Value_202: Annotated[float, Field()]

    Property_Value_203: Annotated[float, Field()]

    Property_Value_204: Annotated[float, Field()]

    Property_Value_205: Annotated[float, Field()]

    Property_Value_206: Annotated[float, Field()]

    Property_Value_207: Annotated[float, Field()]

    Property_Value_208: Annotated[float, Field()]

    Property_Value_209: Annotated[float, Field()]

    Property_Value_210: Annotated[float, Field()]

    Property_Value_211: Annotated[float, Field()]

    Property_Value_212: Annotated[float, Field()]

    Property_Value_213: Annotated[float, Field()]

    Property_Value_214: Annotated[float, Field()]

    Property_Value_215: Annotated[float, Field()]

    Property_Value_216: Annotated[float, Field()]

    Property_Value_217: Annotated[float, Field()]

    Property_Value_218: Annotated[float, Field()]

    Property_Value_219: Annotated[float, Field()]

    Property_Value_220: Annotated[float, Field()]

    Property_Value_221: Annotated[float, Field()]

    Property_Value_222: Annotated[float, Field()]

    Property_Value_223: Annotated[float, Field()]

    Property_Value_224: Annotated[float, Field()]

    Property_Value_225: Annotated[float, Field()]

    Property_Value_226: Annotated[float, Field()]

    Property_Value_227: Annotated[float, Field()]

    Property_Value_228: Annotated[float, Field()]

    Property_Value_229: Annotated[float, Field()]

    Property_Value_230: Annotated[float, Field()]

    Property_Value_231: Annotated[float, Field()]

    Property_Value_232: Annotated[float, Field()]

    Property_Value_233: Annotated[float, Field()]

    Property_Value_234: Annotated[float, Field()]

    Property_Value_235: Annotated[float, Field()]

    Property_Value_236: Annotated[float, Field()]

    Property_Value_237: Annotated[float, Field()]

    Property_Value_238: Annotated[float, Field()]

    Property_Value_239: Annotated[float, Field()]

    Property_Value_240: Annotated[float, Field()]

    Property_Value_241: Annotated[float, Field()]

    Property_Value_242: Annotated[float, Field()]

    Property_Value_243: Annotated[float, Field()]

    Property_Value_244: Annotated[float, Field()]

    Property_Value_245: Annotated[float, Field()]

    Property_Value_246: Annotated[float, Field()]

    Property_Value_247: Annotated[float, Field()]

    Property_Value_248: Annotated[float, Field()]

    Property_Value_249: Annotated[float, Field()]

    Property_Value_250: Annotated[float, Field()]