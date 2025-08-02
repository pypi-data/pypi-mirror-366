from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Materialproperty_Phasechangehysteresis(EpBunch):
    """Additional properties for temperature dependent thermal conductivity"""

    Name: Annotated[str, Field(default=...)]
    """Regular Material Name to which the additional properties will be added."""

    Latent_Heat_During_The_Entire_Phase_Change_Process: Annotated[float, Field(default=..., gt=0)]
    """The total latent heat absorbed or rejected during the transition from solid to liquid, or back"""

    Liquid_State_Thermal_Conductivity: Annotated[float, Field(default=..., gt=0)]
    """The thermal conductivity used by this material when the material is fully liquid"""

    Liquid_State_Density: Annotated[float, Field(default=..., gt=0)]
    """The density used by this material when the material is fully liquid"""

    Liquid_State_Specific_Heat: Annotated[float, Field(default=..., gt=0)]
    """The constant specific heat used for the fully melted (liquid) state"""

    High_Temperature_Difference_Of_Melting_Curve: Annotated[float, Field(default=..., gt=0)]
    """The total melting range of the material is the sum of low and high temperature difference of melting curve."""

    Peak_Melting_Temperature: Annotated[float, Field(default=..., gt=0)]
    """The temperature at which the melting curve peaks"""

    Low_Temperature_Difference_Of_Melting_Curve: Annotated[float, Field(default=..., gt=0)]
    """The total melting range of the material is the sum of low and high temperature difference of melting curve."""

    Solid_State_Thermal_Conductivity: Annotated[float, Field(default=..., gt=0)]
    """The thermal conductivity used by this material when the material is fully solid"""

    Solid_State_Density: Annotated[float, Field(default=..., gt=0)]
    """The density used by this material when the material is fully solid"""

    Solid_State_Specific_Heat: Annotated[float, Field(default=..., gt=0)]
    """The constant specific heat used for the fully frozen (crystallized) state"""

    High_Temperature_Difference_Of_Freezing_Curve: Annotated[float, Field(default=..., gt=0)]
    """The total freezing range of the material is the sum of low and high temperature difference of freezing curve."""

    Peak_Freezing_Temperature: Annotated[float, Field(default=..., gt=0)]
    """The temperature at which the freezing curve peaks"""

    Low_Temperature_Difference_Of_Freezing_Curve: Annotated[float, Field(default=..., gt=0)]
    """The total freezing range of the material is the sum of low and high temperature difference of freezing curve."""