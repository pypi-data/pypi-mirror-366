from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Otherequipment(EpBunch):
    """Sets internal gains or losses for "other" equipment in the zone."""

    Name: Annotated[str, Field(default=...)]

    Fuel_Type: Annotated[Literal['None', 'Electricity', 'NaturalGas', 'PropaneGas', 'FuelOil#1', 'FuelOil#2', 'Diesel', 'Gasoline', 'Coal', 'OtherFuel1', 'OtherFuel2', 'Steam', 'DistrictHeating', 'DistrictCooling'], Field()]

    Zone_or_ZoneList_Name: Annotated[str, Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]
    """units in Schedule should be fraction applied to design level of other equipment, generally (0.0 - 1.0)"""

    Design_Level_Calculation_Method: Annotated[Literal['EquipmentLevel', 'Watts/Area', 'Watts/Person', 'Power/Area', 'Power/Person'], Field(default='EquipmentLevel')]
    """The entered calculation method is used to create the maximum amount of other equipment."""

    Design_Level: Annotated[float, Field()]

    Power_per_Zone_Floor_Area: Annotated[float, Field()]

    Power_per_Person: Annotated[float, Field()]

    Fraction_Latent: Annotated[float, Field(ge=0.0, le=1.0, default=0)]

    Fraction_Radiant: Annotated[float, Field(ge=0.0, le=1.0, default=0)]

    Fraction_Lost: Annotated[float, Field(ge=0.0, le=1.0, default=0)]

    Carbon_Dioxide_Generation_Rate: Annotated[float, Field(ge=0.0, le=4.0E-7, default=0.0)]
    """CO2 generation rate per unit of power input"""

    EndUse_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""