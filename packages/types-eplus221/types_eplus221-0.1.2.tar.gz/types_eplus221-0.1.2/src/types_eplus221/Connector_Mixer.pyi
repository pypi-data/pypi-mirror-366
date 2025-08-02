from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Connector_Mixer(EpBunch):
    """Mix N inlet air/water streams into one. Branch names cannot be duplicated within"""

    Name: Annotated[str, Field(default=...)]

    Outlet_Branch_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_1_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_2_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_3_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_4_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_5_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_6_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_7_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_8_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_9_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_10_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_11_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_12_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_13_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_14_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_15_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_16_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_17_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_18_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_19_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_20_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_21_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_22_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_23_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_24_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_25_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_26_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_27_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_28_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_29_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_30_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_31_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_32_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_33_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_34_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_35_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_36_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_37_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_38_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_39_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_40_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_41_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_42_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_43_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_44_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_45_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_46_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_47_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_48_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_49_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_50_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_51_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_52_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_53_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_54_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_55_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_56_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_57_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_58_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_59_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_60_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_61_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_62_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_63_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_64_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_65_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_66_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_67_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_68_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_69_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_70_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_71_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_72_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_73_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_74_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_75_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_76_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_77_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_78_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_79_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_80_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_81_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_82_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_83_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_84_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_85_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_86_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_87_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_88_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_89_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_90_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_91_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_92_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_93_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_94_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_95_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_96_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_97_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_98_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_99_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_100_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_101_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_102_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_103_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_104_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_105_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_106_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_107_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_108_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_109_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_110_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_111_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_112_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_113_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_114_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_115_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_116_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_117_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_118_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_119_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_120_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_121_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_122_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_123_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_124_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_125_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_126_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_127_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_128_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_129_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_130_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_131_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_132_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_133_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_134_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_135_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_136_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_137_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_138_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_139_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_140_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_141_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_142_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_143_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_144_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_145_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_146_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_147_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_148_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_149_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_150_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_151_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_152_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_153_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_154_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_155_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_156_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_157_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_158_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_159_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_160_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_161_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_162_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_163_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_164_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_165_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_166_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_167_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_168_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_169_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_170_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_171_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_172_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_173_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_174_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_175_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_176_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_177_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_178_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_179_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_180_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_181_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_182_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_183_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_184_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_185_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_186_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_187_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_188_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_189_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_190_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_191_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_192_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_193_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_194_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_195_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_196_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_197_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_198_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_199_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_200_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_201_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_202_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_203_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_204_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_205_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_206_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_207_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_208_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_209_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_210_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_211_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_212_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_213_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_214_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_215_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_216_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_217_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_218_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_219_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_220_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_221_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_222_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_223_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_224_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_225_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_226_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_227_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_228_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_229_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_230_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_231_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_232_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_233_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_234_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_235_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_236_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_237_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_238_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_239_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_240_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_241_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_242_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_243_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_244_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_245_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_246_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_247_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_248_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_249_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_250_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_251_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_252_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_253_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_254_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_255_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_256_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_257_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_258_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_259_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_260_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_261_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_262_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_263_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_264_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_265_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_266_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_267_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_268_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_269_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_270_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_271_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_272_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_273_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_274_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_275_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_276_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_277_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_278_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_279_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_280_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_281_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_282_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_283_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_284_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_285_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_286_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_287_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_288_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_289_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_290_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_291_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_292_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_293_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_294_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_295_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_296_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_297_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_298_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_299_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_300_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_301_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_302_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_303_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_304_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_305_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_306_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_307_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_308_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_309_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_310_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_311_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_312_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_313_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_314_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_315_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_316_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_317_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_318_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_319_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_320_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_321_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_322_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_323_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_324_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_325_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_326_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_327_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_328_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_329_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_330_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_331_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_332_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_333_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_334_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_335_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_336_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_337_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_338_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_339_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_340_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_341_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_342_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_343_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_344_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_345_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_346_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_347_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_348_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_349_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_350_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_351_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_352_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_353_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_354_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_355_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_356_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_357_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_358_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_359_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_360_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_361_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_362_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_363_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_364_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_365_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_366_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_367_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_368_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_369_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_370_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_371_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_372_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_373_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_374_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_375_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_376_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_377_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_378_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_379_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_380_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_381_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_382_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_383_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_384_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_385_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_386_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_387_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_388_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_389_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_390_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_391_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_392_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_393_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_394_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_395_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_396_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_397_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_398_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_399_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_400_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_401_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_402_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_403_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_404_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_405_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_406_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_407_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_408_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_409_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_410_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_411_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_412_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_413_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_414_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_415_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_416_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_417_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_418_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_419_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_420_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_421_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_422_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_423_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_424_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_425_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_426_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_427_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_428_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_429_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_430_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_431_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_432_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_433_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_434_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_435_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_436_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_437_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_438_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_439_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_440_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_441_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_442_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_443_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_444_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_445_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_446_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_447_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_448_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_449_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_450_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_451_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_452_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_453_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_454_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_455_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_456_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_457_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_458_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_459_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_460_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_461_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_462_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_463_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_464_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_465_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_466_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_467_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_468_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_469_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_470_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_471_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_472_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_473_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_474_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_475_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_476_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_477_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_478_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_479_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_480_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_481_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_482_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_483_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_484_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_485_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_486_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_487_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_488_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_489_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_490_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_491_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_492_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_493_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_494_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_495_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_496_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_497_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_498_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_499_Name: Annotated[str, Field(default=...)]

    Inlet_Branch_500_Name: Annotated[str, Field(default=...)]