from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Boiler_Steam(EpBunch):
    """This boiler model is an adaptation of the empirical model from the Building"""

    Name: Annotated[str, Field(default=...)]

    Fuel_Type: Annotated[Literal['Electricity', 'NaturalGas', 'PropaneGas', 'FuelOil#1', 'FuelOil#2', 'Coal', 'Diesel', 'Gasoline', 'OtherFuel1', 'OtherFuel2'], Field(default=...)]

    Maximum_Operating_Pressure: Annotated[str, Field(default='160000')]

    Theoretical_Efficiency: Annotated[float, Field(gt=0.0, le=1.0, default=0.8)]

    Design_Outlet_Steam_Temperature: Annotated[str, Field(default='100')]

    Nominal_Capacity: Annotated[str, Field()]

    Minimum_Part_Load_Ratio: Annotated[str, Field()]

    Maximum_Part_Load_Ratio: Annotated[str, Field()]

    Optimum_Part_Load_Ratio: Annotated[str, Field()]

    Coefficient_1_of_Fuel_Use_Function_of_Part_Load_Ratio_Curve: Annotated[str, Field()]

    Coefficient_2_of_Fuel_Use_Function_of_Part_Load_Ratio_Curve: Annotated[str, Field()]

    Coefficient_3_of_Fuel_Use_Function_of_Part_Load_Ratio_Curve: Annotated[str, Field()]

    Water_Inlet_Node_Name: Annotated[str, Field()]

    Steam_Outlet_Node_Name: Annotated[str, Field()]

    Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized capacity and flow rates"""

    EndUse_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""