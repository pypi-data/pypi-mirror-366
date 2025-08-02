from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coilsystem_Integratedheatpump_Airsource(EpBunch):
    """This object is used for air-source integrated heat pump, a collection of its working modes."""

    Name: Annotated[str, Field(default=...)]
    """Unique name for this instance of an air-source integrated heat pump."""

    Supply_Hot_Water_Flow_Sensor_Node_Name: Annotated[str, Field(default=...)]

    Space_Cooling_Coil_Name: Annotated[str, Field(default=...)]
    """Must match the name used in the corresponding Coil:Cooling:DX:VariableSpeed object."""

    Space_Heating_Coil_Name: Annotated[str, Field()]
    """Must match the name used in the corresponding Coil:Heating:DX:VariableSpeed object."""

    Dedicated_Water_Heating_Coil_Name: Annotated[str, Field()]
    """Must match the name used in the corresponding Coil:WaterHeating:AirToWaterHeatPump:VariableSpeed object."""

    SCWH_Coil_Name: Annotated[str, Field()]
    """Must match the name used in the corresponding Coil:WaterHeating:AirToWaterHeatPump:VariableSpeed object."""

    SCDWH_Cooling_Coil_Name: Annotated[str, Field()]
    """Must match the name used in the corresponding Coil:Cooling:DX:VariableSpeed object."""

    SCDWH_Water_Heating_Coil_Name: Annotated[str, Field()]
    """Must match the name used in the corresponding Coil:WaterHeating:AirToWaterHeatPump:VariableSpeed object."""

    SHDWH_Heating_Coil_Name: Annotated[str, Field()]
    """Must match the name used in the corresponding Coil:Heating:DX:VariableSpeed object."""

    SHDWH_Water_Heating_Coil_Name: Annotated[str, Field()]
    """Must match the name used in the corresponding Coil:WaterHeating:AirToWaterHeatPump:VariableSpeed object."""

    Indoor_Temperature_Limit_for_SCWH_Mode: Annotated[float, Field(gt=15.0, default=20.0)]
    """Indoor Temperature above which Indoor Overcooling is Allowed during Cooling Operation"""

    Ambient_Temperature_Limit_for_SCWH_Mode: Annotated[float, Field(gt=20.0, default=27.0)]
    """Ambient Temperature above which Indoor Overcooling is Allowed during Cooling Operation"""

    Indoor_Temperature_above_Which_WH_has_Higher_Priority: Annotated[float, Field(gt=15.0, default=20.0)]
    """Indoor Temperature above which Water Heating has the higher priority and Space Heating Call Can be ignored."""

    Ambient_Temperature_above_Which_WH_has_Higher_Priority: Annotated[float, Field(gt=15.0, default=20.0)]
    """Ambient Temperature above which Water Heating has the higher priority and Space Heating Call Can be ignored."""

    Flag_to_Indicate_Load_Control_in_SCWH_Mode: Annotated[int, Field(default=0)]
    """0: match space cooling load in SCWH mode, 1: match water heating load in SCWH mode"""

    Minimum_Speed_Level_for_SCWH_Mode: Annotated[int, Field(gt=0, lt=10, default=1)]

    Maximum_Water_Flow_Volume_before_Switching_from_SCDWH_to_SCWH_Mode: Annotated[float, Field(default=0.0)]

    Minimum_Speed_Level_for_SCDWH_Mode: Annotated[int, Field(gt=0, lt=10, default=1)]

    Maximum_Running_Time_before_Allowing_Electric_Resistance_Heat_Use_during_SHDWH_Mode: Annotated[float, Field(gt=0.0, default=360.0)]

    Minimum_Speed_Level_for_SHDWH_Mode: Annotated[int, Field(gt=0, lt=10, default=1)]