from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Multizone_Windpressurecoefficientvalues(EpBunch):
    """Used only if Wind Pressure Coefficient (WPC) Type = INPUT in the AirflowNetwork:SimulationControl"""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this object."""

    AirflowNetworkMultiZoneWindPressureCoefficientArray_Name: Annotated[str, Field(default=...)]
    """Enter the name of the AirflowNetwork:Multizone:WindPressureCoefficientArray object."""

    Wind_Pressure_Coefficient_Value_1: Annotated[float, Field(default=...)]
    """Enter the WPC Value corresponding to the 1st wind direction."""

    Wind_Pressure_Coefficient_Value_2: Annotated[float, Field(default=...)]
    """Enter the WPC Value corresponding to the 2nd wind direction."""

    Wind_Pressure_Coefficient_Value_3: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 3rd wind direction."""

    Wind_Pressure_Coefficient_Value_4: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 4th wind direction."""

    Wind_Pressure_Coefficient_Value_5: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 5th wind direction."""

    Wind_Pressure_Coefficient_Value_6: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 6th wind direction."""

    Wind_Pressure_Coefficient_Value_7: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 7th wind direction."""

    Wind_Pressure_Coefficient_Value_8: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 8th wind direction."""

    Wind_Pressure_Coefficient_Value_9: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 9th wind direction."""

    Wind_Pressure_Coefficient_Value_10: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 10th wind direction."""

    Wind_Pressure_Coefficient_Value_11: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 11th wind direction."""

    Wind_Pressure_Coefficient_Value_12: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 12th wind direction."""

    Wind_Pressure_Coefficient_Value_13: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 13th wind direction."""

    Wind_Pressure_Coefficient_Value_14: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 14th wind direction."""

    Wind_Pressure_Coefficient_Value_15: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 15th wind direction."""

    Wind_Pressure_Coefficient_Value_16: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 16th wind direction."""

    Wind_Pressure_Coefficient_Value_17: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 17th wind direction."""

    Wind_Pressure_Coefficient_Value_18: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 18th wind direction."""

    Wind_Pressure_Coefficient_Value_19: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 19th wind direction."""

    Wind_Pressure_Coefficient_Value_20: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 20th wind direction."""

    Wind_Pressure_Coefficient_Value_21: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 21st wind direction."""

    Wind_Pressure_Coefficient_Value_22: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 22nd wind direction."""

    Wind_Pressure_Coefficient_Value_23: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 23rd wind direction."""

    Wind_Pressure_Coefficient_Value_24: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 24th wind direction."""

    Wind_Pressure_Coefficient_Value_25: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 25th wind direction."""

    Wind_Pressure_Coefficient_Value_26: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 26th wind direction."""

    Wind_Pressure_Coefficient_Value_27: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 27th wind direction."""

    Wind_Pressure_Coefficient_Value_28: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 28th wind direction."""

    Wind_Pressure_Coefficient_Value_29: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 29th wind direction."""

    Wind_Pressure_Coefficient_Value_30: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 30th wind direction."""

    Wind_Pressure_Coefficient_Value_31: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 31st wind direction."""

    Wind_Pressure_Coefficient_Value_32: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 32nd wind direction."""

    Wind_Pressure_Coefficient_Value_33: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 33rd wind direction."""

    Wind_Pressure_Coefficient_Value_34: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 34th wind direction."""

    Wind_Pressure_Coefficient_Value_35: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 35th wind direction."""

    Wind_Pressure_Coefficient_Value_36: Annotated[float, Field()]
    """Enter the WPC Value corresponding to the 36th wind direction."""