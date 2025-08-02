from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Boiler_Hotwater(EpBunch):
    """This boiler model is an adaptation of the empirical model from the Building"""

    Name: Annotated[str, Field(default=...)]

    Fuel_Type: Annotated[Literal['Electricity', 'NaturalGas', 'PropaneGas', 'FuelOil#1', 'FuelOil#2', 'Coal', 'Diesel', 'Gasoline', 'OtherFuel1', 'OtherFuel2'], Field(default=...)]

    Nominal_Capacity: Annotated[float, Field(ge=0.0)]

    Nominal_Thermal_Efficiency: Annotated[float, Field(default=..., gt=0.0, le=1.0)]
    """Based on the higher heating value of fuel."""

    Efficiency_Curve_Temperature_Evaluation_Variable: Annotated[Literal['EnteringBoiler', 'LeavingBoiler'], Field()]

    Normalized_Boiler_Efficiency_Curve_Name: Annotated[str, Field()]
    """Linear, Quadratic and Cubic efficiency curves are solely a function of PLR."""

    Design_Water_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]

    Minimum_Part_Load_Ratio: Annotated[float, Field(ge=0.0, default=0.0)]

    Maximum_Part_Load_Ratio: Annotated[float, Field(ge=0.0, default=1.0)]

    Optimum_Part_Load_Ratio: Annotated[float, Field(ge=0.0, default=1.0)]

    Boiler_Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Boiler_Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Water_Outlet_Upper_Temperature_Limit: Annotated[float, Field(default=99.9)]

    Boiler_Flow_Mode: Annotated[Literal['ConstantFlow', 'LeavingSetpointModulated', 'NotModulated'], Field(default='NotModulated')]
    """Select operating mode for fluid flow through the boiler. "NotModulated" is for"""

    Parasitic_Electric_Load: Annotated[float, Field(ge=0.0, default=0.0)]

    Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized capacity and flow rates"""

    EndUse_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""