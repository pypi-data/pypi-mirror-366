from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Chillerheater_Absorption_Directfired(EpBunch):
    """Direct fired gas absorption chiller-heater using performance curves similar to DOE-2"""

    Name: Annotated[str, Field(default=...)]

    Nominal_Cooling_Capacity: Annotated[str, Field(default='autosize')]

    Heating_to_Cooling_Capacity_Ratio: Annotated[str, Field(default='0.8')]
    """A positive fraction that represents the ratio of the"""

    Fuel_Input_to_Cooling_Output_Ratio: Annotated[str, Field(default='0.97')]
    """The positive fraction that represents the ratio of the"""

    Fuel_Input_to_Heating_Output_Ratio: Annotated[str, Field(default='1.25')]
    """The positive fraction that represents the ratio of the"""

    Electric_Input_to_Cooling_Output_Ratio: Annotated[str, Field(default='0.01')]
    """The positive fraction that represents the ratio of the"""

    Electric_Input_to_Heating_Output_Ratio: Annotated[str, Field(default='0')]
    """The positive fraction that represents the ratio of the"""

    Chilled_Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Chilled_Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Condenser_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Condenser_Outlet_Node_Name: Annotated[str, Field()]
    """Not required if air-cooled"""

    Hot_Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Hot_Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Minimum_Part_Load_Ratio: Annotated[str, Field(default='0.1')]
    """The positive fraction that represents the minimum cooling output possible when"""

    Maximum_Part_Load_Ratio: Annotated[str, Field(default='1.0')]
    """The positive fraction that represents the maximum cooling output possible at"""

    Optimum_Part_Load_Ratio: Annotated[str, Field(default='1.0')]
    """The positive fraction that represents the optimal cooling output at rated"""

    Design_Entering_Condenser_Water_Temperature: Annotated[str, Field(default='29')]
    """The temperature of the water entering the condenser of the chiller when"""

    Design_Leaving_Chilled_Water_Temperature: Annotated[str, Field(default='7')]
    """The temperature of the water leaving the evaporator of the chiller when"""

    Design_Chilled_Water_Flow_Rate: Annotated[str, Field(default='autosize')]
    """For variable volume this is the max flow & for constant flow this is the flow."""

    Design_Condenser_Water_Flow_Rate: Annotated[str, Field(default='autosize')]
    """The water flow rate at design conditions through the condenser."""

    Design_Hot_Water_Flow_Rate: Annotated[str, Field(default='autosize')]
    """The water flow rate at design conditions through the heater side."""

    Cooling_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """The CoolCapFT curve represents the fraction of the cooling capacity of the chiller as it"""

    Fuel_Input_to_Cooling_Output_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """The curve represents the fraction of the fuel input to the chiller at full load as"""

    Fuel_Input_to_Cooling_Output_Ratio_Function_of_Part_Load_Ratio_Curve_Name: Annotated[str, Field()]
    """The curve represents the fraction of the fuel input to the chiller as the load on"""

    Electric_Input_to_Cooling_Output_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """The curve represents the fraction of the electricity to the chiller at full load as"""

    Electric_Input_to_Cooling_Output_Ratio_Function_of_Part_Load_Ratio_Curve_Name: Annotated[str, Field()]
    """The curve represents the fraction of the electricity to the chiller as the load on"""

    Heating_Capacity_Function_of_Cooling_Capacity_Curve_Name: Annotated[str, Field()]
    """The curve represents how the heating capacity of the chiller varies with cooling"""

    Fuel_Input_to_Heat_Output_Ratio_During_Heating_Only_Operation_Curve_Name: Annotated[str, Field()]
    """When the chiller is operating as only a heater, this curve is used to represent the"""

    Temperature_Curve_Input_Variable: Annotated[Literal['LeavingCondenser', 'EnteringCondenser'], Field(default='EnteringCondenser')]
    """Sets the second independent variable in the three temperature dependent performance"""

    Condenser_Type: Annotated[Literal['AirCooled', 'WaterCooled'], Field(default='WaterCooled')]
    """The condenser can either be air cooled or connected to a cooling tower."""

    Chilled_Water_Temperature_Lower_Limit: Annotated[str, Field(default='2.0')]
    """The chilled water supply temperature below which the chiller"""

    Fuel_Higher_Heating_Value: Annotated[str, Field(default='0.0')]
    """Not currently used."""

    Fuel_Type: Annotated[Literal['NaturalGas', 'PropaneGas', 'Diesel', 'Gasoline', 'FuelOil#1', 'FuelOil#2', 'OtherFuel1', 'OtherFuel2'], Field(default='NaturalGas')]

    Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized capacity and flow rates"""