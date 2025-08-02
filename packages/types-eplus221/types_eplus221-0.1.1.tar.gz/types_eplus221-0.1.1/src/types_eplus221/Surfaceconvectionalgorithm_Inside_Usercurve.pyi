from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceconvectionalgorithm_Inside_Usercurve(EpBunch):
    """Used to describe a custom model equation for surface convection heat transfer coefficient"""

    Name: Annotated[str, Field()]

    Reference_Temperature_For_Convection_Heat_Transfer: Annotated[Literal['MeanAirTemperature', 'AdjacentAirTemperature', 'SupplyAirTemperature'], Field()]
    """Controls which temperature is differenced from surface temperature when using the Hc value"""

    Hc_Function_Of_Temperature_Difference_Curve_Name: Annotated[str, Field()]
    """Curve's "x" is absolute value of delta-T (Surface temperature minus reference temperature, (C))"""

    Hc_Function_Of_Temperature_Difference_Divided_By_Height_Curve_Name: Annotated[str, Field()]
    """Curve's "x" is absolute value of delta-T/Height (Surface temp minus Air temp)/(vertical length scale), (C/m)"""

    Hc_Function_Of_Air_Change_Rate_Curve_Name: Annotated[str, Field()]
    """Curve's "x" is mechanical ACH (Air Changes per hour from mechanical air system), (1/hr)"""

    Hc_Function_Of_Air_System_Volume_Flow_Rate_Divided_By_Zone_Perimeter_Length_Curve_Name: Annotated[str, Field()]
    """Curve's "x" is mechanical system air flow rate (m3/s) divided by zone's length along"""