from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Materialproperty_Heatandmoisturetransfer_Thermalconductivity(EpBunch):
    """HeatBalanceAlgorithm = CombinedHeatAndMoistureFiniteElement solution algorithm only."""

    Material_Name: Annotated[str, Field(default=...)]
    """Moisture Material Name that the Thermal Conductivity will be added to."""

    Number_of_Thermal_Coordinates: Annotated[int, Field(default=..., ge=1, le=25)]
    """number of data coordinates"""

    Moisture_Content_1: Annotated[str, Field(default=...)]

    Thermal_Conductivity_1: Annotated[str, Field(default=...)]

    Moisture_Content_2: Annotated[str, Field()]

    Thermal_Conductivity_2: Annotated[str, Field()]

    Moisture_Content_3: Annotated[str, Field()]

    Thermal_Conductivity_3: Annotated[str, Field()]

    Moisture_Content_4: Annotated[str, Field()]

    Thermal_Conductivity_4: Annotated[str, Field()]

    Moisture_Content_5: Annotated[str, Field()]

    Thermal_Conductivity_5: Annotated[str, Field()]

    Moisture_Content_6: Annotated[str, Field()]

    Thermal_Conductivity_6: Annotated[str, Field()]

    Moisture_Content_7: Annotated[str, Field()]

    Thermal_Conductivity_7: Annotated[str, Field()]

    Moisture_Content_8: Annotated[str, Field()]

    Thermal_Conductivity_8: Annotated[str, Field()]

    Moisture_Content_9: Annotated[str, Field()]

    Thermal_Conductivity_9: Annotated[str, Field()]

    Moisture_Content_10: Annotated[str, Field()]

    Thermal_Conductivity_10: Annotated[str, Field()]

    Moisture_Content_11: Annotated[str, Field()]

    Thermal_Conductivity_11: Annotated[str, Field()]

    Moisture_Content_12: Annotated[str, Field()]

    Thermal_Conductivity_12: Annotated[str, Field()]

    Moisture_Content_13: Annotated[str, Field()]

    Thermal_Conductivity_13: Annotated[str, Field()]

    Moisture_Content_14: Annotated[str, Field()]

    Thermal_Conductivity_14: Annotated[str, Field()]

    Moisture_Content_15: Annotated[str, Field()]

    Thermal_Conductivity_15: Annotated[str, Field()]

    Moisture_Content_16: Annotated[str, Field()]

    Thermal_Conductivity_16: Annotated[str, Field()]

    Moisture_Content_17: Annotated[str, Field()]

    Thermal_Conductivity_17: Annotated[str, Field()]

    Moisture_Content_18: Annotated[str, Field()]

    Thermal_Conductivity_18: Annotated[str, Field()]

    Moisture_Content_19: Annotated[str, Field()]

    Thermal_Conductivity_19: Annotated[str, Field()]

    Moisture_Content_20: Annotated[str, Field()]

    Thermal_Conductivity_20: Annotated[str, Field()]

    Moisture_Content_21: Annotated[str, Field()]

    Thermal_Conductivity_21: Annotated[str, Field()]

    Moisture_Content_22: Annotated[str, Field()]

    Thermal_Conductivity_22: Annotated[str, Field()]

    Moisture_Content_23: Annotated[str, Field()]

    Thermal_Conductivity_23: Annotated[str, Field()]

    Moisture_Content_24: Annotated[str, Field()]

    Thermal_Conductivity_24: Annotated[str, Field()]

    Moisture_Content_25: Annotated[str, Field()]

    Thermal_Conductivity_25: Annotated[str, Field()]