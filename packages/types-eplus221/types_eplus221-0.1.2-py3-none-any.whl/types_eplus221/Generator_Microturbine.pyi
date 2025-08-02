from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Generator_Microturbine(EpBunch):
    """MicroTurbine generators are small combustion turbines (e.g., 25kW to 500kW). The model"""

    Name: Annotated[str, Field(default=...)]

    Reference_Electrical_Power_Output: Annotated[float, Field(default=..., gt=0.0)]

    Minimum_Full_Load_Electrical_Power_Output: Annotated[float, Field(ge=0.0, default=0.0)]

    Maximum_Full_Load_Electrical_Power_Output: Annotated[float, Field(gt=0.0)]
    """If left blank, Maximum Full Load Electrical Power Output will be set"""

    Reference_Electrical_Efficiency_Using_Lower_Heating_Value: Annotated[float, Field(default=..., gt=0.0, le=1.0)]
    """Electric power output divided by fuel energy input (LHV basis)"""

    Reference_Combustion_Air_Inlet_Temperature: Annotated[float, Field(default=15.0)]

    Reference_Combustion_Air_Inlet_Humidity_Ratio: Annotated[float, Field(gt=0.0, default=0.00638)]

    Reference_Elevation: Annotated[float, Field(ge=-300.0, default=0.0)]

    Electrical_Power_Function_of_Temperature_and_Elevation_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*T + c*T**2 + d*Elev + e*Elev**2 + f*T*Elev"""

    Electrical_Efficiency_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """Quadratic curve = a + b*T + c*T**2"""

    Electrical_Efficiency_Function_of_Part_Load_Ratio_Curve_Name: Annotated[str, Field(default=...)]
    """Quadratic curve = a + b*PLR + c*PLR**2"""

    Fuel_Type: Annotated[Literal['NaturalGas', 'PropaneGas'], Field(default='NaturalGas')]

    Fuel_Higher_Heating_Value: Annotated[float, Field(gt=0.0, default=50000)]

    Fuel_Lower_Heating_Value: Annotated[float, Field(gt=0.0, default=45450)]

    Standby_Power: Annotated[float, Field(ge=0.0, default=0.0)]
    """Electric power consumed when the generator is available but not being called"""

    Ancillary_Power: Annotated[float, Field(ge=0.0, default=0.0)]
    """Electric power consumed by ancillary equipment (e.g., external fuel pressurization pump)."""

    Ancillary_Power_Function_of_Fuel_Input_Curve_Name: Annotated[str, Field()]
    """Quadratic curve = a + b*mdot + c*mdot**2"""

    Heat_Recovery_Water_Inlet_Node_Name: Annotated[str, Field()]

    Heat_Recovery_Water_Outlet_Node_Name: Annotated[str, Field()]

    Reference_Thermal_Efficiency_Using_Lower_Heat_Value: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Reference thermal efficiency (heat recovery to water) based on the"""

    Reference_Inlet_Water_Temperature: Annotated[float, Field()]

    Heat_Recovery_Water_Flow_Operating_Mode: Annotated[Literal['PlantControl', 'InternalControl'], Field(default='PlantControl')]
    """PlantControl means the heat recovery water flow rate is determined by the plant,"""

    Reference_Heat_Recovery_Water_Flow_Rate: Annotated[float, Field(gt=0.0)]

    Heat_Recovery_Water_Flow_Rate_Function_of_Temperature_and_Power_Curve_Name: Annotated[str, Field()]
    """curve = a + b*T + c*T**2 + d*Pnet + e*Pnet + f*T*Pnet"""

    Thermal_Efficiency_Function_of_Temperature_and_Elevation_Curve_Name: Annotated[str, Field()]
    """Bicubic curve = a + b*T + c*T**2 + d*Elev + e*Elev**2 + f*T*Elev + g*T**3 + h*Elev**3 + i*T**2*Elev + j*T*Elev**2"""

    Heat_Recovery_Rate_Function_of_Part_Load_Ratio_Curve_Name: Annotated[str, Field()]
    """Quadratic curve = a + b*PLR + c*PLR**2"""

    Heat_Recovery_Rate_Function_of_Inlet_Water_Temperature_Curve_Name: Annotated[str, Field()]
    """Quadratic curve = a + b*T + c*T**2"""

    Heat_Recovery_Rate_Function_of_Water_Flow_Rate_Curve_Name: Annotated[str, Field()]
    """Quadratic curve = a + b*Flow + c*Flow**2"""

    Minimum_Heat_Recovery_Water_Flow_Rate: Annotated[float, Field(ge=0.0, default=0.0)]

    Maximum_Heat_Recovery_Water_Flow_Rate: Annotated[float, Field(ge=0.0, default=0.0)]

    Maximum_Heat_Recovery_Water_Temperature: Annotated[float, Field()]

    Combustion_Air_Inlet_Node_Name: Annotated[str, Field()]
    """Must be an outdoor air node."""

    Combustion_Air_Outlet_Node_Name: Annotated[str, Field()]

    Reference_Exhaust_Air_Mass_Flow_Rate: Annotated[float, Field(gt=0.0)]

    Exhaust_Air_Flow_Rate_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """Quadratic curve = a + b*T + c*T**2"""

    Exhaust_Air_Flow_Rate_Function_of_Part_Load_Ratio_Curve_Name: Annotated[str, Field()]
    """Quadratic curve = a + b*PLR + c*PLR**2"""

    Nominal_Exhaust_Air_Outlet_Temperature: Annotated[float, Field()]
    """Exhaust air outlet temperature at reference conditions."""

    Exhaust_Air_Temperature_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """Quadratic curve = a + b*T + c*T**2"""

    Exhaust_Air_Temperature_Function_of_Part_Load_Ratio_Curve_Name: Annotated[str, Field()]
    """Quadratic curve = a + b*PLR + c*PLR**2"""