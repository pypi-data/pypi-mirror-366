from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Plantequipmentoperationschemes(EpBunch):
    """Operation schemes are listed in "priority" order. Note that each scheme"""

    Name: Annotated[str, Field(default=...)]

    Control_Scheme_1_Object_Type: Annotated[Literal['PlantEquipmentOperation:CoolingLoad', 'PlantEquipmentOperation:HeatingLoad', 'PlantEquipmentOperation:Uncontrolled', 'PlantEquipmentOperation:ComponentSetpoint', 'PlantEquipmentOperation:ThermalEnergyStorage', 'PlantEquipmentOperation:UserDefined', 'PlantEquipmentOperation:OutdoorDryBulb', 'PlantEquipmentOperation:OutdoorWetBulb', 'PlantEquipmentOperation:OutdoorRelativeHumidity', 'PlantEquipmentOperation:OutdoorDewpoint', 'PlantEquipmentOperation:OutdoorDryBulbDifference', 'PlantEquipmentOperation:OutdoorWetBulbDifference', 'PlantEquipmentOperation:OutdoorDewpointDifference'], Field(default=...)]

    Control_Scheme_1_Name: Annotated[str, Field(default=...)]

    Control_Scheme_1_Schedule_Name: Annotated[str, Field(default=...)]

    Control_Scheme_2_Object_Type: Annotated[Literal['PlantEquipmentOperation:CoolingLoad', 'PlantEquipmentOperation:HeatingLoad', 'PlantEquipmentOperation:Uncontrolled', 'PlantEquipmentOperation:ComponentSetpoint', 'PlantEquipmentOperation:ThermalEnergyStorage', 'PlantEquipmentOperation:UserDefined', 'PlantEquipmentOperation:OutdoorDryBulb', 'PlantEquipmentOperation:OutdoorWetBulb', 'PlantEquipmentOperation:OutdoorRelativeHumidity', 'PlantEquipmentOperation:OutdoorDewpoint', 'PlantEquipmentOperation:OutdoorDryBulbDifference', 'PlantEquipmentOperation:OutdoorWetBulbDifference', 'PlantEquipmentOperation:OutdoorDewpointDifference'], Field()]

    Control_Scheme_2_Name: Annotated[str, Field()]

    Control_Scheme_2_Schedule_Name: Annotated[str, Field()]

    Control_Scheme_3_Object_Type: Annotated[Literal['PlantEquipmentOperation:CoolingLoad', 'PlantEquipmentOperation:HeatingLoad', 'PlantEquipmentOperation:Uncontrolled', 'PlantEquipmentOperation:ComponentSetpoint', 'PlantEquipmentOperation:ThermalEnergyStorage', 'PlantEquipmentOperation:UserDefined', 'PlantEquipmentOperation:OutdoorDryBulb', 'PlantEquipmentOperation:OutdoorWetBulb', 'PlantEquipmentOperation:OutdoorRelativeHumidity', 'PlantEquipmentOperation:OutdoorDewpoint', 'PlantEquipmentOperation:OutdoorDryBulbDifference', 'PlantEquipmentOperation:OutdoorWetBulbDifference', 'PlantEquipmentOperation:OutdoorDewpointDifference'], Field()]

    Control_Scheme_3_Name: Annotated[str, Field()]

    Control_Scheme_3_Schedule_Name: Annotated[str, Field()]

    Control_Scheme_4_Object_Type: Annotated[Literal['PlantEquipmentOperation:CoolingLoad', 'PlantEquipmentOperation:HeatingLoad', 'PlantEquipmentOperation:Uncontrolled', 'PlantEquipmentOperation:ComponentSetpoint', 'PlantEquipmentOperation:ThermalEnergyStorage', 'PlantEquipmentOperation:UserDefined', 'PlantEquipmentOperation:OutdoorDryBulb', 'PlantEquipmentOperation:OutdoorWetBulb', 'PlantEquipmentOperation:OutdoorRelativeHumidity', 'PlantEquipmentOperation:OutdoorDewpoint', 'PlantEquipmentOperation:OutdoorDryBulbDifference', 'PlantEquipmentOperation:OutdoorWetBulbDifference', 'PlantEquipmentOperation:OutdoorDewpointDifference'], Field()]

    Control_Scheme_4_Name: Annotated[str, Field()]

    Control_Scheme_4_Schedule_Name: Annotated[str, Field()]

    Control_Scheme_5_Object_Type: Annotated[Literal['PlantEquipmentOperation:CoolingLoad', 'PlantEquipmentOperation:HeatingLoad', 'PlantEquipmentOperation:Uncontrolled', 'PlantEquipmentOperation:ComponentSetpoint', 'PlantEquipmentOperation:ThermalEnergyStorage', 'PlantEquipmentOperation:UserDefined', 'PlantEquipmentOperation:OutdoorDryBulb', 'PlantEquipmentOperation:OutdoorWetBulb', 'PlantEquipmentOperation:OutdoorRelativeHumidity', 'PlantEquipmentOperation:OutdoorDewpoint', 'PlantEquipmentOperation:OutdoorDryBulbDifference', 'PlantEquipmentOperation:OutdoorWetBulbDifference', 'PlantEquipmentOperation:OutdoorDewpointDifference'], Field()]

    Control_Scheme_5_Name: Annotated[str, Field()]

    Control_Scheme_5_Schedule_Name: Annotated[str, Field()]

    Control_Scheme_6_Object_Type: Annotated[Literal['PlantEquipmentOperation:CoolingLoad', 'PlantEquipmentOperation:HeatingLoad', 'PlantEquipmentOperation:Uncontrolled', 'PlantEquipmentOperation:ComponentSetpoint', 'PlantEquipmentOperation:ThermalEnergyStorage', 'PlantEquipmentOperation:UserDefined', 'PlantEquipmentOperation:OutdoorDryBulb', 'PlantEquipmentOperation:OutdoorWetBulb', 'PlantEquipmentOperation:OutdoorRelativeHumidity', 'PlantEquipmentOperation:OutdoorDewpoint', 'PlantEquipmentOperation:OutdoorDryBulbDifference', 'PlantEquipmentOperation:OutdoorWetBulbDifference', 'PlantEquipmentOperation:OutdoorDewpointDifference'], Field()]

    Control_Scheme_6_Name: Annotated[str, Field()]

    Control_Scheme_6_Schedule_Name: Annotated[str, Field()]

    Control_Scheme_7_Object_Type: Annotated[Literal['PlantEquipmentOperation:CoolingLoad', 'PlantEquipmentOperation:HeatingLoad', 'PlantEquipmentOperation:Uncontrolled', 'PlantEquipmentOperation:ComponentSetpoint', 'PlantEquipmentOperation:ThermalEnergyStorage', 'PlantEquipmentOperation:UserDefined', 'PlantEquipmentOperation:OutdoorDryBulb', 'PlantEquipmentOperation:OutdoorWetBulb', 'PlantEquipmentOperation:OutdoorRelativeHumidity', 'PlantEquipmentOperation:OutdoorDewpoint', 'PlantEquipmentOperation:OutdoorDryBulbDifference', 'PlantEquipmentOperation:OutdoorWetBulbDifference', 'PlantEquipmentOperation:OutdoorDewpointDifference'], Field()]

    Control_Scheme_7_Name: Annotated[str, Field()]

    Control_Scheme_7_Schedule_Name: Annotated[str, Field()]

    Control_Scheme_8_Object_Type: Annotated[Literal['PlantEquipmentOperation:CoolingLoad', 'PlantEquipmentOperation:HeatingLoad', 'PlantEquipmentOperation:Uncontrolled', 'PlantEquipmentOperation:ComponentSetpoint', 'PlantEquipmentOperation:ThermalEnergyStorage', 'PlantEquipmentOperation:UserDefined', 'PlantEquipmentOperation:OutdoorDryBulb', 'PlantEquipmentOperation:OutdoorWetBulb', 'PlantEquipmentOperation:OutdoorRelativeHumidity', 'PlantEquipmentOperation:OutdoorDewpoint', 'PlantEquipmentOperation:OutdoorDryBulbDifference', 'PlantEquipmentOperation:OutdoorWetBulbDifference', 'PlantEquipmentOperation:OutdoorDewpointDifference'], Field()]

    Control_Scheme_8_Name: Annotated[str, Field()]

    Control_Scheme_8_Schedule_Name: Annotated[str, Field()]