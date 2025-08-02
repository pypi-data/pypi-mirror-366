from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Waterheater_Sizing(EpBunch):
    """This input object is used with WaterHeater:Mixed or"""

    Waterheater_Name: Annotated[str, Field(default=...)]

    Design_Mode: Annotated[Literal['PeakDraw', 'ResidentialHUD-FHAMinimum', 'PerPerson', 'PerFloorArea', 'PerUnit', 'PerSolarCollectorArea'], Field()]

    Time_Storage_Can_Meet_Peak_Draw: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PeakDraw"""

    Time_For_Tank_Recovery: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PeakDraw"""

    Nominal_Tank_Volume_For_Autosizing_Plant_Connections: Annotated[float, Field()]
    """Only used if Design Mode = PeakDraw and the water heater also"""

    Number_Of_Bedrooms: Annotated[int, Field(ge=1)]
    """Only used for Design Mode = ResidentialHUD-FHAMinimum"""

    Number_Of_Bathrooms: Annotated[int, Field(ge=1)]
    """Only used for Design Mode = ResidentialHUD-FHAMinimum"""

    Storage_Capacity_Per_Person: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PerPerson"""

    Recovery_Capacity_Per_Person: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PerPerson"""

    Storage_Capacity_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PerFloorArea"""

    Recovery_Capacity_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PerFloorArea"""

    Number_Of_Units: Annotated[float, Field()]
    """Only used for Design Mode = PerUnit"""

    Storage_Capacity_Per_Unit: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PerUnit"""

    Recovery_Capacity_Perunit: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PerUnit"""

    Storage_Capacity_Per_Collector_Area: Annotated[float, Field(ge=0.0)]
    """Only used for Design Mode = PerSolarCollectorArea"""

    Height_Aspect_Ratio: Annotated[float, Field(ge=0.0)]
    """only used if for WaterHeater:Stratified"""