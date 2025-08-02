from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac_Zonesplitter(EpBunch):
    """Split one air stream into N outlet streams (currently 500 per air loop, but extensible). Node names"""

    Name: Annotated[str, Field(default=...)]

    Inlet_Node_Name: Annotated[str, Field(default=...)]

    Outlet_1_Node_Name: Annotated[str, Field(default=...)]

    Outlet_2_Node_Name: Annotated[str, Field(default=...)]

    Outlet_3_Node_Name: Annotated[str, Field(default=...)]

    Outlet_4_Node_Name: Annotated[str, Field(default=...)]

    Outlet_5_Node_Name: Annotated[str, Field(default=...)]

    Outlet_6_Node_Name: Annotated[str, Field(default=...)]

    Outlet_7_Node_Name: Annotated[str, Field(default=...)]

    Outlet_8_Node_Name: Annotated[str, Field(default=...)]

    Outlet_9_Node_Name: Annotated[str, Field(default=...)]

    Outlet_10_Node_Name: Annotated[str, Field(default=...)]

    Outlet_11_Node_Name: Annotated[str, Field(default=...)]

    Outlet_12_Node_Name: Annotated[str, Field(default=...)]

    Outlet_13_Node_Name: Annotated[str, Field(default=...)]

    Outlet_14_Node_Name: Annotated[str, Field(default=...)]

    Outlet_15_Node_Name: Annotated[str, Field(default=...)]

    Outlet_16_Node_Name: Annotated[str, Field(default=...)]

    Outlet_17_Node_Name: Annotated[str, Field(default=...)]

    Outlet_18_Node_Name: Annotated[str, Field(default=...)]

    Outlet_19_Node_Name: Annotated[str, Field(default=...)]

    Outlet_20_Node_Name: Annotated[str, Field(default=...)]

    Outlet_21_Node_Name: Annotated[str, Field(default=...)]

    Outlet_22_Node_Name: Annotated[str, Field(default=...)]

    Outlet_23_Node_Name: Annotated[str, Field(default=...)]

    Outlet_24_Node_Name: Annotated[str, Field(default=...)]

    Outlet_25_Node_Name: Annotated[str, Field(default=...)]

    Outlet_26_Node_Name: Annotated[str, Field(default=...)]

    Outlet_27_Node_Name: Annotated[str, Field(default=...)]

    Outlet_28_Node_Name: Annotated[str, Field(default=...)]

    Outlet_29_Node_Name: Annotated[str, Field(default=...)]

    Outlet_30_Node_Name: Annotated[str, Field(default=...)]

    Outlet_31_Node_Name: Annotated[str, Field(default=...)]

    Outlet_32_Node_Name: Annotated[str, Field(default=...)]

    Outlet_33_Node_Name: Annotated[str, Field(default=...)]

    Outlet_34_Node_Name: Annotated[str, Field(default=...)]

    Outlet_35_Node_Name: Annotated[str, Field(default=...)]

    Outlet_36_Node_Name: Annotated[str, Field(default=...)]

    Outlet_37_Node_Name: Annotated[str, Field(default=...)]

    Outlet_38_Node_Name: Annotated[str, Field(default=...)]

    Outlet_39_Node_Name: Annotated[str, Field(default=...)]

    Outlet_40_Node_Name: Annotated[str, Field(default=...)]

    Outlet_41_Node_Name: Annotated[str, Field(default=...)]

    Outlet_42_Node_Name: Annotated[str, Field(default=...)]

    Outlet_43_Node_Name: Annotated[str, Field(default=...)]

    Outlet_44_Node_Name: Annotated[str, Field(default=...)]

    Outlet_45_Node_Name: Annotated[str, Field(default=...)]

    Outlet_46_Node_Name: Annotated[str, Field(default=...)]

    Outlet_47_Node_Name: Annotated[str, Field(default=...)]

    Outlet_48_Node_Name: Annotated[str, Field(default=...)]

    Outlet_49_Node_Name: Annotated[str, Field(default=...)]

    Outlet_50_Node_Name: Annotated[str, Field(default=...)]

    Outlet_51_Node_Name: Annotated[str, Field(default=...)]

    Outlet_52_Node_Name: Annotated[str, Field(default=...)]

    Outlet_53_Node_Name: Annotated[str, Field(default=...)]

    Outlet_54_Node_Name: Annotated[str, Field(default=...)]

    Outlet_55_Node_Name: Annotated[str, Field(default=...)]

    Outlet_56_Node_Name: Annotated[str, Field(default=...)]

    Outlet_57_Node_Name: Annotated[str, Field(default=...)]

    Outlet_58_Node_Name: Annotated[str, Field(default=...)]

    Outlet_59_Node_Name: Annotated[str, Field(default=...)]

    Outlet_60_Node_Name: Annotated[str, Field(default=...)]

    Outlet_61_Node_Name: Annotated[str, Field(default=...)]

    Outlet_62_Node_Name: Annotated[str, Field(default=...)]

    Outlet_63_Node_Name: Annotated[str, Field(default=...)]

    Outlet_64_Node_Name: Annotated[str, Field(default=...)]

    Outlet_65_Node_Name: Annotated[str, Field(default=...)]

    Outlet_66_Node_Name: Annotated[str, Field(default=...)]

    Outlet_67_Node_Name: Annotated[str, Field(default=...)]

    Outlet_68_Node_Name: Annotated[str, Field(default=...)]

    Outlet_69_Node_Name: Annotated[str, Field(default=...)]

    Outlet_70_Node_Name: Annotated[str, Field(default=...)]

    Outlet_71_Node_Name: Annotated[str, Field(default=...)]

    Outlet_72_Node_Name: Annotated[str, Field(default=...)]

    Outlet_73_Node_Name: Annotated[str, Field(default=...)]

    Outlet_74_Node_Name: Annotated[str, Field(default=...)]

    Outlet_75_Node_Name: Annotated[str, Field(default=...)]

    Outlet_76_Node_Name: Annotated[str, Field(default=...)]

    Outlet_77_Node_Name: Annotated[str, Field(default=...)]

    Outlet_78_Node_Name: Annotated[str, Field(default=...)]

    Outlet_79_Node_Name: Annotated[str, Field(default=...)]

    Outlet_80_Node_Name: Annotated[str, Field(default=...)]

    Outlet_81_Node_Name: Annotated[str, Field(default=...)]

    Outlet_82_Node_Name: Annotated[str, Field(default=...)]

    Outlet_83_Node_Name: Annotated[str, Field(default=...)]

    Outlet_84_Node_Name: Annotated[str, Field(default=...)]

    Outlet_85_Node_Name: Annotated[str, Field(default=...)]

    Outlet_86_Node_Name: Annotated[str, Field(default=...)]

    Outlet_87_Node_Name: Annotated[str, Field(default=...)]

    Outlet_88_Node_Name: Annotated[str, Field(default=...)]

    Outlet_89_Node_Name: Annotated[str, Field(default=...)]

    Outlet_90_Node_Name: Annotated[str, Field(default=...)]

    Outlet_91_Node_Name: Annotated[str, Field(default=...)]

    Outlet_92_Node_Name: Annotated[str, Field(default=...)]

    Outlet_93_Node_Name: Annotated[str, Field(default=...)]

    Outlet_94_Node_Name: Annotated[str, Field(default=...)]

    Outlet_95_Node_Name: Annotated[str, Field(default=...)]

    Outlet_96_Node_Name: Annotated[str, Field(default=...)]

    Outlet_97_Node_Name: Annotated[str, Field(default=...)]

    Outlet_98_Node_Name: Annotated[str, Field(default=...)]

    Outlet_99_Node_Name: Annotated[str, Field(default=...)]

    Outlet_100_Node_Name: Annotated[str, Field(default=...)]

    Outlet_101_Node_Name: Annotated[str, Field(default=...)]

    Outlet_102_Node_Name: Annotated[str, Field(default=...)]

    Outlet_103_Node_Name: Annotated[str, Field(default=...)]

    Outlet_104_Node_Name: Annotated[str, Field(default=...)]

    Outlet_105_Node_Name: Annotated[str, Field(default=...)]

    Outlet_106_Node_Name: Annotated[str, Field(default=...)]

    Outlet_107_Node_Name: Annotated[str, Field(default=...)]

    Outlet_108_Node_Name: Annotated[str, Field(default=...)]

    Outlet_109_Node_Name: Annotated[str, Field(default=...)]

    Outlet_110_Node_Name: Annotated[str, Field(default=...)]

    Outlet_111_Node_Name: Annotated[str, Field(default=...)]

    Outlet_112_Node_Name: Annotated[str, Field(default=...)]

    Outlet_113_Node_Name: Annotated[str, Field(default=...)]

    Outlet_114_Node_Name: Annotated[str, Field(default=...)]

    Outlet_115_Node_Name: Annotated[str, Field(default=...)]

    Outlet_116_Node_Name: Annotated[str, Field(default=...)]

    Outlet_117_Node_Name: Annotated[str, Field(default=...)]

    Outlet_118_Node_Name: Annotated[str, Field(default=...)]

    Outlet_119_Node_Name: Annotated[str, Field(default=...)]

    Outlet_120_Node_Name: Annotated[str, Field(default=...)]

    Outlet_121_Node_Name: Annotated[str, Field(default=...)]

    Outlet_122_Node_Name: Annotated[str, Field(default=...)]

    Outlet_123_Node_Name: Annotated[str, Field(default=...)]

    Outlet_124_Node_Name: Annotated[str, Field(default=...)]

    Outlet_125_Node_Name: Annotated[str, Field(default=...)]

    Outlet_126_Node_Name: Annotated[str, Field(default=...)]

    Outlet_127_Node_Name: Annotated[str, Field(default=...)]

    Outlet_128_Node_Name: Annotated[str, Field(default=...)]

    Outlet_129_Node_Name: Annotated[str, Field(default=...)]

    Outlet_130_Node_Name: Annotated[str, Field(default=...)]

    Outlet_131_Node_Name: Annotated[str, Field(default=...)]

    Outlet_132_Node_Name: Annotated[str, Field(default=...)]

    Outlet_133_Node_Name: Annotated[str, Field(default=...)]

    Outlet_134_Node_Name: Annotated[str, Field(default=...)]

    Outlet_135_Node_Name: Annotated[str, Field(default=...)]

    Outlet_136_Node_Name: Annotated[str, Field(default=...)]

    Outlet_137_Node_Name: Annotated[str, Field(default=...)]

    Outlet_138_Node_Name: Annotated[str, Field(default=...)]

    Outlet_139_Node_Name: Annotated[str, Field(default=...)]

    Outlet_140_Node_Name: Annotated[str, Field(default=...)]

    Outlet_141_Node_Name: Annotated[str, Field(default=...)]

    Outlet_142_Node_Name: Annotated[str, Field(default=...)]

    Outlet_143_Node_Name: Annotated[str, Field(default=...)]

    Outlet_144_Node_Name: Annotated[str, Field(default=...)]

    Outlet_145_Node_Name: Annotated[str, Field(default=...)]

    Outlet_146_Node_Name: Annotated[str, Field(default=...)]

    Outlet_147_Node_Name: Annotated[str, Field(default=...)]

    Outlet_148_Node_Name: Annotated[str, Field(default=...)]

    Outlet_149_Node_Name: Annotated[str, Field(default=...)]

    Outlet_150_Node_Name: Annotated[str, Field(default=...)]

    Outlet_151_Node_Name: Annotated[str, Field(default=...)]

    Outlet_152_Node_Name: Annotated[str, Field(default=...)]

    Outlet_153_Node_Name: Annotated[str, Field(default=...)]

    Outlet_154_Node_Name: Annotated[str, Field(default=...)]

    Outlet_155_Node_Name: Annotated[str, Field(default=...)]

    Outlet_156_Node_Name: Annotated[str, Field(default=...)]

    Outlet_157_Node_Name: Annotated[str, Field(default=...)]

    Outlet_158_Node_Name: Annotated[str, Field(default=...)]

    Outlet_159_Node_Name: Annotated[str, Field(default=...)]

    Outlet_160_Node_Name: Annotated[str, Field(default=...)]

    Outlet_161_Node_Name: Annotated[str, Field(default=...)]

    Outlet_162_Node_Name: Annotated[str, Field(default=...)]

    Outlet_163_Node_Name: Annotated[str, Field(default=...)]

    Outlet_164_Node_Name: Annotated[str, Field(default=...)]

    Outlet_165_Node_Name: Annotated[str, Field(default=...)]

    Outlet_166_Node_Name: Annotated[str, Field(default=...)]

    Outlet_167_Node_Name: Annotated[str, Field(default=...)]

    Outlet_168_Node_Name: Annotated[str, Field(default=...)]

    Outlet_169_Node_Name: Annotated[str, Field(default=...)]

    Outlet_170_Node_Name: Annotated[str, Field(default=...)]

    Outlet_171_Node_Name: Annotated[str, Field(default=...)]

    Outlet_172_Node_Name: Annotated[str, Field(default=...)]

    Outlet_173_Node_Name: Annotated[str, Field(default=...)]

    Outlet_174_Node_Name: Annotated[str, Field(default=...)]

    Outlet_175_Node_Name: Annotated[str, Field(default=...)]

    Outlet_176_Node_Name: Annotated[str, Field(default=...)]

    Outlet_177_Node_Name: Annotated[str, Field(default=...)]

    Outlet_178_Node_Name: Annotated[str, Field(default=...)]

    Outlet_179_Node_Name: Annotated[str, Field(default=...)]

    Outlet_180_Node_Name: Annotated[str, Field(default=...)]

    Outlet_181_Node_Name: Annotated[str, Field(default=...)]

    Outlet_182_Node_Name: Annotated[str, Field(default=...)]

    Outlet_183_Node_Name: Annotated[str, Field(default=...)]

    Outlet_184_Node_Name: Annotated[str, Field(default=...)]

    Outlet_185_Node_Name: Annotated[str, Field(default=...)]

    Outlet_186_Node_Name: Annotated[str, Field(default=...)]

    Outlet_187_Node_Name: Annotated[str, Field(default=...)]

    Outlet_188_Node_Name: Annotated[str, Field(default=...)]

    Outlet_189_Node_Name: Annotated[str, Field(default=...)]

    Outlet_190_Node_Name: Annotated[str, Field(default=...)]

    Outlet_191_Node_Name: Annotated[str, Field(default=...)]

    Outlet_192_Node_Name: Annotated[str, Field(default=...)]

    Outlet_193_Node_Name: Annotated[str, Field(default=...)]

    Outlet_194_Node_Name: Annotated[str, Field(default=...)]

    Outlet_195_Node_Name: Annotated[str, Field(default=...)]

    Outlet_196_Node_Name: Annotated[str, Field(default=...)]

    Outlet_197_Node_Name: Annotated[str, Field(default=...)]

    Outlet_198_Node_Name: Annotated[str, Field(default=...)]

    Outlet_199_Node_Name: Annotated[str, Field(default=...)]

    Outlet_200_Node_Name: Annotated[str, Field(default=...)]

    Outlet_201_Node_Name: Annotated[str, Field(default=...)]

    Outlet_202_Node_Name: Annotated[str, Field(default=...)]

    Outlet_203_Node_Name: Annotated[str, Field(default=...)]

    Outlet_204_Node_Name: Annotated[str, Field(default=...)]

    Outlet_205_Node_Name: Annotated[str, Field(default=...)]

    Outlet_206_Node_Name: Annotated[str, Field(default=...)]

    Outlet_207_Node_Name: Annotated[str, Field(default=...)]

    Outlet_208_Node_Name: Annotated[str, Field(default=...)]

    Outlet_209_Node_Name: Annotated[str, Field(default=...)]

    Outlet_210_Node_Name: Annotated[str, Field(default=...)]

    Outlet_211_Node_Name: Annotated[str, Field(default=...)]

    Outlet_212_Node_Name: Annotated[str, Field(default=...)]

    Outlet_213_Node_Name: Annotated[str, Field(default=...)]

    Outlet_214_Node_Name: Annotated[str, Field(default=...)]

    Outlet_215_Node_Name: Annotated[str, Field(default=...)]

    Outlet_216_Node_Name: Annotated[str, Field(default=...)]

    Outlet_217_Node_Name: Annotated[str, Field(default=...)]

    Outlet_218_Node_Name: Annotated[str, Field(default=...)]

    Outlet_219_Node_Name: Annotated[str, Field(default=...)]

    Outlet_220_Node_Name: Annotated[str, Field(default=...)]

    Outlet_221_Node_Name: Annotated[str, Field(default=...)]

    Outlet_222_Node_Name: Annotated[str, Field(default=...)]

    Outlet_223_Node_Name: Annotated[str, Field(default=...)]

    Outlet_224_Node_Name: Annotated[str, Field(default=...)]

    Outlet_225_Node_Name: Annotated[str, Field(default=...)]

    Outlet_226_Node_Name: Annotated[str, Field(default=...)]

    Outlet_227_Node_Name: Annotated[str, Field(default=...)]

    Outlet_228_Node_Name: Annotated[str, Field(default=...)]

    Outlet_229_Node_Name: Annotated[str, Field(default=...)]

    Outlet_230_Node_Name: Annotated[str, Field(default=...)]

    Outlet_231_Node_Name: Annotated[str, Field(default=...)]

    Outlet_232_Node_Name: Annotated[str, Field(default=...)]

    Outlet_233_Node_Name: Annotated[str, Field(default=...)]

    Outlet_234_Node_Name: Annotated[str, Field(default=...)]

    Outlet_235_Node_Name: Annotated[str, Field(default=...)]

    Outlet_236_Node_Name: Annotated[str, Field(default=...)]

    Outlet_237_Node_Name: Annotated[str, Field(default=...)]

    Outlet_238_Node_Name: Annotated[str, Field(default=...)]

    Outlet_239_Node_Name: Annotated[str, Field(default=...)]

    Outlet_240_Node_Name: Annotated[str, Field(default=...)]

    Outlet_241_Node_Name: Annotated[str, Field(default=...)]

    Outlet_242_Node_Name: Annotated[str, Field(default=...)]

    Outlet_243_Node_Name: Annotated[str, Field(default=...)]

    Outlet_244_Node_Name: Annotated[str, Field(default=...)]

    Outlet_245_Node_Name: Annotated[str, Field(default=...)]

    Outlet_246_Node_Name: Annotated[str, Field(default=...)]

    Outlet_247_Node_Name: Annotated[str, Field(default=...)]

    Outlet_248_Node_Name: Annotated[str, Field(default=...)]

    Outlet_249_Node_Name: Annotated[str, Field(default=...)]

    Outlet_250_Node_Name: Annotated[str, Field(default=...)]

    Outlet_251_Node_Name: Annotated[str, Field(default=...)]

    Outlet_252_Node_Name: Annotated[str, Field(default=...)]

    Outlet_253_Node_Name: Annotated[str, Field(default=...)]

    Outlet_254_Node_Name: Annotated[str, Field(default=...)]

    Outlet_255_Node_Name: Annotated[str, Field(default=...)]

    Outlet_256_Node_Name: Annotated[str, Field(default=...)]

    Outlet_257_Node_Name: Annotated[str, Field(default=...)]

    Outlet_258_Node_Name: Annotated[str, Field(default=...)]

    Outlet_259_Node_Name: Annotated[str, Field(default=...)]

    Outlet_260_Node_Name: Annotated[str, Field(default=...)]

    Outlet_261_Node_Name: Annotated[str, Field(default=...)]

    Outlet_262_Node_Name: Annotated[str, Field(default=...)]

    Outlet_263_Node_Name: Annotated[str, Field(default=...)]

    Outlet_264_Node_Name: Annotated[str, Field(default=...)]

    Outlet_265_Node_Name: Annotated[str, Field(default=...)]

    Outlet_266_Node_Name: Annotated[str, Field(default=...)]

    Outlet_267_Node_Name: Annotated[str, Field(default=...)]

    Outlet_268_Node_Name: Annotated[str, Field(default=...)]

    Outlet_269_Node_Name: Annotated[str, Field(default=...)]

    Outlet_270_Node_Name: Annotated[str, Field(default=...)]

    Outlet_271_Node_Name: Annotated[str, Field(default=...)]

    Outlet_272_Node_Name: Annotated[str, Field(default=...)]

    Outlet_273_Node_Name: Annotated[str, Field(default=...)]

    Outlet_274_Node_Name: Annotated[str, Field(default=...)]

    Outlet_275_Node_Name: Annotated[str, Field(default=...)]

    Outlet_276_Node_Name: Annotated[str, Field(default=...)]

    Outlet_277_Node_Name: Annotated[str, Field(default=...)]

    Outlet_278_Node_Name: Annotated[str, Field(default=...)]

    Outlet_279_Node_Name: Annotated[str, Field(default=...)]

    Outlet_280_Node_Name: Annotated[str, Field(default=...)]

    Outlet_281_Node_Name: Annotated[str, Field(default=...)]

    Outlet_282_Node_Name: Annotated[str, Field(default=...)]

    Outlet_283_Node_Name: Annotated[str, Field(default=...)]

    Outlet_284_Node_Name: Annotated[str, Field(default=...)]

    Outlet_285_Node_Name: Annotated[str, Field(default=...)]

    Outlet_286_Node_Name: Annotated[str, Field(default=...)]

    Outlet_287_Node_Name: Annotated[str, Field(default=...)]

    Outlet_288_Node_Name: Annotated[str, Field(default=...)]

    Outlet_289_Node_Name: Annotated[str, Field(default=...)]

    Outlet_290_Node_Name: Annotated[str, Field(default=...)]

    Outlet_291_Node_Name: Annotated[str, Field(default=...)]

    Outlet_292_Node_Name: Annotated[str, Field(default=...)]

    Outlet_293_Node_Name: Annotated[str, Field(default=...)]

    Outlet_294_Node_Name: Annotated[str, Field(default=...)]

    Outlet_295_Node_Name: Annotated[str, Field(default=...)]

    Outlet_296_Node_Name: Annotated[str, Field(default=...)]

    Outlet_297_Node_Name: Annotated[str, Field(default=...)]

    Outlet_298_Node_Name: Annotated[str, Field(default=...)]

    Outlet_299_Node_Name: Annotated[str, Field(default=...)]

    Outlet_300_Node_Name: Annotated[str, Field(default=...)]

    Outlet_301_Node_Name: Annotated[str, Field(default=...)]

    Outlet_302_Node_Name: Annotated[str, Field(default=...)]

    Outlet_303_Node_Name: Annotated[str, Field(default=...)]

    Outlet_304_Node_Name: Annotated[str, Field(default=...)]

    Outlet_305_Node_Name: Annotated[str, Field(default=...)]

    Outlet_306_Node_Name: Annotated[str, Field(default=...)]

    Outlet_307_Node_Name: Annotated[str, Field(default=...)]

    Outlet_308_Node_Name: Annotated[str, Field(default=...)]

    Outlet_309_Node_Name: Annotated[str, Field(default=...)]

    Outlet_310_Node_Name: Annotated[str, Field(default=...)]

    Outlet_311_Node_Name: Annotated[str, Field(default=...)]

    Outlet_312_Node_Name: Annotated[str, Field(default=...)]

    Outlet_313_Node_Name: Annotated[str, Field(default=...)]

    Outlet_314_Node_Name: Annotated[str, Field(default=...)]

    Outlet_315_Node_Name: Annotated[str, Field(default=...)]

    Outlet_316_Node_Name: Annotated[str, Field(default=...)]

    Outlet_317_Node_Name: Annotated[str, Field(default=...)]

    Outlet_318_Node_Name: Annotated[str, Field(default=...)]

    Outlet_319_Node_Name: Annotated[str, Field(default=...)]

    Outlet_320_Node_Name: Annotated[str, Field(default=...)]

    Outlet_321_Node_Name: Annotated[str, Field(default=...)]

    Outlet_322_Node_Name: Annotated[str, Field(default=...)]

    Outlet_323_Node_Name: Annotated[str, Field(default=...)]

    Outlet_324_Node_Name: Annotated[str, Field(default=...)]

    Outlet_325_Node_Name: Annotated[str, Field(default=...)]

    Outlet_326_Node_Name: Annotated[str, Field(default=...)]

    Outlet_327_Node_Name: Annotated[str, Field(default=...)]

    Outlet_328_Node_Name: Annotated[str, Field(default=...)]

    Outlet_329_Node_Name: Annotated[str, Field(default=...)]

    Outlet_330_Node_Name: Annotated[str, Field(default=...)]

    Outlet_331_Node_Name: Annotated[str, Field(default=...)]

    Outlet_332_Node_Name: Annotated[str, Field(default=...)]

    Outlet_333_Node_Name: Annotated[str, Field(default=...)]

    Outlet_334_Node_Name: Annotated[str, Field(default=...)]

    Outlet_335_Node_Name: Annotated[str, Field(default=...)]

    Outlet_336_Node_Name: Annotated[str, Field(default=...)]

    Outlet_337_Node_Name: Annotated[str, Field(default=...)]

    Outlet_338_Node_Name: Annotated[str, Field(default=...)]

    Outlet_339_Node_Name: Annotated[str, Field(default=...)]

    Outlet_340_Node_Name: Annotated[str, Field(default=...)]

    Outlet_341_Node_Name: Annotated[str, Field(default=...)]

    Outlet_342_Node_Name: Annotated[str, Field(default=...)]

    Outlet_343_Node_Name: Annotated[str, Field(default=...)]

    Outlet_344_Node_Name: Annotated[str, Field(default=...)]

    Outlet_345_Node_Name: Annotated[str, Field(default=...)]

    Outlet_346_Node_Name: Annotated[str, Field(default=...)]

    Outlet_347_Node_Name: Annotated[str, Field(default=...)]

    Outlet_348_Node_Name: Annotated[str, Field(default=...)]

    Outlet_349_Node_Name: Annotated[str, Field(default=...)]

    Outlet_350_Node_Name: Annotated[str, Field(default=...)]

    Outlet_351_Node_Name: Annotated[str, Field(default=...)]

    Outlet_352_Node_Name: Annotated[str, Field(default=...)]

    Outlet_353_Node_Name: Annotated[str, Field(default=...)]

    Outlet_354_Node_Name: Annotated[str, Field(default=...)]

    Outlet_355_Node_Name: Annotated[str, Field(default=...)]

    Outlet_356_Node_Name: Annotated[str, Field(default=...)]

    Outlet_357_Node_Name: Annotated[str, Field(default=...)]

    Outlet_358_Node_Name: Annotated[str, Field(default=...)]

    Outlet_359_Node_Name: Annotated[str, Field(default=...)]

    Outlet_360_Node_Name: Annotated[str, Field(default=...)]

    Outlet_361_Node_Name: Annotated[str, Field(default=...)]

    Outlet_362_Node_Name: Annotated[str, Field(default=...)]

    Outlet_363_Node_Name: Annotated[str, Field(default=...)]

    Outlet_364_Node_Name: Annotated[str, Field(default=...)]

    Outlet_365_Node_Name: Annotated[str, Field(default=...)]

    Outlet_366_Node_Name: Annotated[str, Field(default=...)]

    Outlet_367_Node_Name: Annotated[str, Field(default=...)]

    Outlet_368_Node_Name: Annotated[str, Field(default=...)]

    Outlet_369_Node_Name: Annotated[str, Field(default=...)]

    Outlet_370_Node_Name: Annotated[str, Field(default=...)]

    Outlet_371_Node_Name: Annotated[str, Field(default=...)]

    Outlet_372_Node_Name: Annotated[str, Field(default=...)]

    Outlet_373_Node_Name: Annotated[str, Field(default=...)]

    Outlet_374_Node_Name: Annotated[str, Field(default=...)]

    Outlet_375_Node_Name: Annotated[str, Field(default=...)]

    Outlet_376_Node_Name: Annotated[str, Field(default=...)]

    Outlet_377_Node_Name: Annotated[str, Field(default=...)]

    Outlet_378_Node_Name: Annotated[str, Field(default=...)]

    Outlet_379_Node_Name: Annotated[str, Field(default=...)]

    Outlet_380_Node_Name: Annotated[str, Field(default=...)]

    Outlet_381_Node_Name: Annotated[str, Field(default=...)]

    Outlet_382_Node_Name: Annotated[str, Field(default=...)]

    Outlet_383_Node_Name: Annotated[str, Field(default=...)]

    Outlet_384_Node_Name: Annotated[str, Field(default=...)]

    Outlet_385_Node_Name: Annotated[str, Field(default=...)]

    Outlet_386_Node_Name: Annotated[str, Field(default=...)]

    Outlet_387_Node_Name: Annotated[str, Field(default=...)]

    Outlet_388_Node_Name: Annotated[str, Field(default=...)]

    Outlet_389_Node_Name: Annotated[str, Field(default=...)]

    Outlet_390_Node_Name: Annotated[str, Field(default=...)]

    Outlet_391_Node_Name: Annotated[str, Field(default=...)]

    Outlet_392_Node_Name: Annotated[str, Field(default=...)]

    Outlet_393_Node_Name: Annotated[str, Field(default=...)]

    Outlet_394_Node_Name: Annotated[str, Field(default=...)]

    Outlet_395_Node_Name: Annotated[str, Field(default=...)]

    Outlet_396_Node_Name: Annotated[str, Field(default=...)]

    Outlet_397_Node_Name: Annotated[str, Field(default=...)]

    Outlet_398_Node_Name: Annotated[str, Field(default=...)]

    Outlet_399_Node_Name: Annotated[str, Field(default=...)]

    Outlet_400_Node_Name: Annotated[str, Field(default=...)]

    Outlet_401_Node_Name: Annotated[str, Field(default=...)]

    Outlet_402_Node_Name: Annotated[str, Field(default=...)]

    Outlet_403_Node_Name: Annotated[str, Field(default=...)]

    Outlet_404_Node_Name: Annotated[str, Field(default=...)]

    Outlet_405_Node_Name: Annotated[str, Field(default=...)]

    Outlet_406_Node_Name: Annotated[str, Field(default=...)]

    Outlet_407_Node_Name: Annotated[str, Field(default=...)]

    Outlet_408_Node_Name: Annotated[str, Field(default=...)]

    Outlet_409_Node_Name: Annotated[str, Field(default=...)]

    Outlet_410_Node_Name: Annotated[str, Field(default=...)]

    Outlet_411_Node_Name: Annotated[str, Field(default=...)]

    Outlet_412_Node_Name: Annotated[str, Field(default=...)]

    Outlet_413_Node_Name: Annotated[str, Field(default=...)]

    Outlet_414_Node_Name: Annotated[str, Field(default=...)]

    Outlet_415_Node_Name: Annotated[str, Field(default=...)]

    Outlet_416_Node_Name: Annotated[str, Field(default=...)]

    Outlet_417_Node_Name: Annotated[str, Field(default=...)]

    Outlet_418_Node_Name: Annotated[str, Field(default=...)]

    Outlet_419_Node_Name: Annotated[str, Field(default=...)]

    Outlet_420_Node_Name: Annotated[str, Field(default=...)]

    Outlet_421_Node_Name: Annotated[str, Field(default=...)]

    Outlet_422_Node_Name: Annotated[str, Field(default=...)]

    Outlet_423_Node_Name: Annotated[str, Field(default=...)]

    Outlet_424_Node_Name: Annotated[str, Field(default=...)]

    Outlet_425_Node_Name: Annotated[str, Field(default=...)]

    Outlet_426_Node_Name: Annotated[str, Field(default=...)]

    Outlet_427_Node_Name: Annotated[str, Field(default=...)]

    Outlet_428_Node_Name: Annotated[str, Field(default=...)]

    Outlet_429_Node_Name: Annotated[str, Field(default=...)]

    Outlet_430_Node_Name: Annotated[str, Field(default=...)]

    Outlet_431_Node_Name: Annotated[str, Field(default=...)]

    Outlet_432_Node_Name: Annotated[str, Field(default=...)]

    Outlet_433_Node_Name: Annotated[str, Field(default=...)]

    Outlet_434_Node_Name: Annotated[str, Field(default=...)]

    Outlet_435_Node_Name: Annotated[str, Field(default=...)]

    Outlet_436_Node_Name: Annotated[str, Field(default=...)]

    Outlet_437_Node_Name: Annotated[str, Field(default=...)]

    Outlet_438_Node_Name: Annotated[str, Field(default=...)]

    Outlet_439_Node_Name: Annotated[str, Field(default=...)]

    Outlet_440_Node_Name: Annotated[str, Field(default=...)]

    Outlet_441_Node_Name: Annotated[str, Field(default=...)]

    Outlet_442_Node_Name: Annotated[str, Field(default=...)]

    Outlet_443_Node_Name: Annotated[str, Field(default=...)]

    Outlet_444_Node_Name: Annotated[str, Field(default=...)]

    Outlet_445_Node_Name: Annotated[str, Field(default=...)]

    Outlet_446_Node_Name: Annotated[str, Field(default=...)]

    Outlet_447_Node_Name: Annotated[str, Field(default=...)]

    Outlet_448_Node_Name: Annotated[str, Field(default=...)]

    Outlet_449_Node_Name: Annotated[str, Field(default=...)]

    Outlet_450_Node_Name: Annotated[str, Field(default=...)]

    Outlet_451_Node_Name: Annotated[str, Field(default=...)]

    Outlet_452_Node_Name: Annotated[str, Field(default=...)]

    Outlet_453_Node_Name: Annotated[str, Field(default=...)]

    Outlet_454_Node_Name: Annotated[str, Field(default=...)]

    Outlet_455_Node_Name: Annotated[str, Field(default=...)]

    Outlet_456_Node_Name: Annotated[str, Field(default=...)]

    Outlet_457_Node_Name: Annotated[str, Field(default=...)]

    Outlet_458_Node_Name: Annotated[str, Field(default=...)]

    Outlet_459_Node_Name: Annotated[str, Field(default=...)]

    Outlet_460_Node_Name: Annotated[str, Field(default=...)]

    Outlet_461_Node_Name: Annotated[str, Field(default=...)]

    Outlet_462_Node_Name: Annotated[str, Field(default=...)]

    Outlet_463_Node_Name: Annotated[str, Field(default=...)]

    Outlet_464_Node_Name: Annotated[str, Field(default=...)]

    Outlet_465_Node_Name: Annotated[str, Field(default=...)]

    Outlet_466_Node_Name: Annotated[str, Field(default=...)]

    Outlet_467_Node_Name: Annotated[str, Field(default=...)]

    Outlet_468_Node_Name: Annotated[str, Field(default=...)]

    Outlet_469_Node_Name: Annotated[str, Field(default=...)]

    Outlet_470_Node_Name: Annotated[str, Field(default=...)]

    Outlet_471_Node_Name: Annotated[str, Field(default=...)]

    Outlet_472_Node_Name: Annotated[str, Field(default=...)]

    Outlet_473_Node_Name: Annotated[str, Field(default=...)]

    Outlet_474_Node_Name: Annotated[str, Field(default=...)]

    Outlet_475_Node_Name: Annotated[str, Field(default=...)]

    Outlet_476_Node_Name: Annotated[str, Field(default=...)]

    Outlet_477_Node_Name: Annotated[str, Field(default=...)]

    Outlet_478_Node_Name: Annotated[str, Field(default=...)]

    Outlet_479_Node_Name: Annotated[str, Field(default=...)]

    Outlet_480_Node_Name: Annotated[str, Field(default=...)]

    Outlet_481_Node_Name: Annotated[str, Field(default=...)]

    Outlet_482_Node_Name: Annotated[str, Field(default=...)]

    Outlet_483_Node_Name: Annotated[str, Field(default=...)]

    Outlet_484_Node_Name: Annotated[str, Field(default=...)]

    Outlet_485_Node_Name: Annotated[str, Field(default=...)]

    Outlet_486_Node_Name: Annotated[str, Field(default=...)]

    Outlet_487_Node_Name: Annotated[str, Field(default=...)]

    Outlet_488_Node_Name: Annotated[str, Field(default=...)]

    Outlet_489_Node_Name: Annotated[str, Field(default=...)]

    Outlet_490_Node_Name: Annotated[str, Field(default=...)]

    Outlet_491_Node_Name: Annotated[str, Field(default=...)]

    Outlet_492_Node_Name: Annotated[str, Field(default=...)]

    Outlet_493_Node_Name: Annotated[str, Field(default=...)]

    Outlet_494_Node_Name: Annotated[str, Field(default=...)]

    Outlet_495_Node_Name: Annotated[str, Field(default=...)]

    Outlet_496_Node_Name: Annotated[str, Field(default=...)]

    Outlet_497_Node_Name: Annotated[str, Field(default=...)]

    Outlet_498_Node_Name: Annotated[str, Field(default=...)]

    Outlet_499_Node_Name: Annotated[str, Field(default=...)]

    Outlet_500_Node_Name: Annotated[str, Field(default=...)]