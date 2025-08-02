from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Waterheater_Sizing(EpBunch):
    """This input object is used with WaterHeater:Mixed or"""

    WaterHeater_Name: Annotated[str, Field(default=...)]

    Design_Mode: Annotated[Literal['PeakDraw', 'ResidentialHUD-FHAMinimum', 'PerPerson', 'PerFloorArea', 'PerUnit', 'PerSolarCollectorArea'], Field()]

    Time_Storage_Can_Meet_Peak_Draw: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PeakDraw"""

    Time_for_Tank_Recovery: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PeakDraw"""

    Nominal_Tank_Volume_for_Autosizing_Plant_Connections: Annotated[float, Field()]
    """Only used if Design Mode = PeakDraw and the water heater also"""

    Number_of_Bedrooms: Annotated[int, Field(ge=1)]
    """Only used for Design Mode = ResidentialHUD-FHAMinimum"""

    Number_of_Bathrooms: Annotated[int, Field(ge=1)]
    """Only used for Design Mode = ResidentialHUD-FHAMinimum"""

    Storage_Capacity_per_Person: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PerPerson"""

    Recovery_Capacity_per_Person: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PerPerson"""

    Storage_Capacity_per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PerFloorArea"""

    Recovery_Capacity_per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PerFloorArea"""

    Number_of_Units: Annotated[float, Field()]
    """Only used for Design Mode = PerUnit"""

    Storage_Capacity_per_Unit: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PerUnit"""

    Recovery_Capacity_PerUnit: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PerUnit"""

    Storage_Capacity_per_Collector_Area: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PerSolarCollectorArea"""

    Height_Aspect_Ratio: Annotated[float, Field(ge=0.0)]
    """only used if for WaterHeater:Stratified"""