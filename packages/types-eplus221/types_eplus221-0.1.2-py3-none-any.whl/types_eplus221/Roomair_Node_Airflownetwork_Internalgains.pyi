from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roomair_Node_Airflownetwork_Internalgains(EpBunch):
    """define the internal gains that are associated with one particular RoomAir:Node"""

    Name: Annotated[str, Field()]

    Internal_Gain_Object_1_Type: Annotated[Literal['People', 'Lights', 'ElectricEquipment', 'GasEquipment', 'HotWaterEquipment', 'SteamEquipment', 'OtherEquipment', 'ZoneBaseboard:OutdoorTemperatureControlled', 'ZoneContaminantSourceAndSink:CarbonDioxide', 'WaterUse:Equipment', 'DaylightingDevice:Tubular', 'WaterHeater:Mixed', 'WaterHeater:Stratified', 'ThermalStorage:ChilledWater:Mixed', 'ThermalStorage:ChilledWater:Stratified', 'Generator:FuelCell', 'Generator:MicroCHP', 'ElectricLoadCenter:Transformer', 'ElectricLoadCenter:Inverter:Simple', 'ElectricLoadCenter:Inverter:FunctionOfPower', 'ElectricLoadCenter:Inverter:LookUpTable', 'ElectricLoadCenter:Storage:Battery', 'ElectricLoadCenter:Storage:Simple', 'ElectricLoadCenter:Storage:Converter', 'Pipe:Indoor', 'Refrigeration:Case', 'Refrigeration:CompressorRack', 'Refrigeration:System:Condenser:AirCooled', 'Refrigeration:TranscriticalSystem:GasCooler:AirCooled', 'Refrigeration:System:SuctionPipe', 'Refrigeration:TranscriticalSystem:SuctionPipeMT', 'Refrigeration:TranscriticalSystem:SuctionPipeLT', 'Refrigeration:SecondarySystem:Receiver', 'Refrigeration:SecondarySystem:Pipe', 'Refrigeration:WalkIn', 'Pump:VariableSpeed', 'Pump:ConstantSpeed', 'Pump:VariableSpeed:Condensate', 'HeaderedPumps:VariableSpeed', 'HeaderedPumps:ConstantSpeed', 'ZoneContaminantSourceAndSink:GenericContaminant', 'PlantComponent:UserDefined', 'Coil:UserDefined', 'ZoneHVAC:ForcedAir:UserDefined', 'AirTerminal:SingleDuct:UserDefined'], Field()]

    Internal_Gain_Object_1_Name: Annotated[str, Field()]

    Fraction_of_Gains_to_Node_1: Annotated[float, Field(ge=0.0, le=1.0)]
    """fraction applies to sensible, latent, carbon dioxide, and generic contaminant gains or losses"""

    Internal_Gain_Object_2_Type: Annotated[Literal['People', 'Lights', 'ElectricEquipment', 'GasEquipment', 'HotWaterEquipment', 'SteamEquipment', 'OtherEquipment', 'ZoneBaseboard:OutdoorTemperatureControlled', 'ZoneContaminantSourceAndSink:CarbonDioxide', 'WaterUse:Equipment', 'DaylightingDevice:Tubular', 'WaterHeater:Mixed', 'WaterHeater:Stratified', 'ThermalStorage:ChilledWater:Mixed', 'ThermalStorage:ChilledWater:Stratified', 'Generator:FuelCell', 'Generator:MicroCHP', 'ElectricLoadCenter:Transformer', 'ElectricLoadCenter:Inverter:Simple', 'ElectricLoadCenter:Inverter:FunctionOfPower', 'ElectricLoadCenter:Inverter:LookUpTable', 'ElectricLoadCenter:Storage:Battery', 'ElectricLoadCenter:Storage:Simple', 'ElectricLoadCenter:Storage:Converter', 'Pipe:Indoor', 'Refrigeration:Case', 'Refrigeration:CompressorRack', 'Refrigeration:System:Condenser:AirCooled', 'Refrigeration:TranscriticalSystem:GasCooler:AirCooled', 'Refrigeration:System:SuctionPipe', 'Refrigeration:TranscriticalSystem:SuctionPipeMT', 'Refrigeration:TranscriticalSystem:SuctionPipeLT', 'Refrigeration:SecondarySystem:Receiver', 'Refrigeration:SecondarySystem:Pipe', 'Refrigeration:WalkIn', 'Pump:VariableSpeed', 'Pump:ConstantSpeed', 'Pump:VariableSpeed:Condensate', 'HeaderedPumps:VariableSpeed', 'HeaderedPumps:ConstantSpeed', 'ZoneContaminantSourceAndSink:GenericContaminant', 'PlantComponent:UserDefined', 'Coil:UserDefined', 'ZoneHVAC:ForcedAir:UserDefined', 'AirTerminal:SingleDuct:UserDefined'], Field()]

    Internal_Gain_Object_2_Name: Annotated[str, Field()]

    Fraction_of_Gains_to_Node_2: Annotated[float, Field(ge=0.0, le=1.0)]

    Internal_Gain_Object_3_Type: Annotated[Literal['People', 'Lights', 'ElectricEquipment', 'GasEquipment', 'HotWaterEquipment', 'SteamEquipment', 'OtherEquipment', 'ZoneBaseboard:OutdoorTemperatureControlled', 'ZoneContaminantSourceAndSink:CarbonDioxide', 'WaterUse:Equipment', 'DaylightingDevice:Tubular', 'WaterHeater:Mixed', 'WaterHeater:Stratified', 'ThermalStorage:ChilledWater:Mixed', 'ThermalStorage:ChilledWater:Stratified', 'Generator:FuelCell', 'Generator:MicroCHP', 'ElectricLoadCenter:Transformer', 'ElectricLoadCenter:Inverter:Simple', 'ElectricLoadCenter:Inverter:FunctionOfPower', 'ElectricLoadCenter:Inverter:LookUpTable', 'ElectricLoadCenter:Storage:Battery', 'ElectricLoadCenter:Storage:Simple', 'ElectricLoadCenter:Storage:Converter', 'Pipe:Indoor', 'Refrigeration:Case', 'Refrigeration:CompressorRack', 'Refrigeration:System:Condenser:AirCooled', 'Refrigeration:TranscriticalSystem:GasCooler:AirCooled', 'Refrigeration:System:SuctionPipe', 'Refrigeration:TranscriticalSystem:SuctionPipeMT', 'Refrigeration:TranscriticalSystem:SuctionPipeLT', 'Refrigeration:SecondarySystem:Receiver', 'Refrigeration:SecondarySystem:Pipe', 'Refrigeration:WalkIn', 'Pump:VariableSpeed', 'Pump:ConstantSpeed', 'Pump:VariableSpeed:Condensate', 'HeaderedPumps:VariableSpeed', 'HeaderedPumps:ConstantSpeed', 'ZoneContaminantSourceAndSink:GenericContaminant', 'PlantComponent:UserDefined', 'Coil:UserDefined', 'ZoneHVAC:ForcedAir:UserDefined', 'AirTerminal:SingleDuct:UserDefined'], Field()]

    Internal_Gain_Object_3_Name: Annotated[str, Field()]

    Fraction_of_Gains_to_Node_3: Annotated[float, Field(ge=0.0, le=1.0)]