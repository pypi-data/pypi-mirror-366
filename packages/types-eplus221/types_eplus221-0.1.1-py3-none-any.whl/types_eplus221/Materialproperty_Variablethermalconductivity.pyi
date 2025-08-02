from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Materialproperty_Variablethermalconductivity(EpBunch):
    """Additional properties for temperature dependent thermal conductivity"""

    Name: Annotated[str, Field(default=...)]
    """Regular Material Name to which the additional properties will be added."""

    Temperature_1: Annotated[float, Field(default=...)]
    """for Temperature-Thermal Conductivity function"""

    Thermal_Conductivity_1: Annotated[str, Field(default=...)]
    """for Temperature-Thermal Conductivity function corresponding to temperature 1"""

    Temperature_2: Annotated[float, Field(default=...)]
    """for Temperature-Thermal Conductivity function"""

    Thermal_Conductivity_2: Annotated[float, Field(default=...)]
    """for Temperature-Thermal Conductivity function corresponding to temperature 2"""

    Temperature_3: Annotated[float, Field(default=...)]
    """for Temperature-Thermal Conductivity function"""

    Thermal_Conductivity_3: Annotated[float, Field(default=...)]
    """for Temperature-Thermal Conductivity function corresponding to temperature 3"""

    Temperature_4: Annotated[float, Field()]
    """for Temperature-Thermal Conductivity function"""

    Thermal_Conductivity_4: Annotated[float, Field()]
    """for Temperature-Thermal Conductivity function corresponding to temperature 4"""

    Temperature_5: Annotated[float, Field()]
    """for Temperature-Thermal Conductivity function"""

    Thermal_Conductivity_5: Annotated[float, Field()]
    """for Temperature-Thermal Conductivity function corresponding to temperature 5"""

    Temperature_6: Annotated[float, Field()]
    """for Temperature-Thermal Conductivity function"""

    Thermal_Conductivity_6: Annotated[float, Field()]
    """for Temperature-Thermal Conductivity function corresponding to temperature 6"""

    Temperature_7: Annotated[float, Field()]
    """for Temperature-Thermal Conductivity function"""

    Thermal_Conductivity_7: Annotated[float, Field()]
    """for Temperature-Thermal Conductivity function corresponding to temperature 7"""

    Temperature_8: Annotated[float, Field()]
    """for Temperature-Thermal Conductivity function"""

    Thermal_Conductivity_8: Annotated[float, Field()]
    """for Temperature-Thermal Conductivity function corresponding to temperature 8"""

    Temperature_9: Annotated[float, Field()]
    """for Temperature-Thermal Conductivity function"""

    Thermal_Conductivity_9: Annotated[str, Field()]
    """for Temperature-Thermal Conductivity function corresponding to temperature 9"""

    Temperature_10: Annotated[float, Field()]
    """for Temperature-Thermal Conductivity function"""

    Thermal_Conductivity_10: Annotated[float, Field()]
    """for Temperature-Thermal Conductivity function corresponding to temperature 10"""