from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coolingtowerperformance_Cooltools(EpBunch):
    """This object is used to define coefficients for the approach temperature"""

    Name: Annotated[str, Field(default=...)]

    Minimum_Inlet_Air_WetBulb_Temperature: Annotated[float, Field(default=...)]
    """Minimum valid inlet air wet-bulb temperature for this approach"""

    Maximum_Inlet_Air_WetBulb_Temperature: Annotated[float, Field(default=...)]
    """Maximum valid inlet air wet-bulb temperature for this approach"""

    Minimum_Range_Temperature: Annotated[float, Field(default=...)]
    """Minimum valid range temperature for this approach temperature"""

    Maximum_Range_Temperature: Annotated[float, Field(default=...)]
    """Maximum valid range temperature for this approach temperature"""

    Minimum_Approach_Temperature: Annotated[float, Field(default=...)]
    """Minimum valid approach temperature for this correlation."""

    Maximum_Approach_Temperature: Annotated[float, Field(default=...)]
    """Maximum valid approach temperature for this correlation."""

    Minimum_Water_Flow_Rate_Ratio: Annotated[float, Field(default=...)]
    """Minimum valid water flow rate ratio for this approach"""

    Maximum_Water_Flow_Rate_Ratio: Annotated[float, Field(default=...)]
    """Maximum valid water flow rate ratio for this approach"""

    Coefficient_1: Annotated[float, Field(default=...)]

    Coefficient_2: Annotated[float, Field(default=...)]

    Coefficient_3: Annotated[float, Field(default=...)]

    Coefficient_4: Annotated[float, Field(default=...)]

    Coefficient_5: Annotated[float, Field(default=...)]

    Coefficient_6: Annotated[float, Field(default=...)]

    Coefficient_7: Annotated[float, Field(default=...)]

    Coefficient_8: Annotated[float, Field(default=...)]

    Coefficient_9: Annotated[float, Field(default=...)]

    Coefficient_10: Annotated[float, Field(default=...)]

    Coefficient_11: Annotated[float, Field(default=...)]

    Coefficient_12: Annotated[float, Field(default=...)]

    Coefficient_13: Annotated[float, Field(default=...)]

    Coefficient_14: Annotated[float, Field(default=...)]

    Coefficient_15: Annotated[float, Field(default=...)]

    Coefficient_16: Annotated[float, Field(default=...)]

    Coefficient_17: Annotated[float, Field(default=...)]

    Coefficient_18: Annotated[float, Field(default=...)]

    Coefficient_19: Annotated[float, Field(default=...)]

    Coefficient_20: Annotated[float, Field(default=...)]

    Coefficient_21: Annotated[float, Field(default=...)]

    Coefficient_22: Annotated[float, Field(default=...)]

    Coefficient_23: Annotated[float, Field(default=...)]

    Coefficient_24: Annotated[float, Field(default=...)]

    Coefficient_25: Annotated[float, Field(default=...)]

    Coefficient_26: Annotated[float, Field(default=...)]

    Coefficient_27: Annotated[float, Field(default=...)]

    Coefficient_28: Annotated[float, Field(default=...)]

    Coefficient_29: Annotated[float, Field(default=...)]

    Coefficient_30: Annotated[float, Field(default=...)]

    Coefficient_31: Annotated[float, Field(default=...)]

    Coefficient_32: Annotated[float, Field(default=...)]

    Coefficient_33: Annotated[float, Field(default=...)]

    Coefficient_34: Annotated[float, Field(default=...)]

    Coefficient_35: Annotated[float, Field(default=...)]