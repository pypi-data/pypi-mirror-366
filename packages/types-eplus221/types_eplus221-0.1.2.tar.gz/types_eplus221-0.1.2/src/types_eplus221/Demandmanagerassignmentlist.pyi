from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Demandmanagerassignmentlist(EpBunch):
    """a list of meters that can be reported are available after a run on"""

    Name: Annotated[str, Field(default=...)]

    Meter_Name: Annotated[str, Field(default=...)]

    Demand_Limit_Schedule_Name: Annotated[str, Field()]

    Demand_Limit_Safety_Fraction: Annotated[float, Field(default=..., ge=0.0)]

    Billing_Period_Schedule_Name: Annotated[str, Field()]
    """This field should reference the same schedule as the month schedule name field of the"""

    Peak_Period_Schedule_Name: Annotated[str, Field()]
    """This field should reference the same schedule as the period schedule name field of the"""

    Demand_Window_Length: Annotated[int, Field(default=..., gt=0)]

    Demand_Manager_Priority: Annotated[Literal['Sequential', 'All'], Field(default=...)]

    DemandManager_1_Object_Type: Annotated[Literal['DemandManager:ExteriorLights', 'DemandManager:Lights', 'DemandManager:ElectricEquipment', 'DemandManager:Thermostats', 'DemandManager:Ventilation'], Field()]

    DemandManager_1_Name: Annotated[str, Field()]

    DemandManager_2_Object_Type: Annotated[Literal['DemandManager:ExteriorLights', 'DemandManager:Lights', 'DemandManager:ElectricEquipment', 'DemandManager:Thermostats', 'DemandManager:Ventilation'], Field()]

    DemandManager_2_Name: Annotated[str, Field()]

    DemandManager_3_Object_Type: Annotated[Literal['DemandManager:ExteriorLights', 'DemandManager:Lights', 'DemandManager:ElectricEquipment', 'DemandManager:Thermostats', 'DemandManager:Ventilation'], Field()]

    DemandManager_3_Name: Annotated[str, Field()]

    DemandManager_4_Object_Type: Annotated[Literal['DemandManager:ExteriorLights', 'DemandManager:Lights', 'DemandManager:ElectricEquipment', 'DemandManager:Thermostats', 'DemandManager:Ventilation'], Field()]

    DemandManager_4_Name: Annotated[str, Field()]

    DemandManager_5_Object_Type: Annotated[Literal['DemandManager:ExteriorLights', 'DemandManager:Lights', 'DemandManager:ElectricEquipment', 'DemandManager:Thermostats', 'DemandManager:Ventilation'], Field()]

    DemandManager_5_Name: Annotated[str, Field()]

    DemandManager_6_Object_Type: Annotated[Literal['DemandManager:ExteriorLights', 'DemandManager:Lights', 'DemandManager:ElectricEquipment', 'DemandManager:Thermostats', 'DemandManager:Ventilation'], Field()]

    DemandManager_6_Name: Annotated[str, Field()]

    DemandManager_7_Object_Type: Annotated[Literal['DemandManager:ExteriorLights', 'DemandManager:Lights', 'DemandManager:ElectricEquipment', 'DemandManager:Thermostats', 'DemandManager:Ventilation'], Field()]

    DemandManager_7_Name: Annotated[str, Field()]

    DemandManager_8_Object_Type: Annotated[Literal['DemandManager:ExteriorLights', 'DemandManager:Lights', 'DemandManager:ElectricEquipment', 'DemandManager:Thermostats', 'DemandManager:Ventilation'], Field()]

    DemandManager_8_Name: Annotated[str, Field()]

    DemandManager_9_Object_Type: Annotated[Literal['DemandManager:ExteriorLights', 'DemandManager:Lights', 'DemandManager:ElectricEquipment', 'DemandManager:Thermostats', 'DemandManager:Ventilation'], Field()]

    DemandManager_9_Name: Annotated[str, Field()]

    DemandManager_10_Object_Type: Annotated[Literal['DemandManager:ExteriorLights', 'DemandManager:Lights', 'DemandManager:ElectricEquipment', 'DemandManager:Thermostats', 'DemandManager:Ventilation'], Field()]

    DemandManager_10_Name: Annotated[str, Field()]