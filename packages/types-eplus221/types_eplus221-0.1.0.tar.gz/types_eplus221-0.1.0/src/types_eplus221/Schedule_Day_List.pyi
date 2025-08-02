from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Schedule_Day_List(EpBunch):
    """Schedule:Day:List will allow the user to list 24 hours worth of values, which can be sub-hourly in nature."""

    Name: Annotated[str, Field(default=...)]

    Schedule_Type_Limits_Name: Annotated[str, Field()]

    Interpolate_To_Timestep: Annotated[Literal['Average', 'Linear', 'No'], Field(default='No')]
    """when the interval does not match the user specified timestep a "Average" choice will average between the intervals request (to"""

    Minutes_Per_Item: Annotated[int, Field(ge=1, le=60)]
    """Must be evenly divisible into 60"""

    Value_1: Annotated[str, Field(default='0.0')]

    Value_2: Annotated[str, Field(default='0.0')]

    Value_3: Annotated[str, Field(default='0.0')]

    Value_4: Annotated[str, Field(default='0.0')]

    Value_5: Annotated[str, Field(default='0.0')]

    Value_6: Annotated[str, Field(default='0.0')]

    Value_7: Annotated[str, Field(default='0.0')]

    Value_8: Annotated[str, Field(default='0.0')]

    Value_9: Annotated[str, Field(default='0.0')]

    Value_10: Annotated[str, Field(default='0.0')]

    Value_11: Annotated[str, Field(default='0.0')]

    Value_12: Annotated[str, Field(default='0.0')]

    Value_13: Annotated[str, Field(default='0.0')]

    Value_14: Annotated[str, Field(default='0.0')]

    Value_15: Annotated[str, Field(default='0.0')]

    Value_16: Annotated[str, Field(default='0.0')]

    Value_17: Annotated[str, Field(default='0.0')]

    Value_18: Annotated[str, Field(default='0.0')]

    Value_19: Annotated[str, Field(default='0.0')]

    Value_20: Annotated[str, Field(default='0.0')]

    Value_21: Annotated[str, Field(default='0.0')]

    Value_22: Annotated[str, Field(default='0.0')]

    Value_23: Annotated[str, Field(default='0.0')]

    Value_24: Annotated[str, Field(default='0.0')]

    Value_25: Annotated[str, Field(default='0.0')]

    Value_26: Annotated[str, Field(default='0.0')]

    Value_27: Annotated[str, Field(default='0.0')]

    Value_28: Annotated[str, Field(default='0.0')]

    Value_29: Annotated[str, Field(default='0.0')]

    Value_30: Annotated[str, Field(default='0.0')]

    Value_31: Annotated[str, Field(default='0.0')]

    Value_32: Annotated[str, Field(default='0.0')]

    Value_33: Annotated[str, Field(default='0.0')]

    Value_34: Annotated[str, Field(default='0.0')]

    Value_35: Annotated[str, Field(default='0.0')]

    Value_36: Annotated[str, Field(default='0.0')]

    Value_37: Annotated[str, Field(default='0.0')]

    Value_38: Annotated[str, Field(default='0.0')]

    Value_39: Annotated[str, Field(default='0.0')]

    Value_40: Annotated[str, Field(default='0.0')]

    Value_41: Annotated[str, Field(default='0.0')]

    Value_42: Annotated[str, Field(default='0.0')]

    Value_43: Annotated[str, Field(default='0.0')]

    Value_44: Annotated[str, Field(default='0.0')]

    Value_45: Annotated[str, Field(default='0.0')]

    Value_46: Annotated[str, Field(default='0.0')]

    Value_47: Annotated[str, Field(default='0.0')]

    Value_48: Annotated[str, Field(default='0.0')]

    Value_49: Annotated[str, Field(default='0.0')]

    Value_50: Annotated[str, Field(default='0.0')]

    Value_51: Annotated[str, Field(default='0.0')]

    Value_52: Annotated[str, Field(default='0.0')]

    Value_53: Annotated[str, Field(default='0.0')]

    Value_54: Annotated[str, Field(default='0.0')]

    Value_55: Annotated[str, Field(default='0.0')]

    Value_56: Annotated[str, Field(default='0.0')]

    Value_57: Annotated[str, Field(default='0.0')]

    Value_58: Annotated[str, Field(default='0.0')]

    Value_59: Annotated[str, Field(default='0.0')]

    Value_60: Annotated[str, Field(default='0.0')]

    Value_61: Annotated[str, Field(default='0.0')]

    Value_62: Annotated[str, Field(default='0.0')]

    Value_63: Annotated[str, Field(default='0.0')]

    Value_64: Annotated[str, Field(default='0.0')]

    Value_65: Annotated[str, Field(default='0.0')]

    Value_66: Annotated[str, Field(default='0.0')]

    Value_67: Annotated[str, Field(default='0.0')]

    Value_68: Annotated[str, Field(default='0.0')]

    Value_69: Annotated[str, Field(default='0.0')]

    Value_70: Annotated[str, Field(default='0.0')]

    Value_71: Annotated[str, Field(default='0.0')]

    Value_72: Annotated[str, Field(default='0.0')]

    Value_73: Annotated[str, Field(default='0.0')]

    Value_74: Annotated[str, Field(default='0.0')]

    Value_75: Annotated[str, Field(default='0.0')]

    Value_76: Annotated[str, Field(default='0.0')]

    Value_77: Annotated[str, Field(default='0.0')]

    Value_78: Annotated[str, Field(default='0.0')]

    Value_79: Annotated[str, Field(default='0.0')]

    Value_80: Annotated[str, Field(default='0.0')]

    Value_81: Annotated[str, Field(default='0.0')]

    Value_82: Annotated[str, Field(default='0.0')]

    Value_83: Annotated[str, Field(default='0.0')]

    Value_84: Annotated[str, Field(default='0.0')]

    Value_85: Annotated[str, Field(default='0.0')]

    Value_86: Annotated[str, Field(default='0.0')]

    Value_87: Annotated[str, Field(default='0.0')]

    Value_88: Annotated[str, Field(default='0.0')]

    Value_89: Annotated[str, Field(default='0.0')]

    Value_90: Annotated[str, Field(default='0.0')]

    Value_91: Annotated[str, Field(default='0.0')]

    Value_92: Annotated[str, Field(default='0.0')]

    Value_93: Annotated[str, Field(default='0.0')]

    Value_94: Annotated[str, Field(default='0.0')]

    Value_95: Annotated[str, Field(default='0.0')]

    Value_96: Annotated[str, Field(default='0.0')]

    Value_97: Annotated[str, Field(default='0.0')]

    Value_98: Annotated[str, Field(default='0.0')]

    Value_99: Annotated[str, Field(default='0.0')]

    Value_100: Annotated[str, Field(default='0.0')]

    Value_101: Annotated[str, Field(default='0.0')]

    Value_102: Annotated[str, Field(default='0.0')]

    Value_103: Annotated[str, Field(default='0.0')]

    Value_104: Annotated[str, Field(default='0.0')]

    Value_105: Annotated[str, Field(default='0.0')]

    Value_106: Annotated[str, Field(default='0.0')]

    Value_107: Annotated[str, Field(default='0.0')]

    Value_108: Annotated[str, Field(default='0.0')]

    Value_109: Annotated[str, Field(default='0.0')]

    Value_110: Annotated[str, Field(default='0.0')]

    Value_111: Annotated[str, Field(default='0.0')]

    Value_112: Annotated[str, Field(default='0.0')]

    Value_113: Annotated[str, Field(default='0.0')]

    Value_114: Annotated[str, Field(default='0.0')]

    Value_115: Annotated[str, Field(default='0.0')]

    Value_116: Annotated[str, Field(default='0.0')]

    Value_117: Annotated[str, Field(default='0.0')]

    Value_118: Annotated[str, Field(default='0.0')]

    Value_119: Annotated[str, Field(default='0.0')]

    Value_120: Annotated[str, Field(default='0.0')]

    Value_121: Annotated[str, Field(default='0.0')]

    Value_122: Annotated[str, Field(default='0.0')]

    Value_123: Annotated[str, Field(default='0.0')]

    Value_124: Annotated[str, Field(default='0.0')]

    Value_125: Annotated[str, Field(default='0.0')]

    Value_126: Annotated[str, Field(default='0.0')]

    Value_127: Annotated[str, Field(default='0.0')]

    Value_128: Annotated[str, Field(default='0.0')]

    Value_129: Annotated[str, Field(default='0.0')]

    Value_130: Annotated[str, Field(default='0.0')]

    Value_131: Annotated[str, Field(default='0.0')]

    Value_132: Annotated[str, Field(default='0.0')]

    Value_133: Annotated[str, Field(default='0.0')]

    Value_134: Annotated[str, Field(default='0.0')]

    Value_135: Annotated[str, Field(default='0.0')]

    Value_136: Annotated[str, Field(default='0.0')]

    Value_137: Annotated[str, Field(default='0.0')]

    Value_138: Annotated[str, Field(default='0.0')]

    Value_139: Annotated[str, Field(default='0.0')]

    Value_140: Annotated[str, Field(default='0.0')]

    Value_141: Annotated[str, Field(default='0.0')]

    Value_142: Annotated[str, Field(default='0.0')]

    Value_143: Annotated[str, Field(default='0.0')]

    Value_144: Annotated[str, Field(default='0.0')]

    Value_145: Annotated[str, Field(default='0.0')]

    Value_146: Annotated[str, Field(default='0.0')]

    Value_147: Annotated[str, Field(default='0.0')]

    Value_148: Annotated[str, Field(default='0.0')]

    Value_149: Annotated[str, Field(default='0.0')]

    Value_150: Annotated[str, Field(default='0.0')]

    Value_151: Annotated[str, Field(default='0.0')]

    Value_152: Annotated[str, Field(default='0.0')]

    Value_153: Annotated[str, Field(default='0.0')]

    Value_154: Annotated[str, Field(default='0.0')]

    Value_155: Annotated[str, Field(default='0.0')]

    Value_156: Annotated[str, Field(default='0.0')]

    Value_157: Annotated[str, Field(default='0.0')]

    Value_158: Annotated[str, Field(default='0.0')]

    Value_159: Annotated[str, Field(default='0.0')]

    Value_160: Annotated[str, Field(default='0.0')]

    Value_161: Annotated[str, Field(default='0.0')]

    Value_162: Annotated[str, Field(default='0.0')]

    Value_163: Annotated[str, Field(default='0.0')]

    Value_164: Annotated[str, Field(default='0.0')]

    Value_165: Annotated[str, Field(default='0.0')]

    Value_166: Annotated[str, Field(default='0.0')]

    Value_167: Annotated[str, Field(default='0.0')]

    Value_168: Annotated[str, Field(default='0.0')]

    Value_169: Annotated[str, Field(default='0.0')]

    Value_170: Annotated[str, Field(default='0.0')]

    Value_171: Annotated[str, Field(default='0.0')]

    Value_172: Annotated[str, Field(default='0.0')]

    Value_173: Annotated[str, Field(default='0.0')]

    Value_174: Annotated[str, Field(default='0.0')]

    Value_175: Annotated[str, Field(default='0.0')]

    Value_176: Annotated[str, Field(default='0.0')]

    Value_177: Annotated[str, Field(default='0.0')]

    Value_178: Annotated[str, Field(default='0.0')]

    Value_179: Annotated[str, Field(default='0.0')]

    Value_180: Annotated[str, Field(default='0.0')]

    Value_181: Annotated[str, Field(default='0.0')]

    Value_182: Annotated[str, Field(default='0.0')]

    Value_183: Annotated[str, Field(default='0.0')]

    Value_184: Annotated[str, Field(default='0.0')]

    Value_185: Annotated[str, Field(default='0.0')]

    Value_186: Annotated[str, Field(default='0.0')]

    Value_187: Annotated[str, Field(default='0.0')]

    Value_188: Annotated[str, Field(default='0.0')]

    Value_189: Annotated[str, Field(default='0.0')]

    Value_190: Annotated[str, Field(default='0.0')]

    Value_191: Annotated[str, Field(default='0.0')]

    Value_192: Annotated[str, Field(default='0.0')]

    Value_193: Annotated[str, Field(default='0.0')]

    Value_194: Annotated[str, Field(default='0.0')]

    Value_195: Annotated[str, Field(default='0.0')]

    Value_196: Annotated[str, Field(default='0.0')]

    Value_197: Annotated[str, Field(default='0.0')]

    Value_198: Annotated[str, Field(default='0.0')]

    Value_199: Annotated[str, Field(default='0.0')]

    Value_200: Annotated[str, Field(default='0.0')]

    Value_201: Annotated[str, Field(default='0.0')]

    Value_202: Annotated[str, Field(default='0.0')]

    Value_203: Annotated[str, Field(default='0.0')]

    Value_204: Annotated[str, Field(default='0.0')]

    Value_205: Annotated[str, Field(default='0.0')]

    Value_206: Annotated[str, Field(default='0.0')]

    Value_207: Annotated[str, Field(default='0.0')]

    Value_208: Annotated[str, Field(default='0.0')]

    Value_209: Annotated[str, Field(default='0.0')]

    Value_210: Annotated[str, Field(default='0.0')]

    Value_211: Annotated[str, Field(default='0.0')]

    Value_212: Annotated[str, Field(default='0.0')]

    Value_213: Annotated[str, Field(default='0.0')]

    Value_214: Annotated[str, Field(default='0.0')]

    Value_215: Annotated[str, Field(default='0.0')]

    Value_216: Annotated[str, Field(default='0.0')]

    Value_217: Annotated[str, Field(default='0.0')]

    Value_218: Annotated[str, Field(default='0.0')]

    Value_219: Annotated[str, Field(default='0.0')]

    Value_220: Annotated[str, Field(default='0.0')]

    Value_221: Annotated[str, Field(default='0.0')]

    Value_222: Annotated[str, Field(default='0.0')]

    Value_223: Annotated[str, Field(default='0.0')]

    Value_224: Annotated[str, Field(default='0.0')]

    Value_225: Annotated[str, Field(default='0.0')]

    Value_226: Annotated[str, Field(default='0.0')]

    Value_227: Annotated[str, Field(default='0.0')]

    Value_228: Annotated[str, Field(default='0.0')]

    Value_229: Annotated[str, Field(default='0.0')]

    Value_230: Annotated[str, Field(default='0.0')]

    Value_231: Annotated[str, Field(default='0.0')]

    Value_232: Annotated[str, Field(default='0.0')]

    Value_233: Annotated[str, Field(default='0.0')]

    Value_234: Annotated[str, Field(default='0.0')]

    Value_235: Annotated[str, Field(default='0.0')]

    Value_236: Annotated[str, Field(default='0.0')]

    Value_237: Annotated[str, Field(default='0.0')]

    Value_238: Annotated[str, Field(default='0.0')]

    Value_239: Annotated[str, Field(default='0.0')]

    Value_240: Annotated[str, Field(default='0.0')]

    Value_241: Annotated[str, Field(default='0.0')]

    Value_242: Annotated[str, Field(default='0.0')]

    Value_243: Annotated[str, Field(default='0.0')]

    Value_244: Annotated[str, Field(default='0.0')]

    Value_245: Annotated[str, Field(default='0.0')]

    Value_246: Annotated[str, Field(default='0.0')]

    Value_247: Annotated[str, Field(default='0.0')]

    Value_248: Annotated[str, Field(default='0.0')]

    Value_249: Annotated[str, Field(default='0.0')]

    Value_250: Annotated[str, Field(default='0.0')]

    Value_251: Annotated[str, Field(default='0.0')]

    Value_252: Annotated[str, Field(default='0.0')]

    Value_253: Annotated[str, Field(default='0.0')]

    Value_254: Annotated[str, Field(default='0.0')]

    Value_255: Annotated[str, Field(default='0.0')]

    Value_256: Annotated[str, Field(default='0.0')]

    Value_257: Annotated[str, Field(default='0.0')]

    Value_258: Annotated[str, Field(default='0.0')]

    Value_259: Annotated[str, Field(default='0.0')]

    Value_260: Annotated[str, Field(default='0.0')]

    Value_261: Annotated[str, Field(default='0.0')]

    Value_262: Annotated[str, Field(default='0.0')]

    Value_263: Annotated[str, Field(default='0.0')]

    Value_264: Annotated[str, Field(default='0.0')]

    Value_265: Annotated[str, Field(default='0.0')]

    Value_266: Annotated[str, Field(default='0.0')]

    Value_267: Annotated[str, Field(default='0.0')]

    Value_268: Annotated[str, Field(default='0.0')]

    Value_269: Annotated[str, Field(default='0.0')]

    Value_270: Annotated[str, Field(default='0.0')]

    Value_271: Annotated[str, Field(default='0.0')]

    Value_272: Annotated[str, Field(default='0.0')]

    Value_273: Annotated[str, Field(default='0.0')]

    Value_274: Annotated[str, Field(default='0.0')]

    Value_275: Annotated[str, Field(default='0.0')]

    Value_276: Annotated[str, Field(default='0.0')]

    Value_277: Annotated[str, Field(default='0.0')]

    Value_278: Annotated[str, Field(default='0.0')]

    Value_279: Annotated[str, Field(default='0.0')]

    Value_280: Annotated[str, Field(default='0.0')]

    Value_281: Annotated[str, Field(default='0.0')]

    Value_282: Annotated[str, Field(default='0.0')]

    Value_283: Annotated[str, Field(default='0.0')]

    Value_284: Annotated[str, Field(default='0.0')]

    Value_285: Annotated[str, Field(default='0.0')]

    Value_286: Annotated[str, Field(default='0.0')]

    Value_287: Annotated[str, Field(default='0.0')]

    Value_288: Annotated[str, Field(default='0.0')]

    Value_289: Annotated[str, Field(default='0.0')]

    Value_290: Annotated[str, Field(default='0.0')]

    Value_291: Annotated[str, Field(default='0.0')]

    Value_292: Annotated[str, Field(default='0.0')]

    Value_293: Annotated[str, Field(default='0.0')]

    Value_294: Annotated[str, Field(default='0.0')]

    Value_295: Annotated[str, Field(default='0.0')]

    Value_296: Annotated[str, Field(default='0.0')]

    Value_297: Annotated[str, Field(default='0.0')]

    Value_298: Annotated[str, Field(default='0.0')]

    Value_299: Annotated[str, Field(default='0.0')]

    Value_300: Annotated[str, Field(default='0.0')]

    Value_301: Annotated[str, Field(default='0.0')]

    Value_302: Annotated[str, Field(default='0.0')]

    Value_303: Annotated[str, Field(default='0.0')]

    Value_304: Annotated[str, Field(default='0.0')]

    Value_305: Annotated[str, Field(default='0.0')]

    Value_306: Annotated[str, Field(default='0.0')]

    Value_307: Annotated[str, Field(default='0.0')]

    Value_308: Annotated[str, Field(default='0.0')]

    Value_309: Annotated[str, Field(default='0.0')]

    Value_310: Annotated[str, Field(default='0.0')]

    Value_311: Annotated[str, Field(default='0.0')]

    Value_312: Annotated[str, Field(default='0.0')]

    Value_313: Annotated[str, Field(default='0.0')]

    Value_314: Annotated[str, Field(default='0.0')]

    Value_315: Annotated[str, Field(default='0.0')]

    Value_316: Annotated[str, Field(default='0.0')]

    Value_317: Annotated[str, Field(default='0.0')]

    Value_318: Annotated[str, Field(default='0.0')]

    Value_319: Annotated[str, Field(default='0.0')]

    Value_320: Annotated[str, Field(default='0.0')]

    Value_321: Annotated[str, Field(default='0.0')]

    Value_322: Annotated[str, Field(default='0.0')]

    Value_323: Annotated[str, Field(default='0.0')]

    Value_324: Annotated[str, Field(default='0.0')]

    Value_325: Annotated[str, Field(default='0.0')]

    Value_326: Annotated[str, Field(default='0.0')]

    Value_327: Annotated[str, Field(default='0.0')]

    Value_328: Annotated[str, Field(default='0.0')]

    Value_329: Annotated[str, Field(default='0.0')]

    Value_330: Annotated[str, Field(default='0.0')]

    Value_331: Annotated[str, Field(default='0.0')]

    Value_332: Annotated[str, Field(default='0.0')]

    Value_333: Annotated[str, Field(default='0.0')]

    Value_334: Annotated[str, Field(default='0.0')]

    Value_335: Annotated[str, Field(default='0.0')]

    Value_336: Annotated[str, Field(default='0.0')]

    Value_337: Annotated[str, Field(default='0.0')]

    Value_338: Annotated[str, Field(default='0.0')]

    Value_339: Annotated[str, Field(default='0.0')]

    Value_340: Annotated[str, Field(default='0.0')]

    Value_341: Annotated[str, Field(default='0.0')]

    Value_342: Annotated[str, Field(default='0.0')]

    Value_343: Annotated[str, Field(default='0.0')]

    Value_344: Annotated[str, Field(default='0.0')]

    Value_345: Annotated[str, Field(default='0.0')]

    Value_346: Annotated[str, Field(default='0.0')]

    Value_347: Annotated[str, Field(default='0.0')]

    Value_348: Annotated[str, Field(default='0.0')]

    Value_349: Annotated[str, Field(default='0.0')]

    Value_350: Annotated[str, Field(default='0.0')]

    Value_351: Annotated[str, Field(default='0.0')]

    Value_352: Annotated[str, Field(default='0.0')]

    Value_353: Annotated[str, Field(default='0.0')]

    Value_354: Annotated[str, Field(default='0.0')]

    Value_355: Annotated[str, Field(default='0.0')]

    Value_356: Annotated[str, Field(default='0.0')]

    Value_357: Annotated[str, Field(default='0.0')]

    Value_358: Annotated[str, Field(default='0.0')]

    Value_359: Annotated[str, Field(default='0.0')]

    Value_360: Annotated[str, Field(default='0.0')]

    Value_361: Annotated[str, Field(default='0.0')]

    Value_362: Annotated[str, Field(default='0.0')]

    Value_363: Annotated[str, Field(default='0.0')]

    Value_364: Annotated[str, Field(default='0.0')]

    Value_365: Annotated[str, Field(default='0.0')]

    Value_366: Annotated[str, Field(default='0.0')]

    Value_367: Annotated[str, Field(default='0.0')]

    Value_368: Annotated[str, Field(default='0.0')]

    Value_369: Annotated[str, Field(default='0.0')]

    Value_370: Annotated[str, Field(default='0.0')]

    Value_371: Annotated[str, Field(default='0.0')]

    Value_372: Annotated[str, Field(default='0.0')]

    Value_373: Annotated[str, Field(default='0.0')]

    Value_374: Annotated[str, Field(default='0.0')]

    Value_375: Annotated[str, Field(default='0.0')]

    Value_376: Annotated[str, Field(default='0.0')]

    Value_377: Annotated[str, Field(default='0.0')]

    Value_378: Annotated[str, Field(default='0.0')]

    Value_379: Annotated[str, Field(default='0.0')]

    Value_380: Annotated[str, Field(default='0.0')]

    Value_381: Annotated[str, Field(default='0.0')]

    Value_382: Annotated[str, Field(default='0.0')]

    Value_383: Annotated[str, Field(default='0.0')]

    Value_384: Annotated[str, Field(default='0.0')]

    Value_385: Annotated[str, Field(default='0.0')]

    Value_386: Annotated[str, Field(default='0.0')]

    Value_387: Annotated[str, Field(default='0.0')]

    Value_388: Annotated[str, Field(default='0.0')]

    Value_389: Annotated[str, Field(default='0.0')]

    Value_390: Annotated[str, Field(default='0.0')]

    Value_391: Annotated[str, Field(default='0.0')]

    Value_392: Annotated[str, Field(default='0.0')]

    Value_393: Annotated[str, Field(default='0.0')]

    Value_394: Annotated[str, Field(default='0.0')]

    Value_395: Annotated[str, Field(default='0.0')]

    Value_396: Annotated[str, Field(default='0.0')]

    Value_397: Annotated[str, Field(default='0.0')]

    Value_398: Annotated[str, Field(default='0.0')]

    Value_399: Annotated[str, Field(default='0.0')]

    Value_400: Annotated[str, Field(default='0.0')]

    Value_401: Annotated[str, Field(default='0.0')]

    Value_402: Annotated[str, Field(default='0.0')]

    Value_403: Annotated[str, Field(default='0.0')]

    Value_404: Annotated[str, Field(default='0.0')]

    Value_405: Annotated[str, Field(default='0.0')]

    Value_406: Annotated[str, Field(default='0.0')]

    Value_407: Annotated[str, Field(default='0.0')]

    Value_408: Annotated[str, Field(default='0.0')]

    Value_409: Annotated[str, Field(default='0.0')]

    Value_410: Annotated[str, Field(default='0.0')]

    Value_411: Annotated[str, Field(default='0.0')]

    Value_412: Annotated[str, Field(default='0.0')]

    Value_413: Annotated[str, Field(default='0.0')]

    Value_414: Annotated[str, Field(default='0.0')]

    Value_415: Annotated[str, Field(default='0.0')]

    Value_416: Annotated[str, Field(default='0.0')]

    Value_417: Annotated[str, Field(default='0.0')]

    Value_418: Annotated[str, Field(default='0.0')]

    Value_419: Annotated[str, Field(default='0.0')]

    Value_420: Annotated[str, Field(default='0.0')]

    Value_421: Annotated[str, Field(default='0.0')]

    Value_422: Annotated[str, Field(default='0.0')]

    Value_423: Annotated[str, Field(default='0.0')]

    Value_424: Annotated[str, Field(default='0.0')]

    Value_425: Annotated[str, Field(default='0.0')]

    Value_426: Annotated[str, Field(default='0.0')]

    Value_427: Annotated[str, Field(default='0.0')]

    Value_428: Annotated[str, Field(default='0.0')]

    Value_429: Annotated[str, Field(default='0.0')]

    Value_430: Annotated[str, Field(default='0.0')]

    Value_431: Annotated[str, Field(default='0.0')]

    Value_432: Annotated[str, Field(default='0.0')]

    Value_433: Annotated[str, Field(default='0.0')]

    Value_434: Annotated[str, Field(default='0.0')]

    Value_435: Annotated[str, Field(default='0.0')]

    Value_436: Annotated[str, Field(default='0.0')]

    Value_437: Annotated[str, Field(default='0.0')]

    Value_438: Annotated[str, Field(default='0.0')]

    Value_439: Annotated[str, Field(default='0.0')]

    Value_440: Annotated[str, Field(default='0.0')]

    Value_441: Annotated[str, Field(default='0.0')]

    Value_442: Annotated[str, Field(default='0.0')]

    Value_443: Annotated[str, Field(default='0.0')]

    Value_444: Annotated[str, Field(default='0.0')]

    Value_445: Annotated[str, Field(default='0.0')]

    Value_446: Annotated[str, Field(default='0.0')]

    Value_447: Annotated[str, Field(default='0.0')]

    Value_448: Annotated[str, Field(default='0.0')]

    Value_449: Annotated[str, Field(default='0.0')]

    Value_450: Annotated[str, Field(default='0.0')]

    Value_451: Annotated[str, Field(default='0.0')]

    Value_452: Annotated[str, Field(default='0.0')]

    Value_453: Annotated[str, Field(default='0.0')]

    Value_454: Annotated[str, Field(default='0.0')]

    Value_455: Annotated[str, Field(default='0.0')]

    Value_456: Annotated[str, Field(default='0.0')]

    Value_457: Annotated[str, Field(default='0.0')]

    Value_458: Annotated[str, Field(default='0.0')]

    Value_459: Annotated[str, Field(default='0.0')]

    Value_460: Annotated[str, Field(default='0.0')]

    Value_461: Annotated[str, Field(default='0.0')]

    Value_462: Annotated[str, Field(default='0.0')]

    Value_463: Annotated[str, Field(default='0.0')]

    Value_464: Annotated[str, Field(default='0.0')]

    Value_465: Annotated[str, Field(default='0.0')]

    Value_466: Annotated[str, Field(default='0.0')]

    Value_467: Annotated[str, Field(default='0.0')]

    Value_468: Annotated[str, Field(default='0.0')]

    Value_469: Annotated[str, Field(default='0.0')]

    Value_470: Annotated[str, Field(default='0.0')]

    Value_471: Annotated[str, Field(default='0.0')]

    Value_472: Annotated[str, Field(default='0.0')]

    Value_473: Annotated[str, Field(default='0.0')]

    Value_474: Annotated[str, Field(default='0.0')]

    Value_475: Annotated[str, Field(default='0.0')]

    Value_476: Annotated[str, Field(default='0.0')]

    Value_477: Annotated[str, Field(default='0.0')]

    Value_478: Annotated[str, Field(default='0.0')]

    Value_479: Annotated[str, Field(default='0.0')]

    Value_480: Annotated[str, Field(default='0.0')]

    Value_481: Annotated[str, Field(default='0.0')]

    Value_482: Annotated[str, Field(default='0.0')]

    Value_483: Annotated[str, Field(default='0.0')]

    Value_484: Annotated[str, Field(default='0.0')]

    Value_485: Annotated[str, Field(default='0.0')]

    Value_486: Annotated[str, Field(default='0.0')]

    Value_487: Annotated[str, Field(default='0.0')]

    Value_488: Annotated[str, Field(default='0.0')]

    Value_489: Annotated[str, Field(default='0.0')]

    Value_490: Annotated[str, Field(default='0.0')]

    Value_491: Annotated[str, Field(default='0.0')]

    Value_492: Annotated[str, Field(default='0.0')]

    Value_493: Annotated[str, Field(default='0.0')]

    Value_494: Annotated[str, Field(default='0.0')]

    Value_495: Annotated[str, Field(default='0.0')]

    Value_496: Annotated[str, Field(default='0.0')]

    Value_497: Annotated[str, Field(default='0.0')]

    Value_498: Annotated[str, Field(default='0.0')]

    Value_499: Annotated[str, Field(default='0.0')]

    Value_500: Annotated[str, Field(default='0.0')]

    Value_501: Annotated[str, Field(default='0.0')]

    Value_502: Annotated[str, Field(default='0.0')]

    Value_503: Annotated[str, Field(default='0.0')]

    Value_504: Annotated[str, Field(default='0.0')]

    Value_505: Annotated[str, Field(default='0.0')]

    Value_506: Annotated[str, Field(default='0.0')]

    Value_507: Annotated[str, Field(default='0.0')]

    Value_508: Annotated[str, Field(default='0.0')]

    Value_509: Annotated[str, Field(default='0.0')]

    Value_510: Annotated[str, Field(default='0.0')]

    Value_511: Annotated[str, Field(default='0.0')]

    Value_512: Annotated[str, Field(default='0.0')]

    Value_513: Annotated[str, Field(default='0.0')]

    Value_514: Annotated[str, Field(default='0.0')]

    Value_515: Annotated[str, Field(default='0.0')]

    Value_516: Annotated[str, Field(default='0.0')]

    Value_517: Annotated[str, Field(default='0.0')]

    Value_518: Annotated[str, Field(default='0.0')]

    Value_519: Annotated[str, Field(default='0.0')]

    Value_520: Annotated[str, Field(default='0.0')]

    Value_521: Annotated[str, Field(default='0.0')]

    Value_522: Annotated[str, Field(default='0.0')]

    Value_523: Annotated[str, Field(default='0.0')]

    Value_524: Annotated[str, Field(default='0.0')]

    Value_525: Annotated[str, Field(default='0.0')]

    Value_526: Annotated[str, Field(default='0.0')]

    Value_527: Annotated[str, Field(default='0.0')]

    Value_528: Annotated[str, Field(default='0.0')]

    Value_529: Annotated[str, Field(default='0.0')]

    Value_530: Annotated[str, Field(default='0.0')]

    Value_531: Annotated[str, Field(default='0.0')]

    Value_532: Annotated[str, Field(default='0.0')]

    Value_533: Annotated[str, Field(default='0.0')]

    Value_534: Annotated[str, Field(default='0.0')]

    Value_535: Annotated[str, Field(default='0.0')]

    Value_536: Annotated[str, Field(default='0.0')]

    Value_537: Annotated[str, Field(default='0.0')]

    Value_538: Annotated[str, Field(default='0.0')]

    Value_539: Annotated[str, Field(default='0.0')]

    Value_540: Annotated[str, Field(default='0.0')]

    Value_541: Annotated[str, Field(default='0.0')]

    Value_542: Annotated[str, Field(default='0.0')]

    Value_543: Annotated[str, Field(default='0.0')]

    Value_544: Annotated[str, Field(default='0.0')]

    Value_545: Annotated[str, Field(default='0.0')]

    Value_546: Annotated[str, Field(default='0.0')]

    Value_547: Annotated[str, Field(default='0.0')]

    Value_548: Annotated[str, Field(default='0.0')]

    Value_549: Annotated[str, Field(default='0.0')]

    Value_550: Annotated[str, Field(default='0.0')]

    Value_551: Annotated[str, Field(default='0.0')]

    Value_552: Annotated[str, Field(default='0.0')]

    Value_553: Annotated[str, Field(default='0.0')]

    Value_554: Annotated[str, Field(default='0.0')]

    Value_555: Annotated[str, Field(default='0.0')]

    Value_556: Annotated[str, Field(default='0.0')]

    Value_557: Annotated[str, Field(default='0.0')]

    Value_558: Annotated[str, Field(default='0.0')]

    Value_559: Annotated[str, Field(default='0.0')]

    Value_560: Annotated[str, Field(default='0.0')]

    Value_561: Annotated[str, Field(default='0.0')]

    Value_562: Annotated[str, Field(default='0.0')]

    Value_563: Annotated[str, Field(default='0.0')]

    Value_564: Annotated[str, Field(default='0.0')]

    Value_565: Annotated[str, Field(default='0.0')]

    Value_566: Annotated[str, Field(default='0.0')]

    Value_567: Annotated[str, Field(default='0.0')]

    Value_568: Annotated[str, Field(default='0.0')]

    Value_569: Annotated[str, Field(default='0.0')]

    Value_570: Annotated[str, Field(default='0.0')]

    Value_571: Annotated[str, Field(default='0.0')]

    Value_572: Annotated[str, Field(default='0.0')]

    Value_573: Annotated[str, Field(default='0.0')]

    Value_574: Annotated[str, Field(default='0.0')]

    Value_575: Annotated[str, Field(default='0.0')]

    Value_576: Annotated[str, Field(default='0.0')]

    Value_577: Annotated[str, Field(default='0.0')]

    Value_578: Annotated[str, Field(default='0.0')]

    Value_579: Annotated[str, Field(default='0.0')]

    Value_580: Annotated[str, Field(default='0.0')]

    Value_581: Annotated[str, Field(default='0.0')]

    Value_582: Annotated[str, Field(default='0.0')]

    Value_583: Annotated[str, Field(default='0.0')]

    Value_584: Annotated[str, Field(default='0.0')]

    Value_585: Annotated[str, Field(default='0.0')]

    Value_586: Annotated[str, Field(default='0.0')]

    Value_587: Annotated[str, Field(default='0.0')]

    Value_588: Annotated[str, Field(default='0.0')]

    Value_589: Annotated[str, Field(default='0.0')]

    Value_590: Annotated[str, Field(default='0.0')]

    Value_591: Annotated[str, Field(default='0.0')]

    Value_592: Annotated[str, Field(default='0.0')]

    Value_593: Annotated[str, Field(default='0.0')]

    Value_594: Annotated[str, Field(default='0.0')]

    Value_595: Annotated[str, Field(default='0.0')]

    Value_596: Annotated[str, Field(default='0.0')]

    Value_597: Annotated[str, Field(default='0.0')]

    Value_598: Annotated[str, Field(default='0.0')]

    Value_599: Annotated[str, Field(default='0.0')]

    Value_600: Annotated[str, Field(default='0.0')]

    Value_601: Annotated[str, Field(default='0.0')]

    Value_602: Annotated[str, Field(default='0.0')]

    Value_603: Annotated[str, Field(default='0.0')]

    Value_604: Annotated[str, Field(default='0.0')]

    Value_605: Annotated[str, Field(default='0.0')]

    Value_606: Annotated[str, Field(default='0.0')]

    Value_607: Annotated[str, Field(default='0.0')]

    Value_608: Annotated[str, Field(default='0.0')]

    Value_609: Annotated[str, Field(default='0.0')]

    Value_610: Annotated[str, Field(default='0.0')]

    Value_611: Annotated[str, Field(default='0.0')]

    Value_612: Annotated[str, Field(default='0.0')]

    Value_613: Annotated[str, Field(default='0.0')]

    Value_614: Annotated[str, Field(default='0.0')]

    Value_615: Annotated[str, Field(default='0.0')]

    Value_616: Annotated[str, Field(default='0.0')]

    Value_617: Annotated[str, Field(default='0.0')]

    Value_618: Annotated[str, Field(default='0.0')]

    Value_619: Annotated[str, Field(default='0.0')]

    Value_620: Annotated[str, Field(default='0.0')]

    Value_621: Annotated[str, Field(default='0.0')]

    Value_622: Annotated[str, Field(default='0.0')]

    Value_623: Annotated[str, Field(default='0.0')]

    Value_624: Annotated[str, Field(default='0.0')]

    Value_625: Annotated[str, Field(default='0.0')]

    Value_626: Annotated[str, Field(default='0.0')]

    Value_627: Annotated[str, Field(default='0.0')]

    Value_628: Annotated[str, Field(default='0.0')]

    Value_629: Annotated[str, Field(default='0.0')]

    Value_630: Annotated[str, Field(default='0.0')]

    Value_631: Annotated[str, Field(default='0.0')]

    Value_632: Annotated[str, Field(default='0.0')]

    Value_633: Annotated[str, Field(default='0.0')]

    Value_634: Annotated[str, Field(default='0.0')]

    Value_635: Annotated[str, Field(default='0.0')]

    Value_636: Annotated[str, Field(default='0.0')]

    Value_637: Annotated[str, Field(default='0.0')]

    Value_638: Annotated[str, Field(default='0.0')]

    Value_639: Annotated[str, Field(default='0.0')]

    Value_640: Annotated[str, Field(default='0.0')]

    Value_641: Annotated[str, Field(default='0.0')]

    Value_642: Annotated[str, Field(default='0.0')]

    Value_643: Annotated[str, Field(default='0.0')]

    Value_644: Annotated[str, Field(default='0.0')]

    Value_645: Annotated[str, Field(default='0.0')]

    Value_646: Annotated[str, Field(default='0.0')]

    Value_647: Annotated[str, Field(default='0.0')]

    Value_648: Annotated[str, Field(default='0.0')]

    Value_649: Annotated[str, Field(default='0.0')]

    Value_650: Annotated[str, Field(default='0.0')]

    Value_651: Annotated[str, Field(default='0.0')]

    Value_652: Annotated[str, Field(default='0.0')]

    Value_653: Annotated[str, Field(default='0.0')]

    Value_654: Annotated[str, Field(default='0.0')]

    Value_655: Annotated[str, Field(default='0.0')]

    Value_656: Annotated[str, Field(default='0.0')]

    Value_657: Annotated[str, Field(default='0.0')]

    Value_658: Annotated[str, Field(default='0.0')]

    Value_659: Annotated[str, Field(default='0.0')]

    Value_660: Annotated[str, Field(default='0.0')]

    Value_661: Annotated[str, Field(default='0.0')]

    Value_662: Annotated[str, Field(default='0.0')]

    Value_663: Annotated[str, Field(default='0.0')]

    Value_664: Annotated[str, Field(default='0.0')]

    Value_665: Annotated[str, Field(default='0.0')]

    Value_666: Annotated[str, Field(default='0.0')]

    Value_667: Annotated[str, Field(default='0.0')]

    Value_668: Annotated[str, Field(default='0.0')]

    Value_669: Annotated[str, Field(default='0.0')]

    Value_670: Annotated[str, Field(default='0.0')]

    Value_671: Annotated[str, Field(default='0.0')]

    Value_672: Annotated[str, Field(default='0.0')]

    Value_673: Annotated[str, Field(default='0.0')]

    Value_674: Annotated[str, Field(default='0.0')]

    Value_675: Annotated[str, Field(default='0.0')]

    Value_676: Annotated[str, Field(default='0.0')]

    Value_677: Annotated[str, Field(default='0.0')]

    Value_678: Annotated[str, Field(default='0.0')]

    Value_679: Annotated[str, Field(default='0.0')]

    Value_680: Annotated[str, Field(default='0.0')]

    Value_681: Annotated[str, Field(default='0.0')]

    Value_682: Annotated[str, Field(default='0.0')]

    Value_683: Annotated[str, Field(default='0.0')]

    Value_684: Annotated[str, Field(default='0.0')]

    Value_685: Annotated[str, Field(default='0.0')]

    Value_686: Annotated[str, Field(default='0.0')]

    Value_687: Annotated[str, Field(default='0.0')]

    Value_688: Annotated[str, Field(default='0.0')]

    Value_689: Annotated[str, Field(default='0.0')]

    Value_690: Annotated[str, Field(default='0.0')]

    Value_691: Annotated[str, Field(default='0.0')]

    Value_692: Annotated[str, Field(default='0.0')]

    Value_693: Annotated[str, Field(default='0.0')]

    Value_694: Annotated[str, Field(default='0.0')]

    Value_695: Annotated[str, Field(default='0.0')]

    Value_696: Annotated[str, Field(default='0.0')]

    Value_697: Annotated[str, Field(default='0.0')]

    Value_698: Annotated[str, Field(default='0.0')]

    Value_699: Annotated[str, Field(default='0.0')]

    Value_700: Annotated[str, Field(default='0.0')]

    Value_701: Annotated[str, Field(default='0.0')]

    Value_702: Annotated[str, Field(default='0.0')]

    Value_703: Annotated[str, Field(default='0.0')]

    Value_704: Annotated[str, Field(default='0.0')]

    Value_705: Annotated[str, Field(default='0.0')]

    Value_706: Annotated[str, Field(default='0.0')]

    Value_707: Annotated[str, Field(default='0.0')]

    Value_708: Annotated[str, Field(default='0.0')]

    Value_709: Annotated[str, Field(default='0.0')]

    Value_710: Annotated[str, Field(default='0.0')]

    Value_711: Annotated[str, Field(default='0.0')]

    Value_712: Annotated[str, Field(default='0.0')]

    Value_713: Annotated[str, Field(default='0.0')]

    Value_714: Annotated[str, Field(default='0.0')]

    Value_715: Annotated[str, Field(default='0.0')]

    Value_716: Annotated[str, Field(default='0.0')]

    Value_717: Annotated[str, Field(default='0.0')]

    Value_718: Annotated[str, Field(default='0.0')]

    Value_719: Annotated[str, Field(default='0.0')]

    Value_720: Annotated[str, Field(default='0.0')]

    Value_721: Annotated[str, Field(default='0.0')]

    Value_722: Annotated[str, Field(default='0.0')]

    Value_723: Annotated[str, Field(default='0.0')]

    Value_724: Annotated[str, Field(default='0.0')]

    Value_725: Annotated[str, Field(default='0.0')]

    Value_726: Annotated[str, Field(default='0.0')]

    Value_727: Annotated[str, Field(default='0.0')]

    Value_728: Annotated[str, Field(default='0.0')]

    Value_729: Annotated[str, Field(default='0.0')]

    Value_730: Annotated[str, Field(default='0.0')]

    Value_731: Annotated[str, Field(default='0.0')]

    Value_732: Annotated[str, Field(default='0.0')]

    Value_733: Annotated[str, Field(default='0.0')]

    Value_734: Annotated[str, Field(default='0.0')]

    Value_735: Annotated[str, Field(default='0.0')]

    Value_736: Annotated[str, Field(default='0.0')]

    Value_737: Annotated[str, Field(default='0.0')]

    Value_738: Annotated[str, Field(default='0.0')]

    Value_739: Annotated[str, Field(default='0.0')]

    Value_740: Annotated[str, Field(default='0.0')]

    Value_741: Annotated[str, Field(default='0.0')]

    Value_742: Annotated[str, Field(default='0.0')]

    Value_743: Annotated[str, Field(default='0.0')]

    Value_744: Annotated[str, Field(default='0.0')]

    Value_745: Annotated[str, Field(default='0.0')]

    Value_746: Annotated[str, Field(default='0.0')]

    Value_747: Annotated[str, Field(default='0.0')]

    Value_748: Annotated[str, Field(default='0.0')]

    Value_749: Annotated[str, Field(default='0.0')]

    Value_750: Annotated[str, Field(default='0.0')]

    Value_751: Annotated[str, Field(default='0.0')]

    Value_752: Annotated[str, Field(default='0.0')]

    Value_753: Annotated[str, Field(default='0.0')]

    Value_754: Annotated[str, Field(default='0.0')]

    Value_755: Annotated[str, Field(default='0.0')]

    Value_756: Annotated[str, Field(default='0.0')]

    Value_757: Annotated[str, Field(default='0.0')]

    Value_758: Annotated[str, Field(default='0.0')]

    Value_759: Annotated[str, Field(default='0.0')]

    Value_760: Annotated[str, Field(default='0.0')]

    Value_761: Annotated[str, Field(default='0.0')]

    Value_762: Annotated[str, Field(default='0.0')]

    Value_763: Annotated[str, Field(default='0.0')]

    Value_764: Annotated[str, Field(default='0.0')]

    Value_765: Annotated[str, Field(default='0.0')]

    Value_766: Annotated[str, Field(default='0.0')]

    Value_767: Annotated[str, Field(default='0.0')]

    Value_768: Annotated[str, Field(default='0.0')]

    Value_769: Annotated[str, Field(default='0.0')]

    Value_770: Annotated[str, Field(default='0.0')]

    Value_771: Annotated[str, Field(default='0.0')]

    Value_772: Annotated[str, Field(default='0.0')]

    Value_773: Annotated[str, Field(default='0.0')]

    Value_774: Annotated[str, Field(default='0.0')]

    Value_775: Annotated[str, Field(default='0.0')]

    Value_776: Annotated[str, Field(default='0.0')]

    Value_777: Annotated[str, Field(default='0.0')]

    Value_778: Annotated[str, Field(default='0.0')]

    Value_779: Annotated[str, Field(default='0.0')]

    Value_780: Annotated[str, Field(default='0.0')]

    Value_781: Annotated[str, Field(default='0.0')]

    Value_782: Annotated[str, Field(default='0.0')]

    Value_783: Annotated[str, Field(default='0.0')]

    Value_784: Annotated[str, Field(default='0.0')]

    Value_785: Annotated[str, Field(default='0.0')]

    Value_786: Annotated[str, Field(default='0.0')]

    Value_787: Annotated[str, Field(default='0.0')]

    Value_788: Annotated[str, Field(default='0.0')]

    Value_789: Annotated[str, Field(default='0.0')]

    Value_790: Annotated[str, Field(default='0.0')]

    Value_791: Annotated[str, Field(default='0.0')]

    Value_792: Annotated[str, Field(default='0.0')]

    Value_793: Annotated[str, Field(default='0.0')]

    Value_794: Annotated[str, Field(default='0.0')]

    Value_795: Annotated[str, Field(default='0.0')]

    Value_796: Annotated[str, Field(default='0.0')]

    Value_797: Annotated[str, Field(default='0.0')]

    Value_798: Annotated[str, Field(default='0.0')]

    Value_799: Annotated[str, Field(default='0.0')]

    Value_800: Annotated[str, Field(default='0.0')]

    Value_801: Annotated[str, Field(default='0.0')]

    Value_802: Annotated[str, Field(default='0.0')]

    Value_803: Annotated[str, Field(default='0.0')]

    Value_804: Annotated[str, Field(default='0.0')]

    Value_805: Annotated[str, Field(default='0.0')]

    Value_806: Annotated[str, Field(default='0.0')]

    Value_807: Annotated[str, Field(default='0.0')]

    Value_808: Annotated[str, Field(default='0.0')]

    Value_809: Annotated[str, Field(default='0.0')]

    Value_810: Annotated[str, Field(default='0.0')]

    Value_811: Annotated[str, Field(default='0.0')]

    Value_812: Annotated[str, Field(default='0.0')]

    Value_813: Annotated[str, Field(default='0.0')]

    Value_814: Annotated[str, Field(default='0.0')]

    Value_815: Annotated[str, Field(default='0.0')]

    Value_816: Annotated[str, Field(default='0.0')]

    Value_817: Annotated[str, Field(default='0.0')]

    Value_818: Annotated[str, Field(default='0.0')]

    Value_819: Annotated[str, Field(default='0.0')]

    Value_820: Annotated[str, Field(default='0.0')]

    Value_821: Annotated[str, Field(default='0.0')]

    Value_822: Annotated[str, Field(default='0.0')]

    Value_823: Annotated[str, Field(default='0.0')]

    Value_824: Annotated[str, Field(default='0.0')]

    Value_825: Annotated[str, Field(default='0.0')]

    Value_826: Annotated[str, Field(default='0.0')]

    Value_827: Annotated[str, Field(default='0.0')]

    Value_828: Annotated[str, Field(default='0.0')]

    Value_829: Annotated[str, Field(default='0.0')]

    Value_830: Annotated[str, Field(default='0.0')]

    Value_831: Annotated[str, Field(default='0.0')]

    Value_832: Annotated[str, Field(default='0.0')]

    Value_833: Annotated[str, Field(default='0.0')]

    Value_834: Annotated[str, Field(default='0.0')]

    Value_835: Annotated[str, Field(default='0.0')]

    Value_836: Annotated[str, Field(default='0.0')]

    Value_837: Annotated[str, Field(default='0.0')]

    Value_838: Annotated[str, Field(default='0.0')]

    Value_839: Annotated[str, Field(default='0.0')]

    Value_840: Annotated[str, Field(default='0.0')]

    Value_841: Annotated[str, Field(default='0.0')]

    Value_842: Annotated[str, Field(default='0.0')]

    Value_843: Annotated[str, Field(default='0.0')]

    Value_844: Annotated[str, Field(default='0.0')]

    Value_845: Annotated[str, Field(default='0.0')]

    Value_846: Annotated[str, Field(default='0.0')]

    Value_847: Annotated[str, Field(default='0.0')]

    Value_848: Annotated[str, Field(default='0.0')]

    Value_849: Annotated[str, Field(default='0.0')]

    Value_850: Annotated[str, Field(default='0.0')]

    Value_851: Annotated[str, Field(default='0.0')]

    Value_852: Annotated[str, Field(default='0.0')]

    Value_853: Annotated[str, Field(default='0.0')]

    Value_854: Annotated[str, Field(default='0.0')]

    Value_855: Annotated[str, Field(default='0.0')]

    Value_856: Annotated[str, Field(default='0.0')]

    Value_857: Annotated[str, Field(default='0.0')]

    Value_858: Annotated[str, Field(default='0.0')]

    Value_859: Annotated[str, Field(default='0.0')]

    Value_860: Annotated[str, Field(default='0.0')]

    Value_861: Annotated[str, Field(default='0.0')]

    Value_862: Annotated[str, Field(default='0.0')]

    Value_863: Annotated[str, Field(default='0.0')]

    Value_864: Annotated[str, Field(default='0.0')]

    Value_865: Annotated[str, Field(default='0.0')]

    Value_866: Annotated[str, Field(default='0.0')]

    Value_867: Annotated[str, Field(default='0.0')]

    Value_868: Annotated[str, Field(default='0.0')]

    Value_869: Annotated[str, Field(default='0.0')]

    Value_870: Annotated[str, Field(default='0.0')]

    Value_871: Annotated[str, Field(default='0.0')]

    Value_872: Annotated[str, Field(default='0.0')]

    Value_873: Annotated[str, Field(default='0.0')]

    Value_874: Annotated[str, Field(default='0.0')]

    Value_875: Annotated[str, Field(default='0.0')]

    Value_876: Annotated[str, Field(default='0.0')]

    Value_877: Annotated[str, Field(default='0.0')]

    Value_878: Annotated[str, Field(default='0.0')]

    Value_879: Annotated[str, Field(default='0.0')]

    Value_880: Annotated[str, Field(default='0.0')]

    Value_881: Annotated[str, Field(default='0.0')]

    Value_882: Annotated[str, Field(default='0.0')]

    Value_883: Annotated[str, Field(default='0.0')]

    Value_884: Annotated[str, Field(default='0.0')]

    Value_885: Annotated[str, Field(default='0.0')]

    Value_886: Annotated[str, Field(default='0.0')]

    Value_887: Annotated[str, Field(default='0.0')]

    Value_888: Annotated[str, Field(default='0.0')]

    Value_889: Annotated[str, Field(default='0.0')]

    Value_890: Annotated[str, Field(default='0.0')]

    Value_891: Annotated[str, Field(default='0.0')]

    Value_892: Annotated[str, Field(default='0.0')]

    Value_893: Annotated[str, Field(default='0.0')]

    Value_894: Annotated[str, Field(default='0.0')]

    Value_895: Annotated[str, Field(default='0.0')]

    Value_896: Annotated[str, Field(default='0.0')]

    Value_897: Annotated[str, Field(default='0.0')]

    Value_898: Annotated[str, Field(default='0.0')]

    Value_899: Annotated[str, Field(default='0.0')]

    Value_900: Annotated[str, Field(default='0.0')]

    Value_901: Annotated[str, Field(default='0.0')]

    Value_902: Annotated[str, Field(default='0.0')]

    Value_903: Annotated[str, Field(default='0.0')]

    Value_904: Annotated[str, Field(default='0.0')]

    Value_905: Annotated[str, Field(default='0.0')]

    Value_906: Annotated[str, Field(default='0.0')]

    Value_907: Annotated[str, Field(default='0.0')]

    Value_908: Annotated[str, Field(default='0.0')]

    Value_909: Annotated[str, Field(default='0.0')]

    Value_910: Annotated[str, Field(default='0.0')]

    Value_911: Annotated[str, Field(default='0.0')]

    Value_912: Annotated[str, Field(default='0.0')]

    Value_913: Annotated[str, Field(default='0.0')]

    Value_914: Annotated[str, Field(default='0.0')]

    Value_915: Annotated[str, Field(default='0.0')]

    Value_916: Annotated[str, Field(default='0.0')]

    Value_917: Annotated[str, Field(default='0.0')]

    Value_918: Annotated[str, Field(default='0.0')]

    Value_919: Annotated[str, Field(default='0.0')]

    Value_920: Annotated[str, Field(default='0.0')]

    Value_921: Annotated[str, Field(default='0.0')]

    Value_922: Annotated[str, Field(default='0.0')]

    Value_923: Annotated[str, Field(default='0.0')]

    Value_924: Annotated[str, Field(default='0.0')]

    Value_925: Annotated[str, Field(default='0.0')]

    Value_926: Annotated[str, Field(default='0.0')]

    Value_927: Annotated[str, Field(default='0.0')]

    Value_928: Annotated[str, Field(default='0.0')]

    Value_929: Annotated[str, Field(default='0.0')]

    Value_930: Annotated[str, Field(default='0.0')]

    Value_931: Annotated[str, Field(default='0.0')]

    Value_932: Annotated[str, Field(default='0.0')]

    Value_933: Annotated[str, Field(default='0.0')]

    Value_934: Annotated[str, Field(default='0.0')]

    Value_935: Annotated[str, Field(default='0.0')]

    Value_936: Annotated[str, Field(default='0.0')]

    Value_937: Annotated[str, Field(default='0.0')]

    Value_938: Annotated[str, Field(default='0.0')]

    Value_939: Annotated[str, Field(default='0.0')]

    Value_940: Annotated[str, Field(default='0.0')]

    Value_941: Annotated[str, Field(default='0.0')]

    Value_942: Annotated[str, Field(default='0.0')]

    Value_943: Annotated[str, Field(default='0.0')]

    Value_944: Annotated[str, Field(default='0.0')]

    Value_945: Annotated[str, Field(default='0.0')]

    Value_946: Annotated[str, Field(default='0.0')]

    Value_947: Annotated[str, Field(default='0.0')]

    Value_948: Annotated[str, Field(default='0.0')]

    Value_949: Annotated[str, Field(default='0.0')]

    Value_950: Annotated[str, Field(default='0.0')]

    Value_951: Annotated[str, Field(default='0.0')]

    Value_952: Annotated[str, Field(default='0.0')]

    Value_953: Annotated[str, Field(default='0.0')]

    Value_954: Annotated[str, Field(default='0.0')]

    Value_955: Annotated[str, Field(default='0.0')]

    Value_956: Annotated[str, Field(default='0.0')]

    Value_957: Annotated[str, Field(default='0.0')]

    Value_958: Annotated[str, Field(default='0.0')]

    Value_959: Annotated[str, Field(default='0.0')]

    Value_960: Annotated[str, Field(default='0.0')]

    Value_961: Annotated[str, Field(default='0.0')]

    Value_962: Annotated[str, Field(default='0.0')]

    Value_963: Annotated[str, Field(default='0.0')]

    Value_964: Annotated[str, Field(default='0.0')]

    Value_965: Annotated[str, Field(default='0.0')]

    Value_966: Annotated[str, Field(default='0.0')]

    Value_967: Annotated[str, Field(default='0.0')]

    Value_968: Annotated[str, Field(default='0.0')]

    Value_969: Annotated[str, Field(default='0.0')]

    Value_970: Annotated[str, Field(default='0.0')]

    Value_971: Annotated[str, Field(default='0.0')]

    Value_972: Annotated[str, Field(default='0.0')]

    Value_973: Annotated[str, Field(default='0.0')]

    Value_974: Annotated[str, Field(default='0.0')]

    Value_975: Annotated[str, Field(default='0.0')]

    Value_976: Annotated[str, Field(default='0.0')]

    Value_977: Annotated[str, Field(default='0.0')]

    Value_978: Annotated[str, Field(default='0.0')]

    Value_979: Annotated[str, Field(default='0.0')]

    Value_980: Annotated[str, Field(default='0.0')]

    Value_981: Annotated[str, Field(default='0.0')]

    Value_982: Annotated[str, Field(default='0.0')]

    Value_983: Annotated[str, Field(default='0.0')]

    Value_984: Annotated[str, Field(default='0.0')]

    Value_985: Annotated[str, Field(default='0.0')]

    Value_986: Annotated[str, Field(default='0.0')]

    Value_987: Annotated[str, Field(default='0.0')]

    Value_988: Annotated[str, Field(default='0.0')]

    Value_989: Annotated[str, Field(default='0.0')]

    Value_990: Annotated[str, Field(default='0.0')]

    Value_991: Annotated[str, Field(default='0.0')]

    Value_992: Annotated[str, Field(default='0.0')]

    Value_993: Annotated[str, Field(default='0.0')]

    Value_994: Annotated[str, Field(default='0.0')]

    Value_995: Annotated[str, Field(default='0.0')]

    Value_996: Annotated[str, Field(default='0.0')]

    Value_997: Annotated[str, Field(default='0.0')]

    Value_998: Annotated[str, Field(default='0.0')]

    Value_999: Annotated[str, Field(default='0.0')]

    Value_1000: Annotated[str, Field(default='0.0')]

    Value_1001: Annotated[str, Field(default='0.0')]

    Value_1002: Annotated[str, Field(default='0.0')]

    Value_1003: Annotated[str, Field(default='0.0')]

    Value_1004: Annotated[str, Field(default='0.0')]

    Value_1005: Annotated[str, Field(default='0.0')]

    Value_1006: Annotated[str, Field(default='0.0')]

    Value_1007: Annotated[str, Field(default='0.0')]

    Value_1008: Annotated[str, Field(default='0.0')]

    Value_1009: Annotated[str, Field(default='0.0')]

    Value_1010: Annotated[str, Field(default='0.0')]

    Value_1011: Annotated[str, Field(default='0.0')]

    Value_1012: Annotated[str, Field(default='0.0')]

    Value_1013: Annotated[str, Field(default='0.0')]

    Value_1014: Annotated[str, Field(default='0.0')]

    Value_1015: Annotated[str, Field(default='0.0')]

    Value_1016: Annotated[str, Field(default='0.0')]

    Value_1017: Annotated[str, Field(default='0.0')]

    Value_1018: Annotated[str, Field(default='0.0')]

    Value_1019: Annotated[str, Field(default='0.0')]

    Value_1020: Annotated[str, Field(default='0.0')]

    Value_1021: Annotated[str, Field(default='0.0')]

    Value_1022: Annotated[str, Field(default='0.0')]

    Value_1023: Annotated[str, Field(default='0.0')]

    Value_1024: Annotated[str, Field(default='0.0')]

    Value_1025: Annotated[str, Field(default='0.0')]

    Value_1026: Annotated[str, Field(default='0.0')]

    Value_1027: Annotated[str, Field(default='0.0')]

    Value_1028: Annotated[str, Field(default='0.0')]

    Value_1029: Annotated[str, Field(default='0.0')]

    Value_1030: Annotated[str, Field(default='0.0')]

    Value_1031: Annotated[str, Field(default='0.0')]

    Value_1032: Annotated[str, Field(default='0.0')]

    Value_1033: Annotated[str, Field(default='0.0')]

    Value_1034: Annotated[str, Field(default='0.0')]

    Value_1035: Annotated[str, Field(default='0.0')]

    Value_1036: Annotated[str, Field(default='0.0')]

    Value_1037: Annotated[str, Field(default='0.0')]

    Value_1038: Annotated[str, Field(default='0.0')]

    Value_1039: Annotated[str, Field(default='0.0')]

    Value_1040: Annotated[str, Field(default='0.0')]

    Value_1041: Annotated[str, Field(default='0.0')]

    Value_1042: Annotated[str, Field(default='0.0')]

    Value_1043: Annotated[str, Field(default='0.0')]

    Value_1044: Annotated[str, Field(default='0.0')]

    Value_1045: Annotated[str, Field(default='0.0')]

    Value_1046: Annotated[str, Field(default='0.0')]

    Value_1047: Annotated[str, Field(default='0.0')]

    Value_1048: Annotated[str, Field(default='0.0')]

    Value_1049: Annotated[str, Field(default='0.0')]

    Value_1050: Annotated[str, Field(default='0.0')]

    Value_1051: Annotated[str, Field(default='0.0')]

    Value_1052: Annotated[str, Field(default='0.0')]

    Value_1053: Annotated[str, Field(default='0.0')]

    Value_1054: Annotated[str, Field(default='0.0')]

    Value_1055: Annotated[str, Field(default='0.0')]

    Value_1056: Annotated[str, Field(default='0.0')]

    Value_1057: Annotated[str, Field(default='0.0')]

    Value_1058: Annotated[str, Field(default='0.0')]

    Value_1059: Annotated[str, Field(default='0.0')]

    Value_1060: Annotated[str, Field(default='0.0')]

    Value_1061: Annotated[str, Field(default='0.0')]

    Value_1062: Annotated[str, Field(default='0.0')]

    Value_1063: Annotated[str, Field(default='0.0')]

    Value_1064: Annotated[str, Field(default='0.0')]

    Value_1065: Annotated[str, Field(default='0.0')]

    Value_1066: Annotated[str, Field(default='0.0')]

    Value_1067: Annotated[str, Field(default='0.0')]

    Value_1068: Annotated[str, Field(default='0.0')]

    Value_1069: Annotated[str, Field(default='0.0')]

    Value_1070: Annotated[str, Field(default='0.0')]

    Value_1071: Annotated[str, Field(default='0.0')]

    Value_1072: Annotated[str, Field(default='0.0')]

    Value_1073: Annotated[str, Field(default='0.0')]

    Value_1074: Annotated[str, Field(default='0.0')]

    Value_1075: Annotated[str, Field(default='0.0')]

    Value_1076: Annotated[str, Field(default='0.0')]

    Value_1077: Annotated[str, Field(default='0.0')]

    Value_1078: Annotated[str, Field(default='0.0')]

    Value_1079: Annotated[str, Field(default='0.0')]

    Value_1080: Annotated[str, Field(default='0.0')]

    Value_1081: Annotated[str, Field(default='0.0')]

    Value_1082: Annotated[str, Field(default='0.0')]

    Value_1083: Annotated[str, Field(default='0.0')]

    Value_1084: Annotated[str, Field(default='0.0')]

    Value_1085: Annotated[str, Field(default='0.0')]

    Value_1086: Annotated[str, Field(default='0.0')]

    Value_1087: Annotated[str, Field(default='0.0')]

    Value_1088: Annotated[str, Field(default='0.0')]

    Value_1089: Annotated[str, Field(default='0.0')]

    Value_1090: Annotated[str, Field(default='0.0')]

    Value_1091: Annotated[str, Field(default='0.0')]

    Value_1092: Annotated[str, Field(default='0.0')]

    Value_1093: Annotated[str, Field(default='0.0')]

    Value_1094: Annotated[str, Field(default='0.0')]

    Value_1095: Annotated[str, Field(default='0.0')]

    Value_1096: Annotated[str, Field(default='0.0')]

    Value_1097: Annotated[str, Field(default='0.0')]

    Value_1098: Annotated[str, Field(default='0.0')]

    Value_1099: Annotated[str, Field(default='0.0')]

    Value_1100: Annotated[str, Field(default='0.0')]

    Value_1101: Annotated[str, Field(default='0.0')]

    Value_1102: Annotated[str, Field(default='0.0')]

    Value_1103: Annotated[str, Field(default='0.0')]

    Value_1104: Annotated[str, Field(default='0.0')]

    Value_1105: Annotated[str, Field(default='0.0')]

    Value_1106: Annotated[str, Field(default='0.0')]

    Value_1107: Annotated[str, Field(default='0.0')]

    Value_1108: Annotated[str, Field(default='0.0')]

    Value_1109: Annotated[str, Field(default='0.0')]

    Value_1110: Annotated[str, Field(default='0.0')]

    Value_1111: Annotated[str, Field(default='0.0')]

    Value_1112: Annotated[str, Field(default='0.0')]

    Value_1113: Annotated[str, Field(default='0.0')]

    Value_1114: Annotated[str, Field(default='0.0')]

    Value_1115: Annotated[str, Field(default='0.0')]

    Value_1116: Annotated[str, Field(default='0.0')]

    Value_1117: Annotated[str, Field(default='0.0')]

    Value_1118: Annotated[str, Field(default='0.0')]

    Value_1119: Annotated[str, Field(default='0.0')]

    Value_1120: Annotated[str, Field(default='0.0')]

    Value_1121: Annotated[str, Field(default='0.0')]

    Value_1122: Annotated[str, Field(default='0.0')]

    Value_1123: Annotated[str, Field(default='0.0')]

    Value_1124: Annotated[str, Field(default='0.0')]

    Value_1125: Annotated[str, Field(default='0.0')]

    Value_1126: Annotated[str, Field(default='0.0')]

    Value_1127: Annotated[str, Field(default='0.0')]

    Value_1128: Annotated[str, Field(default='0.0')]

    Value_1129: Annotated[str, Field(default='0.0')]

    Value_1130: Annotated[str, Field(default='0.0')]

    Value_1131: Annotated[str, Field(default='0.0')]

    Value_1132: Annotated[str, Field(default='0.0')]

    Value_1133: Annotated[str, Field(default='0.0')]

    Value_1134: Annotated[str, Field(default='0.0')]

    Value_1135: Annotated[str, Field(default='0.0')]

    Value_1136: Annotated[str, Field(default='0.0')]

    Value_1137: Annotated[str, Field(default='0.0')]

    Value_1138: Annotated[str, Field(default='0.0')]

    Value_1139: Annotated[str, Field(default='0.0')]

    Value_1140: Annotated[str, Field(default='0.0')]

    Value_1141: Annotated[str, Field(default='0.0')]

    Value_1142: Annotated[str, Field(default='0.0')]

    Value_1143: Annotated[str, Field(default='0.0')]

    Value_1144: Annotated[str, Field(default='0.0')]

    Value_1145: Annotated[str, Field(default='0.0')]

    Value_1146: Annotated[str, Field(default='0.0')]

    Value_1147: Annotated[str, Field(default='0.0')]

    Value_1148: Annotated[str, Field(default='0.0')]

    Value_1149: Annotated[str, Field(default='0.0')]

    Value_1150: Annotated[str, Field(default='0.0')]

    Value_1151: Annotated[str, Field(default='0.0')]

    Value_1152: Annotated[str, Field(default='0.0')]

    Value_1153: Annotated[str, Field(default='0.0')]

    Value_1154: Annotated[str, Field(default='0.0')]

    Value_1155: Annotated[str, Field(default='0.0')]

    Value_1156: Annotated[str, Field(default='0.0')]

    Value_1157: Annotated[str, Field(default='0.0')]

    Value_1158: Annotated[str, Field(default='0.0')]

    Value_1159: Annotated[str, Field(default='0.0')]

    Value_1160: Annotated[str, Field(default='0.0')]

    Value_1161: Annotated[str, Field(default='0.0')]

    Value_1162: Annotated[str, Field(default='0.0')]

    Value_1163: Annotated[str, Field(default='0.0')]

    Value_1164: Annotated[str, Field(default='0.0')]

    Value_1165: Annotated[str, Field(default='0.0')]

    Value_1166: Annotated[str, Field(default='0.0')]

    Value_1167: Annotated[str, Field(default='0.0')]

    Value_1168: Annotated[str, Field(default='0.0')]

    Value_1169: Annotated[str, Field(default='0.0')]

    Value_1170: Annotated[str, Field(default='0.0')]

    Value_1171: Annotated[str, Field(default='0.0')]

    Value_1172: Annotated[str, Field(default='0.0')]

    Value_1173: Annotated[str, Field(default='0.0')]

    Value_1174: Annotated[str, Field(default='0.0')]

    Value_1175: Annotated[str, Field(default='0.0')]

    Value_1176: Annotated[str, Field(default='0.0')]

    Value_1177: Annotated[str, Field(default='0.0')]

    Value_1178: Annotated[str, Field(default='0.0')]

    Value_1179: Annotated[str, Field(default='0.0')]

    Value_1180: Annotated[str, Field(default='0.0')]

    Value_1181: Annotated[str, Field(default='0.0')]

    Value_1182: Annotated[str, Field(default='0.0')]

    Value_1183: Annotated[str, Field(default='0.0')]

    Value_1184: Annotated[str, Field(default='0.0')]

    Value_1185: Annotated[str, Field(default='0.0')]

    Value_1186: Annotated[str, Field(default='0.0')]

    Value_1187: Annotated[str, Field(default='0.0')]

    Value_1188: Annotated[str, Field(default='0.0')]

    Value_1189: Annotated[str, Field(default='0.0')]

    Value_1190: Annotated[str, Field(default='0.0')]

    Value_1191: Annotated[str, Field(default='0.0')]

    Value_1192: Annotated[str, Field(default='0.0')]

    Value_1193: Annotated[str, Field(default='0.0')]

    Value_1194: Annotated[str, Field(default='0.0')]

    Value_1195: Annotated[str, Field(default='0.0')]

    Value_1196: Annotated[str, Field(default='0.0')]

    Value_1197: Annotated[str, Field(default='0.0')]

    Value_1198: Annotated[str, Field(default='0.0')]

    Value_1199: Annotated[str, Field(default='0.0')]

    Value_1200: Annotated[str, Field(default='0.0')]

    Value_1201: Annotated[str, Field(default='0.0')]

    Value_1202: Annotated[str, Field(default='0.0')]

    Value_1203: Annotated[str, Field(default='0.0')]

    Value_1204: Annotated[str, Field(default='0.0')]

    Value_1205: Annotated[str, Field(default='0.0')]

    Value_1206: Annotated[str, Field(default='0.0')]

    Value_1207: Annotated[str, Field(default='0.0')]

    Value_1208: Annotated[str, Field(default='0.0')]

    Value_1209: Annotated[str, Field(default='0.0')]

    Value_1210: Annotated[str, Field(default='0.0')]

    Value_1211: Annotated[str, Field(default='0.0')]

    Value_1212: Annotated[str, Field(default='0.0')]

    Value_1213: Annotated[str, Field(default='0.0')]

    Value_1214: Annotated[str, Field(default='0.0')]

    Value_1215: Annotated[str, Field(default='0.0')]

    Value_1216: Annotated[str, Field(default='0.0')]

    Value_1217: Annotated[str, Field(default='0.0')]

    Value_1218: Annotated[str, Field(default='0.0')]

    Value_1219: Annotated[str, Field(default='0.0')]

    Value_1220: Annotated[str, Field(default='0.0')]

    Value_1221: Annotated[str, Field(default='0.0')]

    Value_1222: Annotated[str, Field(default='0.0')]

    Value_1223: Annotated[str, Field(default='0.0')]

    Value_1224: Annotated[str, Field(default='0.0')]

    Value_1225: Annotated[str, Field(default='0.0')]

    Value_1226: Annotated[str, Field(default='0.0')]

    Value_1227: Annotated[str, Field(default='0.0')]

    Value_1228: Annotated[str, Field(default='0.0')]

    Value_1229: Annotated[str, Field(default='0.0')]

    Value_1230: Annotated[str, Field(default='0.0')]

    Value_1231: Annotated[str, Field(default='0.0')]

    Value_1232: Annotated[str, Field(default='0.0')]

    Value_1233: Annotated[str, Field(default='0.0')]

    Value_1234: Annotated[str, Field(default='0.0')]

    Value_1235: Annotated[str, Field(default='0.0')]

    Value_1236: Annotated[str, Field(default='0.0')]

    Value_1237: Annotated[str, Field(default='0.0')]

    Value_1238: Annotated[str, Field(default='0.0')]

    Value_1239: Annotated[str, Field(default='0.0')]

    Value_1240: Annotated[str, Field(default='0.0')]

    Value_1241: Annotated[str, Field(default='0.0')]

    Value_1242: Annotated[str, Field(default='0.0')]

    Value_1243: Annotated[str, Field(default='0.0')]

    Value_1244: Annotated[str, Field(default='0.0')]

    Value_1245: Annotated[str, Field(default='0.0')]

    Value_1246: Annotated[str, Field(default='0.0')]

    Value_1247: Annotated[str, Field(default='0.0')]

    Value_1248: Annotated[str, Field(default='0.0')]

    Value_1249: Annotated[str, Field(default='0.0')]

    Value_1250: Annotated[str, Field(default='0.0')]

    Value_1251: Annotated[str, Field(default='0.0')]

    Value_1252: Annotated[str, Field(default='0.0')]

    Value_1253: Annotated[str, Field(default='0.0')]

    Value_1254: Annotated[str, Field(default='0.0')]

    Value_1255: Annotated[str, Field(default='0.0')]

    Value_1256: Annotated[str, Field(default='0.0')]

    Value_1257: Annotated[str, Field(default='0.0')]

    Value_1258: Annotated[str, Field(default='0.0')]

    Value_1259: Annotated[str, Field(default='0.0')]

    Value_1260: Annotated[str, Field(default='0.0')]

    Value_1261: Annotated[str, Field(default='0.0')]

    Value_1262: Annotated[str, Field(default='0.0')]

    Value_1263: Annotated[str, Field(default='0.0')]

    Value_1264: Annotated[str, Field(default='0.0')]

    Value_1265: Annotated[str, Field(default='0.0')]

    Value_1266: Annotated[str, Field(default='0.0')]

    Value_1267: Annotated[str, Field(default='0.0')]

    Value_1268: Annotated[str, Field(default='0.0')]

    Value_1269: Annotated[str, Field(default='0.0')]

    Value_1270: Annotated[str, Field(default='0.0')]

    Value_1271: Annotated[str, Field(default='0.0')]

    Value_1272: Annotated[str, Field(default='0.0')]

    Value_1273: Annotated[str, Field(default='0.0')]

    Value_1274: Annotated[str, Field(default='0.0')]

    Value_1275: Annotated[str, Field(default='0.0')]

    Value_1276: Annotated[str, Field(default='0.0')]

    Value_1277: Annotated[str, Field(default='0.0')]

    Value_1278: Annotated[str, Field(default='0.0')]

    Value_1279: Annotated[str, Field(default='0.0')]

    Value_1280: Annotated[str, Field(default='0.0')]

    Value_1281: Annotated[str, Field(default='0.0')]

    Value_1282: Annotated[str, Field(default='0.0')]

    Value_1283: Annotated[str, Field(default='0.0')]

    Value_1284: Annotated[str, Field(default='0.0')]

    Value_1285: Annotated[str, Field(default='0.0')]

    Value_1286: Annotated[str, Field(default='0.0')]

    Value_1287: Annotated[str, Field(default='0.0')]

    Value_1288: Annotated[str, Field(default='0.0')]

    Value_1289: Annotated[str, Field(default='0.0')]

    Value_1290: Annotated[str, Field(default='0.0')]

    Value_1291: Annotated[str, Field(default='0.0')]

    Value_1292: Annotated[str, Field(default='0.0')]

    Value_1293: Annotated[str, Field(default='0.0')]

    Value_1294: Annotated[str, Field(default='0.0')]

    Value_1295: Annotated[str, Field(default='0.0')]

    Value_1296: Annotated[str, Field(default='0.0')]

    Value_1297: Annotated[str, Field(default='0.0')]

    Value_1298: Annotated[str, Field(default='0.0')]

    Value_1299: Annotated[str, Field(default='0.0')]

    Value_1300: Annotated[str, Field(default='0.0')]

    Value_1301: Annotated[str, Field(default='0.0')]

    Value_1302: Annotated[str, Field(default='0.0')]

    Value_1303: Annotated[str, Field(default='0.0')]

    Value_1304: Annotated[str, Field(default='0.0')]

    Value_1305: Annotated[str, Field(default='0.0')]

    Value_1306: Annotated[str, Field(default='0.0')]

    Value_1307: Annotated[str, Field(default='0.0')]

    Value_1308: Annotated[str, Field(default='0.0')]

    Value_1309: Annotated[str, Field(default='0.0')]

    Value_1310: Annotated[str, Field(default='0.0')]

    Value_1311: Annotated[str, Field(default='0.0')]

    Value_1312: Annotated[str, Field(default='0.0')]

    Value_1313: Annotated[str, Field(default='0.0')]

    Value_1314: Annotated[str, Field(default='0.0')]

    Value_1315: Annotated[str, Field(default='0.0')]

    Value_1316: Annotated[str, Field(default='0.0')]

    Value_1317: Annotated[str, Field(default='0.0')]

    Value_1318: Annotated[str, Field(default='0.0')]

    Value_1319: Annotated[str, Field(default='0.0')]

    Value_1320: Annotated[str, Field(default='0.0')]

    Value_1321: Annotated[str, Field(default='0.0')]

    Value_1322: Annotated[str, Field(default='0.0')]

    Value_1323: Annotated[str, Field(default='0.0')]

    Value_1324: Annotated[str, Field(default='0.0')]

    Value_1325: Annotated[str, Field(default='0.0')]

    Value_1326: Annotated[str, Field(default='0.0')]

    Value_1327: Annotated[str, Field(default='0.0')]

    Value_1328: Annotated[str, Field(default='0.0')]

    Value_1329: Annotated[str, Field(default='0.0')]

    Value_1330: Annotated[str, Field(default='0.0')]

    Value_1331: Annotated[str, Field(default='0.0')]

    Value_1332: Annotated[str, Field(default='0.0')]

    Value_1333: Annotated[str, Field(default='0.0')]

    Value_1334: Annotated[str, Field(default='0.0')]

    Value_1335: Annotated[str, Field(default='0.0')]

    Value_1336: Annotated[str, Field(default='0.0')]

    Value_1337: Annotated[str, Field(default='0.0')]

    Value_1338: Annotated[str, Field(default='0.0')]

    Value_1339: Annotated[str, Field(default='0.0')]

    Value_1340: Annotated[str, Field(default='0.0')]

    Value_1341: Annotated[str, Field(default='0.0')]

    Value_1342: Annotated[str, Field(default='0.0')]

    Value_1343: Annotated[str, Field(default='0.0')]

    Value_1344: Annotated[str, Field(default='0.0')]

    Value_1345: Annotated[str, Field(default='0.0')]

    Value_1346: Annotated[str, Field(default='0.0')]

    Value_1347: Annotated[str, Field(default='0.0')]

    Value_1348: Annotated[str, Field(default='0.0')]

    Value_1349: Annotated[str, Field(default='0.0')]

    Value_1350: Annotated[str, Field(default='0.0')]

    Value_1351: Annotated[str, Field(default='0.0')]

    Value_1352: Annotated[str, Field(default='0.0')]

    Value_1353: Annotated[str, Field(default='0.0')]

    Value_1354: Annotated[str, Field(default='0.0')]

    Value_1355: Annotated[str, Field(default='0.0')]

    Value_1356: Annotated[str, Field(default='0.0')]

    Value_1357: Annotated[str, Field(default='0.0')]

    Value_1358: Annotated[str, Field(default='0.0')]

    Value_1359: Annotated[str, Field(default='0.0')]

    Value_1360: Annotated[str, Field(default='0.0')]

    Value_1361: Annotated[str, Field(default='0.0')]

    Value_1362: Annotated[str, Field(default='0.0')]

    Value_1363: Annotated[str, Field(default='0.0')]

    Value_1364: Annotated[str, Field(default='0.0')]

    Value_1365: Annotated[str, Field(default='0.0')]

    Value_1366: Annotated[str, Field(default='0.0')]

    Value_1367: Annotated[str, Field(default='0.0')]

    Value_1368: Annotated[str, Field(default='0.0')]

    Value_1369: Annotated[str, Field(default='0.0')]

    Value_1370: Annotated[str, Field(default='0.0')]

    Value_1371: Annotated[str, Field(default='0.0')]

    Value_1372: Annotated[str, Field(default='0.0')]

    Value_1373: Annotated[str, Field(default='0.0')]

    Value_1374: Annotated[str, Field(default='0.0')]

    Value_1375: Annotated[str, Field(default='0.0')]

    Value_1376: Annotated[str, Field(default='0.0')]

    Value_1377: Annotated[str, Field(default='0.0')]

    Value_1378: Annotated[str, Field(default='0.0')]

    Value_1379: Annotated[str, Field(default='0.0')]

    Value_1380: Annotated[str, Field(default='0.0')]

    Value_1381: Annotated[str, Field(default='0.0')]

    Value_1382: Annotated[str, Field(default='0.0')]

    Value_1383: Annotated[str, Field(default='0.0')]

    Value_1384: Annotated[str, Field(default='0.0')]

    Value_1385: Annotated[str, Field(default='0.0')]

    Value_1386: Annotated[str, Field(default='0.0')]

    Value_1387: Annotated[str, Field(default='0.0')]

    Value_1388: Annotated[str, Field(default='0.0')]

    Value_1389: Annotated[str, Field(default='0.0')]

    Value_1390: Annotated[str, Field(default='0.0')]

    Value_1391: Annotated[str, Field(default='0.0')]

    Value_1392: Annotated[str, Field(default='0.0')]

    Value_1393: Annotated[str, Field(default='0.0')]

    Value_1394: Annotated[str, Field(default='0.0')]

    Value_1395: Annotated[str, Field(default='0.0')]

    Value_1396: Annotated[str, Field(default='0.0')]

    Value_1397: Annotated[str, Field(default='0.0')]

    Value_1398: Annotated[str, Field(default='0.0')]

    Value_1399: Annotated[str, Field(default='0.0')]

    Value_1400: Annotated[str, Field(default='0.0')]

    Value_1401: Annotated[str, Field(default='0.0')]

    Value_1402: Annotated[str, Field(default='0.0')]

    Value_1403: Annotated[str, Field(default='0.0')]

    Value_1404: Annotated[str, Field(default='0.0')]

    Value_1405: Annotated[str, Field(default='0.0')]

    Value_1406: Annotated[str, Field(default='0.0')]

    Value_1407: Annotated[str, Field(default='0.0')]

    Value_1408: Annotated[str, Field(default='0.0')]

    Value_1409: Annotated[str, Field(default='0.0')]

    Value_1410: Annotated[str, Field(default='0.0')]

    Value_1411: Annotated[str, Field(default='0.0')]

    Value_1412: Annotated[str, Field(default='0.0')]

    Value_1413: Annotated[str, Field(default='0.0')]

    Value_1414: Annotated[str, Field(default='0.0')]

    Value_1415: Annotated[str, Field(default='0.0')]

    Value_1416: Annotated[str, Field(default='0.0')]

    Value_1417: Annotated[str, Field(default='0.0')]

    Value_1418: Annotated[str, Field(default='0.0')]

    Value_1419: Annotated[str, Field(default='0.0')]

    Value_1420: Annotated[str, Field(default='0.0')]

    Value_1421: Annotated[str, Field(default='0.0')]

    Value_1422: Annotated[str, Field(default='0.0')]

    Value_1423: Annotated[str, Field(default='0.0')]

    Value_1424: Annotated[str, Field(default='0.0')]

    Value_1425: Annotated[str, Field(default='0.0')]

    Value_1426: Annotated[str, Field(default='0.0')]

    Value_1427: Annotated[str, Field(default='0.0')]

    Value_1428: Annotated[str, Field(default='0.0')]

    Value_1429: Annotated[str, Field(default='0.0')]

    Value_1430: Annotated[str, Field(default='0.0')]

    Value_1431: Annotated[str, Field(default='0.0')]

    Value_1432: Annotated[str, Field(default='0.0')]

    Value_1433: Annotated[str, Field(default='0.0')]

    Value_1434: Annotated[str, Field(default='0.0')]

    Value_1435: Annotated[str, Field(default='0.0')]

    Value_1436: Annotated[str, Field(default='0.0')]

    Value_1437: Annotated[str, Field(default='0.0')]

    Value_1438: Annotated[str, Field(default='0.0')]

    Value_1439: Annotated[str, Field(default='0.0')]

    Value_1440: Annotated[str, Field(default='0.0')]