from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_Plant_Boiler(EpBunch):
    """This object adds a boiler to an HVACTemplate:Plant:HotWaterLoop or MixedWaterLoop."""

    Name: Annotated[str, Field(default=...)]

    Boiler_Type: Annotated[Literal['DistrictHotWater', 'HotWaterBoiler', 'CondensingHotWaterBoiler'], Field(default=...)]

    Capacity: Annotated[str, Field(default='autosize')]

    Efficiency: Annotated[str, Field(default='0.8')]
    """Not applicable if Boiler Type is DistrictHotWater"""

    Fuel_Type: Annotated[Literal['Electricity', 'NaturalGas', 'PropaneGas', 'FuelOil#1', 'FuelOil#2', 'Coal', 'Diesel', 'Gasoline', 'OtherFuel1', 'OtherFuel2'], Field()]
    """Not applicable if Boiler Type is DistrictHotWater"""

    Priority: Annotated[str, Field()]
    """If Hot Water Plant Operation Scheme Type=Default"""

    Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized capacity and flow rates"""

    Minimum_Part_Load_Ratio: Annotated[float, Field(ge=0.0, default=0.0)]

    Maximum_Part_Load_Ratio: Annotated[float, Field(ge=0.0, default=1.1)]

    Optimum_Part_Load_Ratio: Annotated[float, Field(ge=0.0, default=1.0)]

    Water_Outlet_Upper_Temperature_Limit: Annotated[float, Field(default=100.0)]

    Template_Plant_Loop_Type: Annotated[Literal['HotWater', 'MixedWater'], Field()]
    """Specifies if this boiler serves a template hot water loop or mixed water loop"""