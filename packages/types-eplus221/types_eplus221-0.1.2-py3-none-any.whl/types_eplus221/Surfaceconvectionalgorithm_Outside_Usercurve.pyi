from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceconvectionalgorithm_Outside_Usercurve(EpBunch):
    """Used to describe a custom model equation for surface convection heat transfer coefficient"""

    Name: Annotated[str, Field()]

    Wind_Speed_Type_for_Curve: Annotated[Literal['WeatherFile', 'HeightAdjust', 'ParallelComponent', 'ParallelComponentHeightAdjust'], Field(default='HeightAdjust')]

    Hf_Function_of_Wind_Speed_Curve_Name: Annotated[str, Field()]
    """Curve's "x" is wind speed of the type determined in the previous field (m/s)"""

    Hn_Function_of_Temperature_Difference_Curve_Name: Annotated[str, Field()]
    """Curve's "x" is absolute value of delta-T (Surface temperature minus air temperature, (C))"""

    Hn_Function_of_Temperature_Difference_Divided_by_Height_Curve_Name: Annotated[str, Field()]
    """Curve's "x" is absolute value of delta-T/Height (Surface temp minus Air temp)/(vertical length scale), (C/m)"""