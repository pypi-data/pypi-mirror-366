from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Availabilitymanagerassignmentlist(EpBunch):
    """Defines the applicable managers used for an AirLoopHVAC or PlantLoop. The priority of"""

    Name: Annotated[str, Field(default=...)]

    Availability_Manager_1_Object_Type: Annotated[Literal['AvailabilityManager:Scheduled', 'AvailabilityManager:ScheduledOn', 'AvailabilityManager:ScheduledOff', 'AvailabilityManager:NightCycle', 'AvailabilityManager:DifferentialThermostat', 'AvailabilityManager:HighTemperatureTurnOff', 'AvailabilityManager:HighTemperatureTurnOn', 'AvailabilityManager:LowTemperatureTurnOff', 'AvailabilityManager:LowTemperatureTurnOn', 'AvailabilityManager:NightVentilation', 'AvailabilityManager:OptimumStart'], Field(default=...)]

    Availability_Manager_1_Name: Annotated[str, Field(default=...)]

    Availability_Manager_2_Object_Type: Annotated[Literal['AvailabilityManager:Scheduled', 'AvailabilityManager:ScheduledOn', 'AvailabilityManager:ScheduledOff', 'AvailabilityManager:NightCycle', 'AvailabilityManager:DifferentialThermostat', 'AvailabilityManager:HighTemperatureTurnOff', 'AvailabilityManager:HighTemperatureTurnOn', 'AvailabilityManager:LowTemperatureTurnOff', 'AvailabilityManager:LowTemperatureTurnOn', 'AvailabilityManager:NightVentilation', 'AvailabilityManager:OptimumStart'], Field()]

    Availability_Manager_2_Name: Annotated[str, Field()]

    Availability_Manager_3_Object_Type: Annotated[Literal['AvailabilityManager:Scheduled', 'AvailabilityManager:ScheduledOn', 'AvailabilityManager:ScheduledOff', 'AvailabilityManager:NightCycle', 'AvailabilityManager:DifferentialThermostat', 'AvailabilityManager:HighTemperatureTurnOff', 'AvailabilityManager:HighTemperatureTurnOn', 'AvailabilityManager:LowTemperatureTurnOff', 'AvailabilityManager:LowTemperatureTurnOn', 'AvailabilityManager:NightVentilation', 'AvailabilityManager:OptimumStart'], Field()]

    Availability_Manager_3_Name: Annotated[str, Field()]

    Availability_Manager_4_Object_Type: Annotated[Literal['AvailabilityManager:Scheduled', 'AvailabilityManager:ScheduledOn', 'AvailabilityManager:ScheduledOff', 'AvailabilityManager:NightCycle', 'AvailabilityManager:DifferentialThermostat', 'AvailabilityManager:HighTemperatureTurnOff', 'AvailabilityManager:HighTemperatureTurnOn', 'AvailabilityManager:LowTemperatureTurnOff', 'AvailabilityManager:LowTemperatureTurnOn', 'AvailabilityManager:NightVentilation', 'AvailabilityManager:OptimumStart'], Field()]

    Availability_Manager_4_Name: Annotated[str, Field()]

    Availability_Manager_5_Object_Type: Annotated[Literal['AvailabilityManager:Scheduled', 'AvailabilityManager:ScheduledOn', 'AvailabilityManager:ScheduledOff', 'AvailabilityManager:NightCycle', 'AvailabilityManager:DifferentialThermostat', 'AvailabilityManager:HighTemperatureTurnOff', 'AvailabilityManager:HighTemperatureTurnOn', 'AvailabilityManager:LowTemperatureTurnOff', 'AvailabilityManager:LowTemperatureTurnOn', 'AvailabilityManager:NightVentilation', 'AvailabilityManager:OptimumStart'], Field()]

    Availability_Manager_5_Name: Annotated[str, Field()]

    Availability_Manager_6_Object_Type: Annotated[Literal['AvailabilityManager:Scheduled', 'AvailabilityManager:ScheduledOn', 'AvailabilityManager:ScheduledOff', 'AvailabilityManager:NightCycle', 'AvailabilityManager:DifferentialThermostat', 'AvailabilityManager:HighTemperatureTurnOff', 'AvailabilityManager:HighTemperatureTurnOn', 'AvailabilityManager:LowTemperatureTurnOff', 'AvailabilityManager:LowTemperatureTurnOn', 'AvailabilityManager:NightVentilation', 'AvailabilityManager:OptimumStart'], Field()]

    Availability_Manager_6_Name: Annotated[str, Field()]