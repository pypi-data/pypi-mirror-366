from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac_Unitaryheatpump_Airtoair_Multispeed(EpBunch):
    """Unitary system, heating and cooling, multi-speed with constant volume supply fan"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Controlling_Zone_Or_Thermostat_Location: Annotated[str, Field(default=...)]

    Supply_Air_Fan_Object_Type: Annotated[Literal['Fan:OnOff', 'Fan:ConstantVolume'], Field(default=...)]
    """Select the type of supply air fan used in this unitary system."""

    Supply_Air_Fan_Name: Annotated[str, Field(default=...)]
    """Enter the name of the supply air fan used in this unitary system."""

    Supply_Air_Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default=...)]
    """Select supply air fan placement as either BlowThrough or DrawThrough."""

    Supply_Air_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """Enter the name of a schedule to control the supply air fan. Schedule values of zero"""

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:DX:MultiSpeed', 'Coil:Heating:Electric:MultiStage', 'Coil:Heating:Gas:MultiStage', 'Coil:Heating:Water', 'Coil:Heating:Steam'], Field(default=...)]
    """Multi Speed DX, Electric, Gas, and Single speed Water and Steam coils"""

    Heating_Coil_Name: Annotated[str, Field(default=...)]

    Minimum_Outdoor_Dry_Bulb_Temperature_For_Compressor_Operation: Annotated[float, Field(default=-8.0)]
    """Needs to match the corresponding minimum outdoor temperature defined"""

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:DX:MultiSpeed'], Field(default=...)]
    """Only works with Coil:Cooling:DX:MultiSpeed"""

    Cooling_Coil_Name: Annotated[str, Field(default=...)]
    """Needs to match in the DX Cooling Coil object"""

    Supplemental_Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:Fuel', 'Coil:Heating:Electric', 'Coil:Heating:Water', 'Coil:Heating:Steam'], Field()]
    """works with gas, electric, hot water and steam heating coils"""

    Supplemental_Heating_Coil_Name: Annotated[str, Field()]
    """Needs to match in the supplemental heating coil object"""

    Maximum_Supply_Air_Temperature_From_Supplemental_Heater: Annotated[float, Field()]

    Maximum_Outdoor_Dry_Bulb_Temperature_For_Supplemental_Heater_Operation: Annotated[float, Field(le=21.0, default=21.0)]

    Auxiliary_On_Cycle_Electric_Power: Annotated[float, Field(ge=0, default=0)]

    Auxiliary_Off_Cycle_Electric_Power: Annotated[float, Field(ge=0, default=0)]

    Design_Heat_Recovery_Water_Flow_Rate: Annotated[float, Field(ge=0.0, default=0.0)]
    """If non-zero, then the heat recovery inlet and outlet node names must be entered."""

    Maximum_Temperature_For_Heat_Recovery: Annotated[str, Field(default='80.0')]

    Heat_Recovery_Water_Inlet_Node_Name: Annotated[str, Field()]

    Heat_Recovery_Water_Outlet_Node_Name: Annotated[str, Field()]

    No_Load_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0)]
    """Only used when the supply air fan operating mode is continuous (see field"""

    Number_Of_Speeds_For_Heating: Annotated[int, Field(default=..., ge=1, le=4)]
    """Enter the number of the following sets of data for air flow rates."""

    Number_Of_Speeds_For_Cooling: Annotated[int, Field(default=..., ge=2, le=4)]
    """Enter the number of the following sets of data for air flow rates."""

    Heating_Speed_1_Supply_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0)]
    """Enter the operating supply air flow rate during heating"""

    Heating_Speed_2_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0)]
    """Enter the operating supply air flow rate during heating"""

    Heating_Speed_3_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0)]
    """Enter the operating supply air flow rate during heating"""

    Heating_Speed_4_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0)]
    """Enter the operating supply air flow rate during heating"""

    Cooling_Speed_1_Supply_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0)]
    """Enter the operating supply air flow rate during cooling"""

    Cooling_Speed_2_Supply_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0)]
    """Enter the operating supply air flow rate during cooling"""

    Cooling_Speed_3_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0)]
    """Enter the operating supply air flow rate during cooling"""

    Cooling_Speed_4_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0)]
    """Enter the operating supply air flow rate during cooling"""