from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Spectrumdata(EpBunch):
    """Spectrum Data Type is followed by up to 107 sets of normal-incidence measured values of"""

    Name: Annotated[str, Field(default=...)]

    Spectrum_Data_Type: Annotated[Literal['Solar', 'Visible'], Field(default=...)]

    Wavelength: Annotated[float, Field()]

    Spectrum: Annotated[float, Field()]

    Wavelength: Annotated[float, Field()]

    Spectrum: Annotated[float, Field()]

    Wavelength: Annotated[float, Field()]

    Spectrum: Annotated[float, Field()]

    N7: Annotated[str, Field()]

    N8: Annotated[str, Field()]
    """fields as indicated"""

    N9: Annotated[str, Field()]

    N10: Annotated[str, Field()]
    """fields as indicated"""

    N11: Annotated[str, Field()]

    N12: Annotated[str, Field()]
    """fields as indicated"""

    N13: Annotated[str, Field()]

    N14: Annotated[str, Field()]
    """fields as indicated"""

    N15: Annotated[str, Field()]

    N16: Annotated[str, Field()]
    """fields as indicated"""

    N17: Annotated[str, Field()]

    N18: Annotated[str, Field()]
    """fields as indicated"""

    N19: Annotated[str, Field()]

    N20: Annotated[str, Field()]
    """fields as indicated"""

    N21: Annotated[str, Field()]

    N22: Annotated[str, Field()]
    """fields as indicated"""

    N23: Annotated[str, Field()]

    N24: Annotated[str, Field()]
    """fields as indicated"""

    N25: Annotated[str, Field()]

    N26: Annotated[str, Field()]
    """fields as indicated"""

    N27: Annotated[str, Field()]

    N28: Annotated[str, Field()]
    """fields as indicated"""

    N29: Annotated[str, Field()]

    N30: Annotated[str, Field()]
    """fields as indicated"""

    N31: Annotated[str, Field()]

    N32: Annotated[str, Field()]
    """fields as indicated"""

    N33: Annotated[str, Field()]

    N34: Annotated[str, Field()]
    """fields as indicated"""

    N35: Annotated[str, Field()]

    N36: Annotated[str, Field()]
    """fields as indicated"""

    N37: Annotated[str, Field()]

    N38: Annotated[str, Field()]
    """fields as indicated"""

    N39: Annotated[str, Field()]

    N40: Annotated[str, Field()]
    """fields as indicated"""

    N41: Annotated[str, Field()]

    N42: Annotated[str, Field()]
    """fields as indicated"""

    N43: Annotated[str, Field()]

    N44: Annotated[str, Field()]
    """fields as indicated"""

    N45: Annotated[str, Field()]

    N46: Annotated[str, Field()]
    """fields as indicated"""

    N47: Annotated[str, Field()]

    N48: Annotated[str, Field()]
    """fields as indicated"""

    N49: Annotated[str, Field()]

    N50: Annotated[str, Field()]
    """fields as indicated"""

    N51: Annotated[str, Field()]

    N52: Annotated[str, Field()]
    """fields as indicated"""

    N53: Annotated[str, Field()]

    N54: Annotated[str, Field()]
    """fields as indicated"""

    N55: Annotated[str, Field()]

    N56: Annotated[str, Field()]
    """fields as indicated"""

    N57: Annotated[str, Field()]

    N58: Annotated[str, Field()]
    """fields as indicated"""

    N59: Annotated[str, Field()]

    N60: Annotated[str, Field()]
    """fields as indicated"""

    N61: Annotated[str, Field()]

    N62: Annotated[str, Field()]
    """fields as indicated"""

    N63: Annotated[str, Field()]

    N64: Annotated[str, Field()]
    """fields as indicated"""

    N65: Annotated[str, Field()]

    N66: Annotated[str, Field()]
    """fields as indicated"""

    N67: Annotated[str, Field()]

    N68: Annotated[str, Field()]
    """fields as indicated"""

    N69: Annotated[str, Field()]

    N70: Annotated[str, Field()]
    """fields as indicated"""

    N71: Annotated[str, Field()]

    N72: Annotated[str, Field()]
    """fields as indicated"""

    N73: Annotated[str, Field()]

    N74: Annotated[str, Field()]
    """fields as indicated"""

    N75: Annotated[str, Field()]

    N76: Annotated[str, Field()]
    """fields as indicated"""

    N77: Annotated[str, Field()]

    N78: Annotated[str, Field()]
    """fields as indicated"""

    N79: Annotated[str, Field()]

    N80: Annotated[str, Field()]
    """fields as indicated"""

    N81: Annotated[str, Field()]

    N82: Annotated[str, Field()]
    """fields as indicated"""

    N83: Annotated[str, Field()]

    N84: Annotated[str, Field()]
    """fields as indicated"""

    N85: Annotated[str, Field()]

    N86: Annotated[str, Field()]
    """fields as indicated"""

    N87: Annotated[str, Field()]

    N88: Annotated[str, Field()]
    """fields as indicated"""

    N89: Annotated[str, Field()]

    N90: Annotated[str, Field()]
    """fields as indicated"""

    N91: Annotated[str, Field()]

    N92: Annotated[str, Field()]
    """fields as indicated"""

    N93: Annotated[str, Field()]

    N94: Annotated[str, Field()]
    """fields as indicated"""

    N95: Annotated[str, Field()]

    N96: Annotated[str, Field()]
    """fields as indicated"""

    N97: Annotated[str, Field()]

    N98: Annotated[str, Field()]
    """fields as indicated"""

    N99: Annotated[str, Field()]

    N100: Annotated[str, Field()]
    """fields as indicated"""

    N101: Annotated[str, Field()]

    N102: Annotated[str, Field()]
    """fields as indicated"""

    N103: Annotated[str, Field()]

    N104: Annotated[str, Field()]
    """fields as indicated"""

    N105: Annotated[str, Field()]

    N106: Annotated[str, Field()]
    """fields as indicated"""

    N107: Annotated[str, Field()]

    N108: Annotated[str, Field()]
    """fields as indicated"""

    N109: Annotated[str, Field()]

    N110: Annotated[str, Field()]
    """fields as indicated"""

    N111: Annotated[str, Field()]

    N112: Annotated[str, Field()]
    """fields as indicated"""

    N113: Annotated[str, Field()]

    N114: Annotated[str, Field()]
    """fields as indicated"""

    N115: Annotated[str, Field()]

    N116: Annotated[str, Field()]
    """fields as indicated"""

    N117: Annotated[str, Field()]

    N118: Annotated[str, Field()]
    """fields as indicated"""

    N119: Annotated[str, Field()]

    N120: Annotated[str, Field()]
    """fields as indicated"""

    N121: Annotated[str, Field()]

    N122: Annotated[str, Field()]
    """fields as indicated"""

    N123: Annotated[str, Field()]

    N124: Annotated[str, Field()]
    """fields as indicated"""

    N125: Annotated[str, Field()]

    N126: Annotated[str, Field()]
    """fields as indicated"""

    N127: Annotated[str, Field()]

    N128: Annotated[str, Field()]
    """fields as indicated"""

    N129: Annotated[str, Field()]

    N130: Annotated[str, Field()]
    """fields as indicated"""

    N131: Annotated[str, Field()]

    N132: Annotated[str, Field()]
    """fields as indicated"""

    N133: Annotated[str, Field()]

    N134: Annotated[str, Field()]
    """fields as indicated"""

    N135: Annotated[str, Field()]

    N136: Annotated[str, Field()]
    """fields as indicated"""

    N137: Annotated[str, Field()]

    N138: Annotated[str, Field()]
    """fields as indicated"""

    N139: Annotated[str, Field()]

    N140: Annotated[str, Field()]
    """fields as indicated"""

    N141: Annotated[str, Field()]

    N142: Annotated[str, Field()]
    """fields as indicated"""

    N143: Annotated[str, Field()]

    N144: Annotated[str, Field()]
    """fields as indicated"""

    N145: Annotated[str, Field()]

    N146: Annotated[str, Field()]
    """fields as indicated"""

    N147: Annotated[str, Field()]

    N148: Annotated[str, Field()]
    """fields as indicated"""

    N149: Annotated[str, Field()]

    N150: Annotated[str, Field()]
    """fields as indicated"""

    N151: Annotated[str, Field()]

    N152: Annotated[str, Field()]
    """fields as indicated"""

    N153: Annotated[str, Field()]

    N154: Annotated[str, Field()]
    """fields as indicated"""

    N155: Annotated[str, Field()]

    N156: Annotated[str, Field()]
    """fields as indicated"""

    N157: Annotated[str, Field()]

    N158: Annotated[str, Field()]
    """fields as indicated"""

    N159: Annotated[str, Field()]

    N160: Annotated[str, Field()]
    """fields as indicated"""

    N161: Annotated[str, Field()]

    N162: Annotated[str, Field()]
    """fields as indicated"""

    N163: Annotated[str, Field()]

    N164: Annotated[str, Field()]
    """fields as indicated"""

    N165: Annotated[str, Field()]

    N166: Annotated[str, Field()]
    """fields as indicated"""

    N167: Annotated[str, Field()]

    N168: Annotated[str, Field()]
    """fields as indicated"""

    N169: Annotated[str, Field()]

    N170: Annotated[str, Field()]
    """fields as indicated"""

    N171: Annotated[str, Field()]

    N172: Annotated[str, Field()]
    """fields as indicated"""

    N173: Annotated[str, Field()]

    N174: Annotated[str, Field()]
    """fields as indicated"""

    N175: Annotated[str, Field()]

    N176: Annotated[str, Field()]
    """fields as indicated"""

    N177: Annotated[str, Field()]

    N178: Annotated[str, Field()]
    """fields as indicated"""

    N179: Annotated[str, Field()]

    N180: Annotated[str, Field()]
    """fields as indicated"""

    N181: Annotated[str, Field()]

    N182: Annotated[str, Field()]
    """fields as indicated"""

    N183: Annotated[str, Field()]

    N184: Annotated[str, Field()]
    """fields as indicated"""

    N185: Annotated[str, Field()]

    N186: Annotated[str, Field()]
    """fields as indicated"""

    N187: Annotated[str, Field()]

    N188: Annotated[str, Field()]
    """fields as indicated"""

    N189: Annotated[str, Field()]

    N190: Annotated[str, Field()]
    """fields as indicated"""

    N191: Annotated[str, Field()]

    N192: Annotated[str, Field()]
    """fields as indicated"""

    N193: Annotated[str, Field()]

    N194: Annotated[str, Field()]
    """fields as indicated"""

    N195: Annotated[str, Field()]

    N196: Annotated[str, Field()]
    """fields as indicated"""

    N197: Annotated[str, Field()]

    N198: Annotated[str, Field()]
    """fields as indicated"""

    N199: Annotated[str, Field()]

    N200: Annotated[str, Field()]
    """fields as indicated"""

    N201: Annotated[str, Field()]

    N202: Annotated[str, Field()]
    """fields as indicated"""

    N203: Annotated[str, Field()]

    N204: Annotated[str, Field()]
    """fields as indicated"""

    N205: Annotated[str, Field()]

    N206: Annotated[str, Field()]
    """fields as indicated"""

    N207: Annotated[str, Field()]

    N208: Annotated[str, Field()]
    """fields as indicated"""

    N209: Annotated[str, Field()]

    N210: Annotated[str, Field()]
    """fields as indicated"""

    N211: Annotated[str, Field()]

    N212: Annotated[str, Field()]
    """fields as indicated"""

    N213: Annotated[str, Field()]

    N214: Annotated[str, Field()]
    """fields as indicated"""