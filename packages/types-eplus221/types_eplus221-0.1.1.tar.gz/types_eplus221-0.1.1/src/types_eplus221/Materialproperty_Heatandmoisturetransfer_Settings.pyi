from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Materialproperty_Heatandmoisturetransfer_Settings(EpBunch):
    """HeatBalanceAlgorithm = CombinedHeatAndMoistureFiniteElement solution algorithm only."""

    Material_Name: Annotated[str, Field(default=...)]
    """Material Name that the moisture properties will be added to."""

    Porosity: Annotated[float, Field(default=..., ge=0.0, le=1.0)]

    Initial_Water_Content_Ratio: Annotated[float, Field(ge=0.0, default=0.2)]
    """units are the water/material density ratio at the beginning of each run period."""