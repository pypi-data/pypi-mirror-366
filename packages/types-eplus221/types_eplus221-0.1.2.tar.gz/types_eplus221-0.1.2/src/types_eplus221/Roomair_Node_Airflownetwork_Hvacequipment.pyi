from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roomair_Node_Airflownetwork_Hvacequipment(EpBunch):
    """define the zone equipment associated with one particular RoomAir:Node"""

    Name: Annotated[str, Field()]

    ZoneHVAC_or_Air_Terminal_Equipment_Object_Type_1: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump', 'AirTerminal:SingleDuct:Uncontrolled', 'AirTerminal:DualDuct:ConstantVolume', 'AirTerminal:DualDuct:VAV', 'AirTerminal:SingleDuct:ConstantVolume:Reheat', 'AirTerminal:SingleDuct:VAV:Reheat', 'AirTerminal:SingleDuct:VAV:NoReheat', 'AirTerminal:SingleDuct:SeriesPIU:Reheat', 'AirTerminal:SingleDuct:ParallelPIU:Reheat', 'AirTerminal:SingleDuct:ConstantVolume:FourPipeInduction', 'AirTerminal:SingleDuct:VAV:Reheat:VariableSpeedFan', 'AirTerminal:SingleDuct:VAV:HeatAndCool:Reheat', 'AirTerminal:SingleDuct:VAV:HeatAndCool:NoReheat', 'AirTerminal:SingleDuct:ConstantVolume:CooledBeam', 'AirTerminal:DualDuct:VAV:OutdoorAir', 'AirLoopHVACReturnAir'], Field()]

    ZoneHVAC_or_Air_Terminal_Equipment_Object_Name_1: Annotated[str, Field()]
    """for object type AirLoopHVACReturnAir, then enter zone return air node name"""

    Fraction_of_Output_or_Supply_Air_from_HVAC_Equipment_1: Annotated[float, Field(ge=0.0, le=1.0)]

    Fraction_of_Input_or_Return_Air_to_HVAC_Equipment_1: Annotated[float, Field(ge=0.0, le=1.0)]

    ZoneHVAC_or_Air_Terminal_Equipment_Object_Type_2: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump', 'AirTerminal:SingleDuct:Uncontrolled', 'AirTerminal:DualDuct:ConstantVolume', 'AirTerminal:DualDuct:VAV', 'AirTerminal:SingleDuct:ConstantVolume:Reheat', 'AirTerminal:SingleDuct:VAV:Reheat', 'AirTerminal:SingleDuct:VAV:NoReheat', 'AirTerminal:SingleDuct:SeriesPIU:Reheat', 'AirTerminal:SingleDuct:ParallelPIU:Reheat', 'AirTerminal:SingleDuct:ConstantVolume:FourPipeInduction', 'AirTerminal:SingleDuct:VAV:Reheat:VariableSpeedFan', 'AirTerminal:SingleDuct:VAV:HeatAndCool:Reheat', 'AirTerminal:SingleDuct:VAV:HeatAndCool:NoReheat', 'AirTerminal:SingleDuct:ConstantVolume:CooledBeam', 'AirTerminal:DualDuct:VAV:OutdoorAir'], Field()]

    ZoneHVAC_or_Air_Terminal_Equipment_Object_Name_2: Annotated[str, Field()]

    Fraction_of_Output_or_Supply_Air_from_HVAC_Equipment_2: Annotated[float, Field(ge=0.0, le=1.0)]

    Fraction_of_Input_or_Return_Air_to_HVAC_Equipment_2: Annotated[float, Field(ge=0.0, le=1.0)]