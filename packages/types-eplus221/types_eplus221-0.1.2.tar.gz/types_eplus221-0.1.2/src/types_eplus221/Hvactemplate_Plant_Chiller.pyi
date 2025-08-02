from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_Plant_Chiller(EpBunch):
    """This object adds a chiller to an HVACTemplate:Plant:ChilledWaterLoop."""

    Name: Annotated[str, Field(default=...)]

    Chiller_Type: Annotated[Literal['DistrictChilledWater', 'ElectricCentrifugalChiller', 'ElectricScrewChiller', 'ElectricReciprocatingChiller'], Field(default=...)]

    Capacity: Annotated[str, Field(default='autosize')]

    Nominal_COP: Annotated[str, Field(default=...)]
    """Not applicable if Chiller Type is DistrictChilledWater"""

    Condenser_Type: Annotated[Literal['AirCooled', 'WaterCooled', 'EvaporativelyCooled'], Field(default='WaterCooled')]
    """Not applicable if Chiller Type is DistrictChilledWater"""

    Priority: Annotated[str, Field()]
    """If Chiller Plant Operation Scheme Type=Default"""

    Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized capacity and flow rates"""

    Minimum_Part_Load_Ratio: Annotated[float, Field(ge=0.0, default=0.0)]
    """Part load ratio below which the chiller starts cycling on/off to meet the load."""

    Maximum_Part_Load_Ratio: Annotated[float, Field(gt=0.0, default=1.0)]
    """Maximum allowable part load ratio. Must be greater than or equal to Minimum Part Load Ratio."""

    Optimum_Part_Load_Ratio: Annotated[float, Field(gt=0.0, default=1.0)]
    """Optimum part load ratio where the chiller is most efficient."""

    Minimum_Unloading_Ratio: Annotated[float, Field(ge=0.0, default=0.25)]
    """Part load ratio where the chiller can no longer unload and false loading begins."""

    Leaving_Chilled_Water_Lower_Temperature_Limit: Annotated[float, Field(default=5.0)]