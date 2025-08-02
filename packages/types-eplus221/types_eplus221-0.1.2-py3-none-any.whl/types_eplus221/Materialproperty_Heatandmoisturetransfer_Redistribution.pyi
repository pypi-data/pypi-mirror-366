from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Materialproperty_Heatandmoisturetransfer_Redistribution(EpBunch):
    """HeatBalanceAlgorithm = CombinedHeatAndMoistureFiniteElement solution algorithm only."""

    Material_Name: Annotated[str, Field(default=...)]
    """Moisture Material Name that the moisture properties will be added to."""

    Number_of_Redistribution_points: Annotated[int, Field(default=..., ge=1, le=25)]
    """number of data points"""

    Moisture_Content_1: Annotated[str, Field(default=...)]

    Liquid_Transport_Coefficient_1: Annotated[str, Field(default=...)]

    Moisture_Content_2: Annotated[str, Field()]

    Liquid_Transport_Coefficient_2: Annotated[str, Field()]

    Moisture_Content_3: Annotated[str, Field()]

    Liquid_Transport_Coefficient_3: Annotated[str, Field()]

    Moisture_Content_4: Annotated[str, Field()]

    Liquid_Transport_Coefficient_4: Annotated[str, Field()]

    Moisture_Content_5: Annotated[str, Field()]

    Liquid_Transport_Coefficient_5: Annotated[str, Field()]

    Moisture_Content_6: Annotated[str, Field()]

    Liquid_Transport_Coefficient_6: Annotated[str, Field()]

    Moisture_Content_7: Annotated[str, Field()]

    Liquid_Transport_Coefficient_7: Annotated[str, Field()]

    Moisture_Content_8: Annotated[str, Field()]

    Liquid_Transport_Coefficient_8: Annotated[str, Field()]

    Moisture_Content_9: Annotated[str, Field()]

    Liquid_Transport_Coefficient_9: Annotated[str, Field()]

    Moisture_Content_10: Annotated[str, Field()]

    Liquid_Transport_Coefficient_10: Annotated[str, Field()]

    Moisture_Content_11: Annotated[str, Field()]

    Liquid_Transport_Coefficient_11: Annotated[str, Field()]

    Moisture_Content_12: Annotated[str, Field()]

    Liquid_Transport_Coefficient_12: Annotated[str, Field()]

    Moisture_Content_13: Annotated[str, Field()]

    Liquid_Transport_Coefficient_13: Annotated[str, Field()]

    Moisture_Content_14: Annotated[str, Field()]

    Liquid_Transport_Coefficient_14: Annotated[str, Field()]

    Moisture_Content_15: Annotated[str, Field()]

    Liquid_Transport_Coefficient_15: Annotated[str, Field()]

    Moisture_Content_16: Annotated[str, Field()]

    Liquid_Transport_Coefficient_16: Annotated[str, Field()]

    Moisture_Content_17: Annotated[str, Field()]

    Liquid_Transport_Coefficient_17: Annotated[str, Field()]

    Moisture_Content_18: Annotated[str, Field()]

    Liquid_Transport_Coefficient_18: Annotated[str, Field()]

    Moisture_Content_19: Annotated[str, Field()]

    Liquid_Transport_Coefficient_19: Annotated[str, Field()]

    Moisture_Content_20: Annotated[str, Field()]

    Liquid_Transport_Coefficient_20: Annotated[str, Field()]

    Moisture_Content_21: Annotated[str, Field()]

    Liquid_Transport_Coefficient_21: Annotated[str, Field()]

    Moisture_Content_22: Annotated[str, Field()]

    Liquid_Transport_Coefficient_22: Annotated[str, Field()]

    Moisture_Content_23: Annotated[str, Field()]

    Liquid_Transport_Coefficient_23: Annotated[str, Field()]

    Moisture_Content_24: Annotated[str, Field()]

    Liquid_Transport_Coefficient_24: Annotated[str, Field()]

    Moisture_Content_25: Annotated[str, Field()]

    Liquid_Transport_Coefficient_25: Annotated[str, Field()]