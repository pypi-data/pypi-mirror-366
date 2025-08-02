from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Materialproperty_Heatandmoisturetransfer_Sorptionisotherm(EpBunch):
    """HeatBalanceAlgorithm = CombinedHeatAndMoistureFiniteElement solution algorithm only."""

    Material_Name: Annotated[str, Field(default=...)]
    """The Material Name that the moisture sorption isotherm will be added to."""

    Number_Of_Isotherm_Coordinates: Annotated[int, Field(default=..., ge=1, le=25)]
    """Number of data Coordinates"""

    Relative_Humidity_Fraction_1: Annotated[str, Field(default=...)]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_1: Annotated[str, Field(default=...)]

    Relative_Humidity_Fraction_2: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_2: Annotated[str, Field()]

    Relative_Humidity_Fraction_3: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_3: Annotated[str, Field()]

    Relative_Humidity_Fraction_4: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_4: Annotated[str, Field()]

    Relative_Humidity_Fraction_5: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_5: Annotated[str, Field()]

    Relative_Humidity_Fraction_6: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_6: Annotated[str, Field()]

    Relative_Humidity_Fraction_7: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_7: Annotated[str, Field()]

    Relative_Humidity_Fraction_8: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_8: Annotated[str, Field()]

    Relative_Humidity_Fraction_9: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_9: Annotated[str, Field()]

    Relative_Humidity_Fraction_10: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_10: Annotated[str, Field()]

    Relative_Humidity_Fraction_11: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_11: Annotated[str, Field()]

    Relative_Humidity_Fraction_12: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_12: Annotated[str, Field()]

    Relative_Humidity_Fraction_13: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_13: Annotated[str, Field()]

    Relative_Humidity_Fraction_14: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_14: Annotated[str, Field()]

    Relative_Humidity_Fraction_15: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_15: Annotated[str, Field()]

    Relative_Humidity_Fraction_16: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_16: Annotated[str, Field()]

    Relative_Humidity_Fraction_17: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_17: Annotated[str, Field()]

    Relative_Humidity_Fraction_18: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_18: Annotated[str, Field()]

    Relative_Humidity_Fraction_19: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_19: Annotated[str, Field()]

    Relative_Humidity_Fraction_20: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_20: Annotated[str, Field()]

    Relative_Humidity_Fraction_21: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_21: Annotated[str, Field()]

    Relative_Humidity_Fraction_22: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_22: Annotated[str, Field()]

    Relative_Humidity_Fraction_23: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_23: Annotated[str, Field()]

    Relative_Humidity_Fraction_24: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_24: Annotated[str, Field()]

    Relative_Humidity_Fraction_25: Annotated[str, Field()]
    """The relative humidity is entered as a fraction."""

    Moisture_Content_25: Annotated[str, Field()]