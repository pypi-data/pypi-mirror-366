from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Energymanagementsystem_Meteredoutputvariable(EpBunch):
    """This object sets up an EnergyPlus output variable from an Erl variable"""

    Name: Annotated[str, Field(default=...)]

    EMS_Variable_Name: Annotated[str, Field(default=...)]
    """must be an acceptable EMS variable, no spaces"""

    Update_Frequency: Annotated[Literal['ZoneTimestep', 'SystemTimestep'], Field(default=...)]

    EMS_Program_or_Subroutine_Name: Annotated[str, Field()]
    """optional for global scope variables, required for local scope variables"""

    Resource_Type: Annotated[Literal['Electricity', 'NaturalGas', 'Gasoline', 'Diesel', 'Coal', 'FuelOil#1', 'FuelOil#2', 'Propane', 'OtherFuel1', 'OtherFuel2', 'WaterUse', 'OnSiteWaterProduced', 'MainsWaterSupply', 'RainWaterCollected', 'WellWaterDrawn', 'CondensateWaterCollected', 'EnergyTransfer', 'Steam', 'DistrictCooling', 'DistrictHeating', 'ElectricityProducedOnSite', 'SolarWaterHeating', 'SolarAirHeating'], Field(default=...)]
    """choose the type of fuel, water, electricity, pollution or heat rate that should be metered."""

    Group_Type: Annotated[Literal['Building', 'HVAC', 'Plant', 'System'], Field(default=...)]
    """choose a general classification, building (internal services), HVAC (air systems), or plant (hydronic systems), or system"""

    EndUse_Category: Annotated[Literal['Heating', 'Cooling', 'InteriorLights', 'ExteriorLights', 'InteriorEquipment', 'ExteriorEquipment', 'Fans', 'Pumps', 'HeatRejection', 'Humidifier', 'HeatRecovery', 'WaterSystems', 'Refrigeration', 'OnSiteGeneration', 'HeatingCoils', 'CoolingCoils', 'Chillers', 'Boilers', 'Baseboard', 'HeatRecoveryForCooling', 'HeatRecoveryForHeating'], Field(default=...)]
    """choose how the metered output should be classified for end-use category"""

    EndUse_Subcategory: Annotated[str, Field()]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""

    Units: Annotated[str, Field()]
    """optional but will result in dimensionless units for blank"""