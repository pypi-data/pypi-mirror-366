from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Outdoorairunit_Equipmentlist(EpBunch):
    """Equipment list for components in a ZoneHVAC:OutdoorAirUnit. Components are simulated"""

    Name: Annotated[str, Field(default=...)]

    Component_1_Object_Type: Annotated[Literal['Coil:Heating:Electric', 'Coil:Heating:Fuel', 'Coil:Heating:Steam', 'Coil:Heating:Water', 'Coil:Cooling:Water', 'Coil:Cooling:Water:DetailedGeometry', 'CoilSystem:Cooling:Water:HeatexchangerAssisted', 'CoilSystem:Cooling:DX', 'CoilSystem:Heating:DX', 'HeatExchanger:AirToAir:FlatPlate', 'HeatExchanger:AirToAir:SensibleAndLatent', 'Dehumidifier:Desiccant:NoFans', 'AirLoopHVAC:UnitarySystem'], Field()]

    Component_1_Name: Annotated[str, Field()]

    Component_2_Object_Type: Annotated[Literal['Coil:Heating:Electric', 'Coil:Heating:Fuel', 'Coil:Heating:Steam', 'Coil:Heating:Water', 'Coil:Cooling:Water', 'Coil:Cooling:Water:DetailedGeometry', 'CoilSystem:Cooling:Water:HeatexchangerAssisted', 'CoilSystem:Cooling:DX', 'CoilSystem:Heating:DX', 'HeatExchanger:AirToAir:FlatPlate', 'HeatExchanger:AirToAir:SensibleAndLatent', 'Dehumidifier:Desiccant:NoFans', 'AirLoopHVAC:UnitarySystem'], Field()]

    Component_2_Name: Annotated[str, Field()]

    Component_3_Object_Type: Annotated[Literal['Coil:Heating:Electric', 'Coil:Heating:Fuel', 'Coil:Heating:Steam', 'Coil:Heating:Water', 'Coil:Cooling:Water', 'Coil:Cooling:Water:DetailedGeometry', 'CoilSystem:Cooling:Water:HeatexchangerAssisted', 'CoilSystem:Cooling:DX', 'CoilSystem:Heating:DX', 'HeatExchanger:AirToAir:FlatPlate', 'HeatExchanger:AirToAir:SensibleAndLatent', 'Dehumidifier:Desiccant:NoFans', 'AirLoopHVAC:UnitarySystem'], Field()]

    Component_3_Name: Annotated[str, Field()]

    Component_4_Object_Type: Annotated[Literal['Coil:Heating:Electric', 'Coil:Heating:Fuel', 'Coil:Heating:Steam', 'Coil:Heating:Water', 'Coil:Cooling:Water', 'Coil:Cooling:Water:DetailedGeometry', 'CoilSystem:Cooling:Water:HeatexchangerAssisted', 'CoilSystem:Cooling:DX', 'CoilSystem:Heating:DX', 'HeatExchanger:AirToAir:FlatPlate', 'HeatExchanger:AirToAir:SensibleAndLatent', 'Dehumidifier:Desiccant:NoFans', 'AirLoopHVAC:UnitarySystem'], Field()]

    Component_4_Name: Annotated[str, Field()]

    Component_5_Object_Type: Annotated[Literal['Coil:Heating:Electric', 'Coil:Heating:Fuel', 'Coil:Heating:Steam', 'Coil:Heating:Water', 'Coil:Cooling:Water', 'Coil:Cooling:Water:DetailedGeometry', 'CoilSystem:Cooling:Water:HeatexchangerAssisted', 'CoilSystem:Cooling:DX', 'CoilSystem:Heating:DX', 'HeatExchanger:AirToAir:FlatPlate', 'HeatExchanger:AirToAir:SensibleAndLatent', 'Dehumidifier:Desiccant:NoFans', 'AirLoopHVAC:UnitarySystem'], Field()]

    Component_5_Name: Annotated[str, Field()]

    Component_6_Object_Type: Annotated[Literal['Coil:Heating:Electric', 'Coil:Heating:Fuel', 'Coil:Heating:Steam', 'Coil:Heating:Water', 'Coil:Cooling:Water', 'Coil:Cooling:Water:DetailedGeometry', 'CoilSystem:Cooling:Water:HeatexchangerAssisted', 'CoilSystem:Cooling:DX', 'CoilSystem:Heating:DX', 'HeatExchanger:AirToAir:FlatPlate', 'HeatExchanger:AirToAir:SensibleAndLatent', 'Dehumidifier:Desiccant:NoFans', 'AirLoopHVAC:UnitarySystem'], Field()]

    Component_6_Name: Annotated[str, Field()]

    Component_7_Object_Type: Annotated[Literal['Coil:Heating:Electric', 'Coil:Heating:Fuel', 'Coil:Heating:Steam', 'Coil:Heating:Water', 'Coil:Cooling:Water', 'Coil:Cooling:Water:DetailedGeometry', 'CoilSystem:Cooling:Water:HeatexchangerAssisted', 'CoilSystem:Cooling:DX', 'CoilSystem:Heating:DX', 'HeatExchanger:AirToAir:FlatPlate', 'HeatExchanger:AirToAir:SensibleAndLatent', 'Dehumidifier:Desiccant:NoFans', 'AirLoopHVAC:UnitarySystem'], Field()]

    Component_7_Name: Annotated[str, Field()]

    Component_8_Object_Type: Annotated[Literal['Coil:Heating:Electric', 'Coil:Heating:Fuel', 'Coil:Heating:Steam', 'Coil:Heating:Water', 'Coil:Cooling:Water', 'Coil:Cooling:Water:DetailedGeometry', 'CoilSystem:Cooling:Water:HeatexchangerAssisted', 'CoilSystem:Cooling:DX', 'CoilSystem:Heating:DX', 'HeatExchanger:AirToAir:FlatPlate', 'HeatExchanger:AirToAir:SensibleAndLatent', 'Dehumidifier:Desiccant:NoFans', 'AirLoopHVAC:UnitarySystem'], Field()]

    Component_8_Name: Annotated[str, Field()]