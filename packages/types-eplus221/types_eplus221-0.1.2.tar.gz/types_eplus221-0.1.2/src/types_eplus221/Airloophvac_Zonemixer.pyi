from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac_Zonemixer(EpBunch):
    """Mix N inlet air streams into one (currently 500 per air loop, but extensible). Node names cannot"""

    Name: Annotated[str, Field(default=...)]

    Outlet_Node_Name: Annotated[str, Field(default=...)]

    Inlet_1_Node_Name: Annotated[str, Field(default=...)]

    Inlet_2_Node_Name: Annotated[str, Field(default=...)]

    Inlet_3_Node_Name: Annotated[str, Field(default=...)]

    Inlet_4_Node_Name: Annotated[str, Field(default=...)]

    Inlet_5_Node_Name: Annotated[str, Field(default=...)]

    Inlet_6_Node_Name: Annotated[str, Field(default=...)]

    Inlet_7_Node_Name: Annotated[str, Field(default=...)]

    Inlet_8_Node_Name: Annotated[str, Field(default=...)]

    Inlet_9_Node_Name: Annotated[str, Field(default=...)]

    Inlet_10_Node_Name: Annotated[str, Field(default=...)]

    Inlet_11_Node_Name: Annotated[str, Field(default=...)]

    Inlet_12_Node_Name: Annotated[str, Field(default=...)]

    Inlet_13_Node_Name: Annotated[str, Field(default=...)]

    Inlet_14_Node_Name: Annotated[str, Field(default=...)]

    Inlet_15_Node_Name: Annotated[str, Field(default=...)]

    Inlet_16_Node_Name: Annotated[str, Field(default=...)]

    Inlet_17_Node_Name: Annotated[str, Field(default=...)]

    Inlet_18_Node_Name: Annotated[str, Field(default=...)]

    Inlet_19_Node_Name: Annotated[str, Field(default=...)]

    Inlet_20_Node_Name: Annotated[str, Field(default=...)]

    Inlet_21_Node_Name: Annotated[str, Field(default=...)]

    Inlet_22_Node_Name: Annotated[str, Field(default=...)]

    Inlet_23_Node_Name: Annotated[str, Field(default=...)]

    Inlet_24_Node_Name: Annotated[str, Field(default=...)]

    Inlet_25_Node_Name: Annotated[str, Field(default=...)]

    Inlet_26_Node_Name: Annotated[str, Field(default=...)]

    Inlet_27_Node_Name: Annotated[str, Field(default=...)]

    Inlet_28_Node_Name: Annotated[str, Field(default=...)]

    Inlet_29_Node_Name: Annotated[str, Field(default=...)]

    Inlet_30_Node_Name: Annotated[str, Field(default=...)]

    Inlet_31_Node_Name: Annotated[str, Field(default=...)]

    Inlet_32_Node_Name: Annotated[str, Field(default=...)]

    Inlet_33_Node_Name: Annotated[str, Field(default=...)]

    Inlet_34_Node_Name: Annotated[str, Field(default=...)]

    Inlet_35_Node_Name: Annotated[str, Field(default=...)]

    Inlet_36_Node_Name: Annotated[str, Field(default=...)]

    Inlet_37_Node_Name: Annotated[str, Field(default=...)]

    Inlet_38_Node_Name: Annotated[str, Field(default=...)]

    Inlet_39_Node_Name: Annotated[str, Field(default=...)]

    Inlet_40_Node_Name: Annotated[str, Field(default=...)]

    Inlet_41_Node_Name: Annotated[str, Field(default=...)]

    Inlet_42_Node_Name: Annotated[str, Field(default=...)]

    Inlet_43_Node_Name: Annotated[str, Field(default=...)]

    Inlet_44_Node_Name: Annotated[str, Field(default=...)]

    Inlet_45_Node_Name: Annotated[str, Field(default=...)]

    Inlet_46_Node_Name: Annotated[str, Field(default=...)]

    Inlet_47_Node_Name: Annotated[str, Field(default=...)]

    Inlet_48_Node_Name: Annotated[str, Field(default=...)]

    Inlet_49_Node_Name: Annotated[str, Field(default=...)]

    Inlet_50_Node_Name: Annotated[str, Field(default=...)]

    Inlet_51_Node_Name: Annotated[str, Field(default=...)]

    Inlet_52_Node_Name: Annotated[str, Field(default=...)]

    Inlet_53_Node_Name: Annotated[str, Field(default=...)]

    Inlet_54_Node_Name: Annotated[str, Field(default=...)]

    Inlet_55_Node_Name: Annotated[str, Field(default=...)]

    Inlet_56_Node_Name: Annotated[str, Field(default=...)]

    Inlet_57_Node_Name: Annotated[str, Field(default=...)]

    Inlet_58_Node_Name: Annotated[str, Field(default=...)]

    Inlet_59_Node_Name: Annotated[str, Field(default=...)]

    Inlet_60_Node_Name: Annotated[str, Field(default=...)]

    Inlet_61_Node_Name: Annotated[str, Field(default=...)]

    Inlet_62_Node_Name: Annotated[str, Field(default=...)]

    Inlet_63_Node_Name: Annotated[str, Field(default=...)]

    Inlet_64_Node_Name: Annotated[str, Field(default=...)]

    Inlet_65_Node_Name: Annotated[str, Field(default=...)]

    Inlet_66_Node_Name: Annotated[str, Field(default=...)]

    Inlet_67_Node_Name: Annotated[str, Field(default=...)]

    Inlet_68_Node_Name: Annotated[str, Field(default=...)]

    Inlet_69_Node_Name: Annotated[str, Field(default=...)]

    Inlet_70_Node_Name: Annotated[str, Field(default=...)]

    Inlet_71_Node_Name: Annotated[str, Field(default=...)]

    Inlet_72_Node_Name: Annotated[str, Field(default=...)]

    Inlet_73_Node_Name: Annotated[str, Field(default=...)]

    Inlet_74_Node_Name: Annotated[str, Field(default=...)]

    Inlet_75_Node_Name: Annotated[str, Field(default=...)]

    Inlet_76_Node_Name: Annotated[str, Field(default=...)]

    Inlet_77_Node_Name: Annotated[str, Field(default=...)]

    Inlet_78_Node_Name: Annotated[str, Field(default=...)]

    Inlet_79_Node_Name: Annotated[str, Field(default=...)]

    Inlet_80_Node_Name: Annotated[str, Field(default=...)]

    Inlet_81_Node_Name: Annotated[str, Field(default=...)]

    Inlet_82_Node_Name: Annotated[str, Field(default=...)]

    Inlet_83_Node_Name: Annotated[str, Field(default=...)]

    Inlet_84_Node_Name: Annotated[str, Field(default=...)]

    Inlet_85_Node_Name: Annotated[str, Field(default=...)]

    Inlet_86_Node_Name: Annotated[str, Field(default=...)]

    Inlet_87_Node_Name: Annotated[str, Field(default=...)]

    Inlet_88_Node_Name: Annotated[str, Field(default=...)]

    Inlet_89_Node_Name: Annotated[str, Field(default=...)]

    Inlet_90_Node_Name: Annotated[str, Field(default=...)]

    Inlet_91_Node_Name: Annotated[str, Field(default=...)]

    Inlet_92_Node_Name: Annotated[str, Field(default=...)]

    Inlet_93_Node_Name: Annotated[str, Field(default=...)]

    Inlet_94_Node_Name: Annotated[str, Field(default=...)]

    Inlet_95_Node_Name: Annotated[str, Field(default=...)]

    Inlet_96_Node_Name: Annotated[str, Field(default=...)]

    Inlet_97_Node_Name: Annotated[str, Field(default=...)]

    Inlet_98_Node_Name: Annotated[str, Field(default=...)]

    Inlet_99_Node_Name: Annotated[str, Field(default=...)]

    Inlet_100_Node_Name: Annotated[str, Field(default=...)]

    Inlet_101_Node_Name: Annotated[str, Field(default=...)]

    Inlet_102_Node_Name: Annotated[str, Field(default=...)]

    Inlet_103_Node_Name: Annotated[str, Field(default=...)]

    Inlet_104_Node_Name: Annotated[str, Field(default=...)]

    Inlet_105_Node_Name: Annotated[str, Field(default=...)]

    Inlet_106_Node_Name: Annotated[str, Field(default=...)]

    Inlet_107_Node_Name: Annotated[str, Field(default=...)]

    Inlet_108_Node_Name: Annotated[str, Field(default=...)]

    Inlet_109_Node_Name: Annotated[str, Field(default=...)]

    Inlet_110_Node_Name: Annotated[str, Field(default=...)]

    Inlet_111_Node_Name: Annotated[str, Field(default=...)]

    Inlet_112_Node_Name: Annotated[str, Field(default=...)]

    Inlet_113_Node_Name: Annotated[str, Field(default=...)]

    Inlet_114_Node_Name: Annotated[str, Field(default=...)]

    Inlet_115_Node_Name: Annotated[str, Field(default=...)]

    Inlet_116_Node_Name: Annotated[str, Field(default=...)]

    Inlet_117_Node_Name: Annotated[str, Field(default=...)]

    Inlet_118_Node_Name: Annotated[str, Field(default=...)]

    Inlet_119_Node_Name: Annotated[str, Field(default=...)]

    Inlet_120_Node_Name: Annotated[str, Field(default=...)]

    Inlet_121_Node_Name: Annotated[str, Field(default=...)]

    Inlet_122_Node_Name: Annotated[str, Field(default=...)]

    Inlet_123_Node_Name: Annotated[str, Field(default=...)]

    Inlet_124_Node_Name: Annotated[str, Field(default=...)]

    Inlet_125_Node_Name: Annotated[str, Field(default=...)]

    Inlet_126_Node_Name: Annotated[str, Field(default=...)]

    Inlet_127_Node_Name: Annotated[str, Field(default=...)]

    Inlet_128_Node_Name: Annotated[str, Field(default=...)]

    Inlet_129_Node_Name: Annotated[str, Field(default=...)]

    Inlet_130_Node_Name: Annotated[str, Field(default=...)]

    Inlet_131_Node_Name: Annotated[str, Field(default=...)]

    Inlet_132_Node_Name: Annotated[str, Field(default=...)]

    Inlet_133_Node_Name: Annotated[str, Field(default=...)]

    Inlet_134_Node_Name: Annotated[str, Field(default=...)]

    Inlet_135_Node_Name: Annotated[str, Field(default=...)]

    Inlet_136_Node_Name: Annotated[str, Field(default=...)]

    Inlet_137_Node_Name: Annotated[str, Field(default=...)]

    Inlet_138_Node_Name: Annotated[str, Field(default=...)]

    Inlet_139_Node_Name: Annotated[str, Field(default=...)]

    Inlet_140_Node_Name: Annotated[str, Field(default=...)]

    Inlet_141_Node_Name: Annotated[str, Field(default=...)]

    Inlet_142_Node_Name: Annotated[str, Field(default=...)]

    Inlet_143_Node_Name: Annotated[str, Field(default=...)]

    Inlet_144_Node_Name: Annotated[str, Field(default=...)]

    Inlet_145_Node_Name: Annotated[str, Field(default=...)]

    Inlet_146_Node_Name: Annotated[str, Field(default=...)]

    Inlet_147_Node_Name: Annotated[str, Field(default=...)]

    Inlet_148_Node_Name: Annotated[str, Field(default=...)]

    Inlet_149_Node_Name: Annotated[str, Field(default=...)]

    Inlet_150_Node_Name: Annotated[str, Field(default=...)]

    Inlet_151_Node_Name: Annotated[str, Field(default=...)]

    Inlet_152_Node_Name: Annotated[str, Field(default=...)]

    Inlet_153_Node_Name: Annotated[str, Field(default=...)]

    Inlet_154_Node_Name: Annotated[str, Field(default=...)]

    Inlet_155_Node_Name: Annotated[str, Field(default=...)]

    Inlet_156_Node_Name: Annotated[str, Field(default=...)]

    Inlet_157_Node_Name: Annotated[str, Field(default=...)]

    Inlet_158_Node_Name: Annotated[str, Field(default=...)]

    Inlet_159_Node_Name: Annotated[str, Field(default=...)]

    Inlet_160_Node_Name: Annotated[str, Field(default=...)]

    Inlet_161_Node_Name: Annotated[str, Field(default=...)]

    Inlet_162_Node_Name: Annotated[str, Field(default=...)]

    Inlet_163_Node_Name: Annotated[str, Field(default=...)]

    Inlet_164_Node_Name: Annotated[str, Field(default=...)]

    Inlet_165_Node_Name: Annotated[str, Field(default=...)]

    Inlet_166_Node_Name: Annotated[str, Field(default=...)]

    Inlet_167_Node_Name: Annotated[str, Field(default=...)]

    Inlet_168_Node_Name: Annotated[str, Field(default=...)]

    Inlet_169_Node_Name: Annotated[str, Field(default=...)]

    Inlet_170_Node_Name: Annotated[str, Field(default=...)]

    Inlet_171_Node_Name: Annotated[str, Field(default=...)]

    Inlet_172_Node_Name: Annotated[str, Field(default=...)]

    Inlet_173_Node_Name: Annotated[str, Field(default=...)]

    Inlet_174_Node_Name: Annotated[str, Field(default=...)]

    Inlet_175_Node_Name: Annotated[str, Field(default=...)]

    Inlet_176_Node_Name: Annotated[str, Field(default=...)]

    Inlet_177_Node_Name: Annotated[str, Field(default=...)]

    Inlet_178_Node_Name: Annotated[str, Field(default=...)]

    Inlet_179_Node_Name: Annotated[str, Field(default=...)]

    Inlet_180_Node_Name: Annotated[str, Field(default=...)]

    Inlet_181_Node_Name: Annotated[str, Field(default=...)]

    Inlet_182_Node_Name: Annotated[str, Field(default=...)]

    Inlet_183_Node_Name: Annotated[str, Field(default=...)]

    Inlet_184_Node_Name: Annotated[str, Field(default=...)]

    Inlet_185_Node_Name: Annotated[str, Field(default=...)]

    Inlet_186_Node_Name: Annotated[str, Field(default=...)]

    Inlet_187_Node_Name: Annotated[str, Field(default=...)]

    Inlet_188_Node_Name: Annotated[str, Field(default=...)]

    Inlet_189_Node_Name: Annotated[str, Field(default=...)]

    Inlet_190_Node_Name: Annotated[str, Field(default=...)]

    Inlet_191_Node_Name: Annotated[str, Field(default=...)]

    Inlet_192_Node_Name: Annotated[str, Field(default=...)]

    Inlet_193_Node_Name: Annotated[str, Field(default=...)]

    Inlet_194_Node_Name: Annotated[str, Field(default=...)]

    Inlet_195_Node_Name: Annotated[str, Field(default=...)]

    Inlet_196_Node_Name: Annotated[str, Field(default=...)]

    Inlet_197_Node_Name: Annotated[str, Field(default=...)]

    Inlet_198_Node_Name: Annotated[str, Field(default=...)]

    Inlet_199_Node_Name: Annotated[str, Field(default=...)]

    Inlet_200_Node_Name: Annotated[str, Field(default=...)]

    Inlet_201_Node_Name: Annotated[str, Field(default=...)]

    Inlet_202_Node_Name: Annotated[str, Field(default=...)]

    Inlet_203_Node_Name: Annotated[str, Field(default=...)]

    Inlet_204_Node_Name: Annotated[str, Field(default=...)]

    Inlet_205_Node_Name: Annotated[str, Field(default=...)]

    Inlet_206_Node_Name: Annotated[str, Field(default=...)]

    Inlet_207_Node_Name: Annotated[str, Field(default=...)]

    Inlet_208_Node_Name: Annotated[str, Field(default=...)]

    Inlet_209_Node_Name: Annotated[str, Field(default=...)]

    Inlet_210_Node_Name: Annotated[str, Field(default=...)]

    Inlet_211_Node_Name: Annotated[str, Field(default=...)]

    Inlet_212_Node_Name: Annotated[str, Field(default=...)]

    Inlet_213_Node_Name: Annotated[str, Field(default=...)]

    Inlet_214_Node_Name: Annotated[str, Field(default=...)]

    Inlet_215_Node_Name: Annotated[str, Field(default=...)]

    Inlet_216_Node_Name: Annotated[str, Field(default=...)]

    Inlet_217_Node_Name: Annotated[str, Field(default=...)]

    Inlet_218_Node_Name: Annotated[str, Field(default=...)]

    Inlet_219_Node_Name: Annotated[str, Field(default=...)]

    Inlet_220_Node_Name: Annotated[str, Field(default=...)]

    Inlet_221_Node_Name: Annotated[str, Field(default=...)]

    Inlet_222_Node_Name: Annotated[str, Field(default=...)]

    Inlet_223_Node_Name: Annotated[str, Field(default=...)]

    Inlet_224_Node_Name: Annotated[str, Field(default=...)]

    Inlet_225_Node_Name: Annotated[str, Field(default=...)]

    Inlet_226_Node_Name: Annotated[str, Field(default=...)]

    Inlet_227_Node_Name: Annotated[str, Field(default=...)]

    Inlet_228_Node_Name: Annotated[str, Field(default=...)]

    Inlet_229_Node_Name: Annotated[str, Field(default=...)]

    Inlet_230_Node_Name: Annotated[str, Field(default=...)]

    Inlet_231_Node_Name: Annotated[str, Field(default=...)]

    Inlet_232_Node_Name: Annotated[str, Field(default=...)]

    Inlet_233_Node_Name: Annotated[str, Field(default=...)]

    Inlet_234_Node_Name: Annotated[str, Field(default=...)]

    Inlet_235_Node_Name: Annotated[str, Field(default=...)]

    Inlet_236_Node_Name: Annotated[str, Field(default=...)]

    Inlet_237_Node_Name: Annotated[str, Field(default=...)]

    Inlet_238_Node_Name: Annotated[str, Field(default=...)]

    Inlet_239_Node_Name: Annotated[str, Field(default=...)]

    Inlet_240_Node_Name: Annotated[str, Field(default=...)]

    Inlet_241_Node_Name: Annotated[str, Field(default=...)]

    Inlet_242_Node_Name: Annotated[str, Field(default=...)]

    Inlet_243_Node_Name: Annotated[str, Field(default=...)]

    Inlet_244_Node_Name: Annotated[str, Field(default=...)]

    Inlet_245_Node_Name: Annotated[str, Field(default=...)]

    Inlet_246_Node_Name: Annotated[str, Field(default=...)]

    Inlet_247_Node_Name: Annotated[str, Field(default=...)]

    Inlet_248_Node_Name: Annotated[str, Field(default=...)]

    Inlet_249_Node_Name: Annotated[str, Field(default=...)]

    Inlet_250_Node_Name: Annotated[str, Field(default=...)]

    Inlet_251_Node_Name: Annotated[str, Field(default=...)]

    Inlet_252_Node_Name: Annotated[str, Field(default=...)]

    Inlet_253_Node_Name: Annotated[str, Field(default=...)]

    Inlet_254_Node_Name: Annotated[str, Field(default=...)]

    Inlet_255_Node_Name: Annotated[str, Field(default=...)]

    Inlet_256_Node_Name: Annotated[str, Field(default=...)]

    Inlet_257_Node_Name: Annotated[str, Field(default=...)]

    Inlet_258_Node_Name: Annotated[str, Field(default=...)]

    Inlet_259_Node_Name: Annotated[str, Field(default=...)]

    Inlet_260_Node_Name: Annotated[str, Field(default=...)]

    Inlet_261_Node_Name: Annotated[str, Field(default=...)]

    Inlet_262_Node_Name: Annotated[str, Field(default=...)]

    Inlet_263_Node_Name: Annotated[str, Field(default=...)]

    Inlet_264_Node_Name: Annotated[str, Field(default=...)]

    Inlet_265_Node_Name: Annotated[str, Field(default=...)]

    Inlet_266_Node_Name: Annotated[str, Field(default=...)]

    Inlet_267_Node_Name: Annotated[str, Field(default=...)]

    Inlet_268_Node_Name: Annotated[str, Field(default=...)]

    Inlet_269_Node_Name: Annotated[str, Field(default=...)]

    Inlet_270_Node_Name: Annotated[str, Field(default=...)]

    Inlet_271_Node_Name: Annotated[str, Field(default=...)]

    Inlet_272_Node_Name: Annotated[str, Field(default=...)]

    Inlet_273_Node_Name: Annotated[str, Field(default=...)]

    Inlet_274_Node_Name: Annotated[str, Field(default=...)]

    Inlet_275_Node_Name: Annotated[str, Field(default=...)]

    Inlet_276_Node_Name: Annotated[str, Field(default=...)]

    Inlet_277_Node_Name: Annotated[str, Field(default=...)]

    Inlet_278_Node_Name: Annotated[str, Field(default=...)]

    Inlet_279_Node_Name: Annotated[str, Field(default=...)]

    Inlet_280_Node_Name: Annotated[str, Field(default=...)]

    Inlet_281_Node_Name: Annotated[str, Field(default=...)]

    Inlet_282_Node_Name: Annotated[str, Field(default=...)]

    Inlet_283_Node_Name: Annotated[str, Field(default=...)]

    Inlet_284_Node_Name: Annotated[str, Field(default=...)]

    Inlet_285_Node_Name: Annotated[str, Field(default=...)]

    Inlet_286_Node_Name: Annotated[str, Field(default=...)]

    Inlet_287_Node_Name: Annotated[str, Field(default=...)]

    Inlet_288_Node_Name: Annotated[str, Field(default=...)]

    Inlet_289_Node_Name: Annotated[str, Field(default=...)]

    Inlet_290_Node_Name: Annotated[str, Field(default=...)]

    Inlet_291_Node_Name: Annotated[str, Field(default=...)]

    Inlet_292_Node_Name: Annotated[str, Field(default=...)]

    Inlet_293_Node_Name: Annotated[str, Field(default=...)]

    Inlet_294_Node_Name: Annotated[str, Field(default=...)]

    Inlet_295_Node_Name: Annotated[str, Field(default=...)]

    Inlet_296_Node_Name: Annotated[str, Field(default=...)]

    Inlet_297_Node_Name: Annotated[str, Field(default=...)]

    Inlet_298_Node_Name: Annotated[str, Field(default=...)]

    Inlet_299_Node_Name: Annotated[str, Field(default=...)]

    Inlet_300_Node_Name: Annotated[str, Field(default=...)]

    Inlet_301_Node_Name: Annotated[str, Field(default=...)]

    Inlet_302_Node_Name: Annotated[str, Field(default=...)]

    Inlet_303_Node_Name: Annotated[str, Field(default=...)]

    Inlet_304_Node_Name: Annotated[str, Field(default=...)]

    Inlet_305_Node_Name: Annotated[str, Field(default=...)]

    Inlet_306_Node_Name: Annotated[str, Field(default=...)]

    Inlet_307_Node_Name: Annotated[str, Field(default=...)]

    Inlet_308_Node_Name: Annotated[str, Field(default=...)]

    Inlet_309_Node_Name: Annotated[str, Field(default=...)]

    Inlet_310_Node_Name: Annotated[str, Field(default=...)]

    Inlet_311_Node_Name: Annotated[str, Field(default=...)]

    Inlet_312_Node_Name: Annotated[str, Field(default=...)]

    Inlet_313_Node_Name: Annotated[str, Field(default=...)]

    Inlet_314_Node_Name: Annotated[str, Field(default=...)]

    Inlet_315_Node_Name: Annotated[str, Field(default=...)]

    Inlet_316_Node_Name: Annotated[str, Field(default=...)]

    Inlet_317_Node_Name: Annotated[str, Field(default=...)]

    Inlet_318_Node_Name: Annotated[str, Field(default=...)]

    Inlet_319_Node_Name: Annotated[str, Field(default=...)]

    Inlet_320_Node_Name: Annotated[str, Field(default=...)]

    Inlet_321_Node_Name: Annotated[str, Field(default=...)]

    Inlet_322_Node_Name: Annotated[str, Field(default=...)]

    Inlet_323_Node_Name: Annotated[str, Field(default=...)]

    Inlet_324_Node_Name: Annotated[str, Field(default=...)]

    Inlet_325_Node_Name: Annotated[str, Field(default=...)]

    Inlet_326_Node_Name: Annotated[str, Field(default=...)]

    Inlet_327_Node_Name: Annotated[str, Field(default=...)]

    Inlet_328_Node_Name: Annotated[str, Field(default=...)]

    Inlet_329_Node_Name: Annotated[str, Field(default=...)]

    Inlet_330_Node_Name: Annotated[str, Field(default=...)]

    Inlet_331_Node_Name: Annotated[str, Field(default=...)]

    Inlet_332_Node_Name: Annotated[str, Field(default=...)]

    Inlet_333_Node_Name: Annotated[str, Field(default=...)]

    Inlet_334_Node_Name: Annotated[str, Field(default=...)]

    Inlet_335_Node_Name: Annotated[str, Field(default=...)]

    Inlet_336_Node_Name: Annotated[str, Field(default=...)]

    Inlet_337_Node_Name: Annotated[str, Field(default=...)]

    Inlet_338_Node_Name: Annotated[str, Field(default=...)]

    Inlet_339_Node_Name: Annotated[str, Field(default=...)]

    Inlet_340_Node_Name: Annotated[str, Field(default=...)]

    Inlet_341_Node_Name: Annotated[str, Field(default=...)]

    Inlet_342_Node_Name: Annotated[str, Field(default=...)]

    Inlet_343_Node_Name: Annotated[str, Field(default=...)]

    Inlet_344_Node_Name: Annotated[str, Field(default=...)]

    Inlet_345_Node_Name: Annotated[str, Field(default=...)]

    Inlet_346_Node_Name: Annotated[str, Field(default=...)]

    Inlet_347_Node_Name: Annotated[str, Field(default=...)]

    Inlet_348_Node_Name: Annotated[str, Field(default=...)]

    Inlet_349_Node_Name: Annotated[str, Field(default=...)]

    Inlet_350_Node_Name: Annotated[str, Field(default=...)]

    Inlet_351_Node_Name: Annotated[str, Field(default=...)]

    Inlet_352_Node_Name: Annotated[str, Field(default=...)]

    Inlet_353_Node_Name: Annotated[str, Field(default=...)]

    Inlet_354_Node_Name: Annotated[str, Field(default=...)]

    Inlet_355_Node_Name: Annotated[str, Field(default=...)]

    Inlet_356_Node_Name: Annotated[str, Field(default=...)]

    Inlet_357_Node_Name: Annotated[str, Field(default=...)]

    Inlet_358_Node_Name: Annotated[str, Field(default=...)]

    Inlet_359_Node_Name: Annotated[str, Field(default=...)]

    Inlet_360_Node_Name: Annotated[str, Field(default=...)]

    Inlet_361_Node_Name: Annotated[str, Field(default=...)]

    Inlet_362_Node_Name: Annotated[str, Field(default=...)]

    Inlet_363_Node_Name: Annotated[str, Field(default=...)]

    Inlet_364_Node_Name: Annotated[str, Field(default=...)]

    Inlet_365_Node_Name: Annotated[str, Field(default=...)]

    Inlet_366_Node_Name: Annotated[str, Field(default=...)]

    Inlet_367_Node_Name: Annotated[str, Field(default=...)]

    Inlet_368_Node_Name: Annotated[str, Field(default=...)]

    Inlet_369_Node_Name: Annotated[str, Field(default=...)]

    Inlet_370_Node_Name: Annotated[str, Field(default=...)]

    Inlet_371_Node_Name: Annotated[str, Field(default=...)]

    Inlet_372_Node_Name: Annotated[str, Field(default=...)]

    Inlet_373_Node_Name: Annotated[str, Field(default=...)]

    Inlet_374_Node_Name: Annotated[str, Field(default=...)]

    Inlet_375_Node_Name: Annotated[str, Field(default=...)]

    Inlet_376_Node_Name: Annotated[str, Field(default=...)]

    Inlet_377_Node_Name: Annotated[str, Field(default=...)]

    Inlet_378_Node_Name: Annotated[str, Field(default=...)]

    Inlet_379_Node_Name: Annotated[str, Field(default=...)]

    Inlet_380_Node_Name: Annotated[str, Field(default=...)]

    Inlet_381_Node_Name: Annotated[str, Field(default=...)]

    Inlet_382_Node_Name: Annotated[str, Field(default=...)]

    Inlet_383_Node_Name: Annotated[str, Field(default=...)]

    Inlet_384_Node_Name: Annotated[str, Field(default=...)]

    Inlet_385_Node_Name: Annotated[str, Field(default=...)]

    Inlet_386_Node_Name: Annotated[str, Field(default=...)]

    Inlet_387_Node_Name: Annotated[str, Field(default=...)]

    Inlet_388_Node_Name: Annotated[str, Field(default=...)]

    Inlet_389_Node_Name: Annotated[str, Field(default=...)]

    Inlet_390_Node_Name: Annotated[str, Field(default=...)]

    Inlet_391_Node_Name: Annotated[str, Field(default=...)]

    Inlet_392_Node_Name: Annotated[str, Field(default=...)]

    Inlet_393_Node_Name: Annotated[str, Field(default=...)]

    Inlet_394_Node_Name: Annotated[str, Field(default=...)]

    Inlet_395_Node_Name: Annotated[str, Field(default=...)]

    Inlet_396_Node_Name: Annotated[str, Field(default=...)]

    Inlet_397_Node_Name: Annotated[str, Field(default=...)]

    Inlet_398_Node_Name: Annotated[str, Field(default=...)]

    Inlet_399_Node_Name: Annotated[str, Field(default=...)]

    Inlet_400_Node_Name: Annotated[str, Field(default=...)]

    Inlet_401_Node_Name: Annotated[str, Field(default=...)]

    Inlet_402_Node_Name: Annotated[str, Field(default=...)]

    Inlet_403_Node_Name: Annotated[str, Field(default=...)]

    Inlet_404_Node_Name: Annotated[str, Field(default=...)]

    Inlet_405_Node_Name: Annotated[str, Field(default=...)]

    Inlet_406_Node_Name: Annotated[str, Field(default=...)]

    Inlet_407_Node_Name: Annotated[str, Field(default=...)]

    Inlet_408_Node_Name: Annotated[str, Field(default=...)]

    Inlet_409_Node_Name: Annotated[str, Field(default=...)]

    Inlet_410_Node_Name: Annotated[str, Field(default=...)]

    Inlet_411_Node_Name: Annotated[str, Field(default=...)]

    Inlet_412_Node_Name: Annotated[str, Field(default=...)]

    Inlet_413_Node_Name: Annotated[str, Field(default=...)]

    Inlet_414_Node_Name: Annotated[str, Field(default=...)]

    Inlet_415_Node_Name: Annotated[str, Field(default=...)]

    Inlet_416_Node_Name: Annotated[str, Field(default=...)]

    Inlet_417_Node_Name: Annotated[str, Field(default=...)]

    Inlet_418_Node_Name: Annotated[str, Field(default=...)]

    Inlet_419_Node_Name: Annotated[str, Field(default=...)]

    Inlet_420_Node_Name: Annotated[str, Field(default=...)]

    Inlet_421_Node_Name: Annotated[str, Field(default=...)]

    Inlet_422_Node_Name: Annotated[str, Field(default=...)]

    Inlet_423_Node_Name: Annotated[str, Field(default=...)]

    Inlet_424_Node_Name: Annotated[str, Field(default=...)]

    Inlet_425_Node_Name: Annotated[str, Field(default=...)]

    Inlet_426_Node_Name: Annotated[str, Field(default=...)]

    Inlet_427_Node_Name: Annotated[str, Field(default=...)]

    Inlet_428_Node_Name: Annotated[str, Field(default=...)]

    Inlet_429_Node_Name: Annotated[str, Field(default=...)]

    Inlet_430_Node_Name: Annotated[str, Field(default=...)]

    Inlet_431_Node_Name: Annotated[str, Field(default=...)]

    Inlet_432_Node_Name: Annotated[str, Field(default=...)]

    Inlet_433_Node_Name: Annotated[str, Field(default=...)]

    Inlet_434_Node_Name: Annotated[str, Field(default=...)]

    Inlet_435_Node_Name: Annotated[str, Field(default=...)]

    Inlet_436_Node_Name: Annotated[str, Field(default=...)]

    Inlet_437_Node_Name: Annotated[str, Field(default=...)]

    Inlet_438_Node_Name: Annotated[str, Field(default=...)]

    Inlet_439_Node_Name: Annotated[str, Field(default=...)]

    Inlet_440_Node_Name: Annotated[str, Field(default=...)]

    Inlet_441_Node_Name: Annotated[str, Field(default=...)]

    Inlet_442_Node_Name: Annotated[str, Field(default=...)]

    Inlet_443_Node_Name: Annotated[str, Field(default=...)]

    Inlet_444_Node_Name: Annotated[str, Field(default=...)]

    Inlet_445_Node_Name: Annotated[str, Field(default=...)]

    Inlet_446_Node_Name: Annotated[str, Field(default=...)]

    Inlet_447_Node_Name: Annotated[str, Field(default=...)]

    Inlet_448_Node_Name: Annotated[str, Field(default=...)]

    Inlet_449_Node_Name: Annotated[str, Field(default=...)]

    Inlet_450_Node_Name: Annotated[str, Field(default=...)]

    Inlet_451_Node_Name: Annotated[str, Field(default=...)]

    Inlet_452_Node_Name: Annotated[str, Field(default=...)]

    Inlet_453_Node_Name: Annotated[str, Field(default=...)]

    Inlet_454_Node_Name: Annotated[str, Field(default=...)]

    Inlet_455_Node_Name: Annotated[str, Field(default=...)]

    Inlet_456_Node_Name: Annotated[str, Field(default=...)]

    Inlet_457_Node_Name: Annotated[str, Field(default=...)]

    Inlet_458_Node_Name: Annotated[str, Field(default=...)]

    Inlet_459_Node_Name: Annotated[str, Field(default=...)]

    Inlet_460_Node_Name: Annotated[str, Field(default=...)]

    Inlet_461_Node_Name: Annotated[str, Field(default=...)]

    Inlet_462_Node_Name: Annotated[str, Field(default=...)]

    Inlet_463_Node_Name: Annotated[str, Field(default=...)]

    Inlet_464_Node_Name: Annotated[str, Field(default=...)]

    Inlet_465_Node_Name: Annotated[str, Field(default=...)]

    Inlet_466_Node_Name: Annotated[str, Field(default=...)]

    Inlet_467_Node_Name: Annotated[str, Field(default=...)]

    Inlet_468_Node_Name: Annotated[str, Field(default=...)]

    Inlet_469_Node_Name: Annotated[str, Field(default=...)]

    Inlet_470_Node_Name: Annotated[str, Field(default=...)]

    Inlet_471_Node_Name: Annotated[str, Field(default=...)]

    Inlet_472_Node_Name: Annotated[str, Field(default=...)]

    Inlet_473_Node_Name: Annotated[str, Field(default=...)]

    Inlet_474_Node_Name: Annotated[str, Field(default=...)]

    Inlet_475_Node_Name: Annotated[str, Field(default=...)]

    Inlet_476_Node_Name: Annotated[str, Field(default=...)]

    Inlet_477_Node_Name: Annotated[str, Field(default=...)]

    Inlet_478_Node_Name: Annotated[str, Field(default=...)]

    Inlet_479_Node_Name: Annotated[str, Field(default=...)]

    Inlet_480_Node_Name: Annotated[str, Field(default=...)]

    Inlet_481_Node_Name: Annotated[str, Field(default=...)]

    Inlet_482_Node_Name: Annotated[str, Field(default=...)]

    Inlet_483_Node_Name: Annotated[str, Field(default=...)]

    Inlet_484_Node_Name: Annotated[str, Field(default=...)]

    Inlet_485_Node_Name: Annotated[str, Field(default=...)]

    Inlet_486_Node_Name: Annotated[str, Field(default=...)]

    Inlet_487_Node_Name: Annotated[str, Field(default=...)]

    Inlet_488_Node_Name: Annotated[str, Field(default=...)]

    Inlet_489_Node_Name: Annotated[str, Field(default=...)]

    Inlet_490_Node_Name: Annotated[str, Field(default=...)]

    Inlet_491_Node_Name: Annotated[str, Field(default=...)]

    Inlet_492_Node_Name: Annotated[str, Field(default=...)]

    Inlet_493_Node_Name: Annotated[str, Field(default=...)]

    Inlet_494_Node_Name: Annotated[str, Field(default=...)]

    Inlet_495_Node_Name: Annotated[str, Field(default=...)]

    Inlet_496_Node_Name: Annotated[str, Field(default=...)]

    Inlet_497_Node_Name: Annotated[str, Field(default=...)]

    Inlet_498_Node_Name: Annotated[str, Field(default=...)]

    Inlet_499_Node_Name: Annotated[str, Field(default=...)]

    Inlet_500_Node_Name: Annotated[str, Field(default=...)]