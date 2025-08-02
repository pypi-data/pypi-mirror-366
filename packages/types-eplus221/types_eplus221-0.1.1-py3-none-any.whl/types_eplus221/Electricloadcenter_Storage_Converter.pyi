from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Electricloadcenter_Storage_Converter(EpBunch):
    """This model is for converting AC to DC for grid-supplied charging of DC storage"""

    Name: Annotated[str, Field()]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Power_Conversion_Efficiency_Method: Annotated[Literal['SimpleFixed', 'FunctionOfPower'], Field(default='SimpleFixed')]
    """SimpleFixed indicates power conversion losses are based on Simple Fixed Efficiency"""

    Simple_Fixed_Efficiency: Annotated[float, Field(gt=0.0, le=1.0, default=0.95)]
    """Constant efficiency for conversion of AC to DC at all power levels."""

    Design_Maximum_Continuous_Input_Power: Annotated[float, Field()]
    """Required field when Power Conversion Efficiency Method is set to FunctionOfPower."""

    Efficiency_Function_Of_Power_Curve_Name: Annotated[str, Field()]
    """Curve or table with a single independent variable that describes efficiency as a function of normalized power."""

    Ancillary_Power_Consumed_In_Standby: Annotated[float, Field()]
    """Optional standby power consumed when converter is available but no power is being conditioned."""

    Zone_Name: Annotated[str, Field()]
    """enter name of zone to receive converter losses as heat"""

    Radiative_Fraction: Annotated[str, Field()]
    """fraction of zone heat gains treated as thermal radiation"""