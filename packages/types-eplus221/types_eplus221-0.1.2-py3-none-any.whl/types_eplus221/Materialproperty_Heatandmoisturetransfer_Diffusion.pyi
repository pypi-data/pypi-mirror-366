from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Materialproperty_Heatandmoisturetransfer_Diffusion(EpBunch):
    """HeatBalanceAlgorithm = CombinedHeatAndMoistureFiniteElement solution algorithm only."""

    Material_Name: Annotated[str, Field(default=...)]
    """Moisture Material Name that the moisture properties will be added to."""

    Number_of_Data_Pairs: Annotated[int, Field(default=..., ge=1, le=25)]
    """Water Vapor Diffusion Resistance Factor"""

    Relative_Humidity_Fraction_1: Annotated[str, Field(default=...)]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_1: Annotated[str, Field(default=...)]

    Relative_Humidity_Fraction_2: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_2: Annotated[str, Field()]

    Relative_Humidity_Fraction_3: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_3: Annotated[str, Field()]

    Relative_Humidity_Fraction_4: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_4: Annotated[str, Field()]

    Relative_Humidity_Fraction_5: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_5: Annotated[str, Field()]

    Relative_Humidity_Fraction_6: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_6: Annotated[str, Field()]

    Relative_Humidity_Fraction_7: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_7: Annotated[str, Field()]

    Relative_Humidity_Fraction_8: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_8: Annotated[str, Field()]

    Relative_Humidity_Fraction_9: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_9: Annotated[str, Field()]

    Relative_Humidity_Fraction_10: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_10: Annotated[str, Field()]

    Relative_Humidity_Fraction_11: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_11: Annotated[str, Field()]

    Relative_Humidity_Fraction_12: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_12: Annotated[str, Field()]

    Relative_Humidity_Fraction_13: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_13: Annotated[str, Field()]

    Relative_Humidity_Fraction_14: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_14: Annotated[str, Field()]

    Relative_Humidity_Fraction_15: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_15: Annotated[str, Field()]

    Relative_Humidity_Fraction_16: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_16: Annotated[str, Field()]

    Relative_Humidity_Fraction_17: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_17: Annotated[str, Field()]

    Relative_Humidity_Fraction_18: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_18: Annotated[str, Field()]

    Relative_Humidity_Fraction_19: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_19: Annotated[str, Field()]

    Relative_Humidity_Fraction_20: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_20: Annotated[str, Field()]

    Relative_Humidity_Fraction_21: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_21: Annotated[str, Field()]

    Relative_Humidity_Fraction_22: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_22: Annotated[str, Field()]

    Relative_Humidity_Fraction_23: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_23: Annotated[str, Field()]

    Relative_Humidity_Fraction_24: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_24: Annotated[str, Field()]

    Relative_Humidity_Fraction_25: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Water_Vapor_Diffusion_Resistance_Factor_25: Annotated[str, Field()]