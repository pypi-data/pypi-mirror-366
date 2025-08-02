from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Exterior_Fuelequipment(EpBunch):
    """only used for Meter type reporting, does not affect building loads"""

    Name: Annotated[str, Field(default=...)]

    Fuel_Use_Type: Annotated[Literal['Electricity', 'Water', 'NaturalGas', 'PropaneGas', 'FuelOil#1', 'FuelOil#2', 'Diesel', 'Gasoline', 'Coal', 'OtherFuel1', 'OtherFuel2', 'Steam', 'DistrictHeating', 'DistrictCooling'], Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]
    """units in schedule should be fraction applied to capacity of the exterior fuel equipment, generally (0.0 - 1.0)"""

    Design_Level: Annotated[float, Field(default=..., ge=0)]

    End_Use_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""