from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Solarcollectorperformance_Integralcollectorstorage(EpBunch):
    """Thermal and optical performance parameters for a single glazed solar collector with"""

    Name: Annotated[str, Field(default=...)]

    ICS_Collector_Type: Annotated[Literal['RectangularTank'], Field(default='RectangularTank')]
    """Currently only RectangularTank ICS collector type is available."""

    Gross_Area: Annotated[float, Field(gt=0)]

    Collector_Water_Volume: Annotated[float, Field(gt=0)]

    Bottom_Heat_Loss_Conductance: Annotated[float, Field(gt=0, default=0.40)]
    """Heat loss conductance of the collector bottom insulation"""

    Side_Heat_Loss_Conductance: Annotated[float, Field(gt=0, default=0.60)]
    """heat loss conductance of the collector side insulation"""

    Aspect_Ratio: Annotated[float, Field(gt=0.5, lt=1.0, default=0.8)]
    """This value is ratio of the width (short side) to length"""

    Collector_Side_Height: Annotated[float, Field(gt=0, lt=0.30, default=0.20)]
    """This value is used to estimate collector side area for the heat"""

    Thermal_Mass_of_Absorber_Plate: Annotated[float, Field(ge=0, default=0)]
    """Calculated from the specific heat, density and thickness"""

    Number_of_Covers: Annotated[int, Field(ge=1, le=2, default=2)]
    """Number of transparent covers. Common practice is to use low-iron"""

    Cover_Spacing: Annotated[float, Field(gt=0, le=0.20, default=0.05)]
    """The gap between the transparent covers and between the inner cover"""

    Refractive_Index_of_Outer_Cover: Annotated[float, Field(ge=1.0, le=2.0, default=1.526)]
    """Refractive index of outer cover. Typically low-iron glass is used"""

    Extinction_Coefficient_Times_Thickness_of_Outer_Cover: Annotated[float, Field(ge=0., default=0.045)]
    """Clear glass has extinction coefficient of about 15 [1/m]"""

    Emissivity_of_Outer_Cover: Annotated[float, Field(gt=0., lt=1.0, default=0.88)]
    """Thermal emissivity of the outer cover, commonly glass is used as"""

    Refractive_Index_of_Inner_Cover: Annotated[float, Field(ge=1.0, le=2.0, default=1.37)]
    """Typical material is very thin sheet of Teflon (PTFE). The default"""

    Extinction_Coefficient_Times_Thickness_of_the_inner_Cover: Annotated[float, Field(ge=0., default=0.008)]
    """Default inner cover is very thin sheet of Teflon with"""

    Emissivity_of_Inner_Cover: Annotated[float, Field(gt=0., lt=1.0, default=0.88)]
    """Thermal emissivity of the inner cover material"""

    Absorptance_of_Absorber_Plate: Annotated[float, Field(gt=0., lt=1.0, default=0.96)]
    """The absorber plate solar absorptance. Copper is assumed as"""

    Emissivity_of_Absorber_Plate: Annotated[float, Field(gt=0., lt=1.0, default=0.30)]
    """Thermal emissivity of the absorber plate"""