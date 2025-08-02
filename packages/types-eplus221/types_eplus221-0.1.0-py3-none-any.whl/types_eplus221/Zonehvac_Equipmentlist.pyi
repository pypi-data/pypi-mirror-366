from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Equipmentlist(EpBunch):
    """List equipment in simulation order. Note that an ZoneHVAC:AirDistributionUnit or"""

    Name: Annotated[str, Field(default=...)]

    Load_Distribution_Scheme: Annotated[Literal['SequentialLoad', 'UniformLoad', 'UniformPLR', 'SequentialUniformPLR'], Field(default='SequentialLoad')]

    Zone_Equipment_1_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field(default=...)]

    Zone_Equipment_1_Name: Annotated[str, Field(default=...)]

    Zone_Equipment_1_Cooling_Sequence: Annotated[int, Field(default=..., ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_1_Heating_Or_No_Load_Sequence: Annotated[int, Field(default=..., ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_1_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_1_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""

    Zone_Equipment_2_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field()]

    Zone_Equipment_2_Name: Annotated[str, Field()]

    Zone_Equipment_2_Cooling_Sequence: Annotated[int, Field(ge=1)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_2_Heating_Or_No_Load_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_2_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_2_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""

    Zone_Equipment_3_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field()]

    Zone_Equipment_3_Name: Annotated[str, Field()]

    Zone_Equipment_3_Cooling_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_3_Heating_Or_No_Load_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_3_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_3_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""

    Zone_Equipment_4_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field()]

    Zone_Equipment_4_Name: Annotated[str, Field()]

    Zone_Equipment_4_Cooling_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_4_Heating_Or_No_Load_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_4_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_4_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""

    Zone_Equipment_5_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field()]

    Zone_Equipment_5_Name: Annotated[str, Field()]

    Zone_Equipment_5_Cooling_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_5_Heating_Or_No_Load_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_5_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_5_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""

    Zone_Equipment_6_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field()]

    Zone_Equipment_6_Name: Annotated[str, Field()]

    Zone_Equipment_6_Cooling_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_6_Heating_Or_No_Load_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_6_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_6_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""

    Zone_Equipment_7_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field()]

    Zone_Equipment_7_Name: Annotated[str, Field()]

    Zone_Equipment_7_Cooling_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_7_Heating_Or_No_Load_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_7_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_7_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""

    Zone_Equipment_8_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field()]

    Zone_Equipment_8_Name: Annotated[str, Field()]

    Zone_Equipment_8_Cooling_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_8_Heating_Or_No_Load_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_8_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_8_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""

    Zone_Equipment_9_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field()]

    Zone_Equipment_9_Name: Annotated[str, Field()]

    Zone_Equipment_9_Cooling_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_9_Heating_Or_No_Load_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_9_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_9_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""

    Zone_Equipment_10_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field()]

    Zone_Equipment_10_Name: Annotated[str, Field()]

    Zone_Equipment_10_Cooling_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_10_Heating_Or_No_Load_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_10_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_10_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""

    Zone_Equipment_11_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field()]

    Zone_Equipment_11_Name: Annotated[str, Field()]

    Zone_Equipment_11_Cooling_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_11_Heating_Or_No_Load_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_11_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_11_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""

    Zone_Equipment_12_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field()]

    Zone_Equipment_12_Name: Annotated[str, Field()]

    Zone_Equipment_12_Cooling_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_12_Heating_Or_No_Load_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_12_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_12_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""

    Zone_Equipment_13_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field()]

    Zone_Equipment_13_Name: Annotated[str, Field()]

    Zone_Equipment_13_Cooling_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_13_Heating_Or_No_Load_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_13_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_13_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""

    Zone_Equipment_14_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field()]

    Zone_Equipment_14_Name: Annotated[str, Field()]

    Zone_Equipment_14_Cooling_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_14_Heating_Or_No_Load_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_14_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_14_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""

    Zone_Equipment_15_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field()]

    Zone_Equipment_15_Name: Annotated[str, Field()]

    Zone_Equipment_15_Cooling_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_15_Heating_Or_No_Load_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_15_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_15_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""

    Zone_Equipment_16_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field()]

    Zone_Equipment_16_Name: Annotated[str, Field()]

    Zone_Equipment_16_Cooling_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_16_Heating_Or_No_Load_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_16_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_16_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""

    Zone_Equipment_17_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field()]

    Zone_Equipment_17_Name: Annotated[str, Field()]

    Zone_Equipment_17_Cooling_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_17_Heating_Or_No_Load_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_17_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_17_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""

    Zone_Equipment_18_Object_Type: Annotated[Literal['ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:AirDistributionUnit', 'AirTerminal:SingleDuct:Uncontrolled', 'ZoneHVAC:EnergyRecoveryVentilator', 'ZoneHVAC:EvaporativeCoolerUnit', 'ZoneHVAC:HybridUnitaryHVAC', 'ZoneHVAC:ForcedAir:UserDefined', 'ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:OutdoorAirUnit', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:UnitHeater', 'ZoneHVAC:UnitVentilator', 'ZoneHVAC:VentilatedSlab', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:WindowAirConditioner', 'ZoneHVAC:Baseboard:RadiantConvective:Electric', 'ZoneHVAC:Baseboard:RadiantConvective:Water', 'ZoneHVAC:Baseboard:RadiantConvective:Steam', 'ZoneHVAC:CoolingPanel:RadiantConvective:Water', 'ZoneHVAC:Baseboard:Convective:Electric', 'ZoneHVAC:Baseboard:Convective:Water', 'ZoneHVAC:HighTemperatureRadiant', 'ZoneHVAC:LowTemperatureRadiant:VariableFlow', 'ZoneHVAC:LowTemperatureRadiant:ConstantFlow', 'ZoneHVAC:LowTemperatureRadiant:Electric', 'ZoneHVAC:Dehumidifier:DX', 'ZoneHVAC:IdealLoadsAirSystem', 'ZoneHVAC:RefrigerationChillerSet', 'Fan:ZoneExhaust', 'WaterHeater:HeatPump:PumpedCondenser', 'WaterHeater:HeatPump:WrappedCondenser', 'HeatExchanger:AirToAir:FlatPlate', 'AirLoopHVAC:UnitarySystem'], Field()]

    Zone_Equipment_18_Name: Annotated[str, Field()]

    Zone_Equipment_18_Cooling_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_18_Heating_Or_No_Load_Sequence: Annotated[int, Field(ge=0)]
    """Specifies the zone equipment simulation order"""

    Zone_Equipment_18_Sequential_Cooling_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining cooling load this equipment will attempt to serve"""

    Zone_Equipment_18_Sequential_Heating_Fraction_Schedule_Name: Annotated[str, Field()]
    """The fraction of the remaining heating load this equipment will attempt to serve"""