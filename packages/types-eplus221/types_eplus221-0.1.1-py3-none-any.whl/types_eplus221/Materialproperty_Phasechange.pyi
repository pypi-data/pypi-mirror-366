from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Materialproperty_Phasechange(EpBunch):
    """Additional properties for temperature dependent thermal conductivity"""

    Name: Annotated[str, Field(default=...)]
    """Regular Material Name to which the additional properties will be added."""

    Temperature_Coefficient_For_Thermal_Conductivity: Annotated[float, Field(default=0.0)]
    """The base temperature is 20C."""

    Temperature_1: Annotated[float, Field(default=...)]
    """for Temperature-enthalpy function"""

    Enthalpy_1: Annotated[str, Field(default=...)]
    """for Temperature-enthalpy function corresponding to temperature 1"""

    Temperature_2: Annotated[float, Field(default=...)]
    """for Temperature-enthalpy function"""

    Enthalpy_2: Annotated[float, Field(default=...)]
    """for Temperature-enthalpy function corresponding to temperature 2"""

    Temperature_3: Annotated[float, Field(default=...)]
    """for Temperature-enthalpy function"""

    Enthalpy_3: Annotated[float, Field(default=...)]
    """for Temperature-enthalpy function corresponding to temperature 3"""

    Temperature_4: Annotated[float, Field()]
    """for Temperature-enthalpy function"""

    Enthalpy_4: Annotated[float, Field()]
    """for Temperature-enthalpy function corresponding to temperature 4"""

    Temperature_5: Annotated[float, Field()]
    """for Temperature-enthalpy function"""

    Enthalpy_5: Annotated[float, Field()]
    """for Temperature-enthalpy function corresponding to temperature 5"""

    Temperature_6: Annotated[float, Field()]
    """for Temperature-enthalpy function"""

    Enthalpy_6: Annotated[float, Field()]
    """for Temperature-enthalpy function corresponding to temperature 6"""

    Temperature_7: Annotated[float, Field()]
    """for Temperature-enthalpy function"""

    Enthalpy_7: Annotated[float, Field()]
    """for Temperature-enthalpy function corresponding to temperature 7"""

    Temperature_8: Annotated[float, Field()]
    """for Temperature-enthalpy function"""

    Enthalpy_8: Annotated[float, Field()]
    """for Temperature-enthalpy function corresponding to temperature 8"""

    Temperature_9: Annotated[float, Field()]
    """for Temperature-enthalpy function"""

    Enthalpy_9: Annotated[str, Field()]
    """for Temperature-enthalpy function corresponding to temperature 1"""

    Temperature_10: Annotated[float, Field()]
    """for Temperature-enthalpy function"""

    Enthalpy_10: Annotated[float, Field()]
    """for Temperature-enthalpy function corresponding to temperature 2"""

    Temperature_11: Annotated[float, Field()]
    """for Temperature-enthalpy function"""

    Enthalpy_11: Annotated[float, Field()]
    """for Temperature-enthalpy function corresponding to temperature 3"""

    Temperature_12: Annotated[float, Field()]
    """for Temperature-enthalpy function"""

    Enthalpy_12: Annotated[float, Field()]
    """for Temperature-enthalpy function corresponding to temperature 14"""

    Temperature_13: Annotated[float, Field()]
    """for Temperature-enthalpy function"""

    Enthalpy_13: Annotated[float, Field()]
    """for Temperature-enthalpy function corresponding to temperature 15"""

    Temperature_14: Annotated[float, Field()]
    """for Temperature-enthalpy function"""

    Enthalpy_14: Annotated[float, Field()]
    """for Temperature-enthalpy function corresponding to temperature 16"""

    Temperature_15: Annotated[float, Field()]
    """for Temperature-enthalpy function"""

    Enthalpy_15: Annotated[float, Field()]
    """for Temperature-enthalpy function corresponding to temperature 17"""

    Temperature_16: Annotated[float, Field()]
    """for Temperature-enthalpy function"""

    Enthalpy_16: Annotated[float, Field()]
    """for Temperature-enthalpy function corresponding to temperature 16"""