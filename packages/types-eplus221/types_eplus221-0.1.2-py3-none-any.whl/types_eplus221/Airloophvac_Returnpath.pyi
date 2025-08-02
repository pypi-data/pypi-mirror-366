from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac_Returnpath(EpBunch):
    """A return air path can only contain one AirLoopHVAC:ZoneMixer"""

    Name: Annotated[str, Field(default=...)]

    Return_Air_Path_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Component_1_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field(default=...)]

    Component_1_Name: Annotated[str, Field(default=...)]

    Component_2_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_2_Name: Annotated[str, Field()]

    Component_3_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_3_Name: Annotated[str, Field()]

    Component_4_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_4_Name: Annotated[str, Field()]

    Component_5_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_5_Name: Annotated[str, Field()]

    Component_6_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_6_Name: Annotated[str, Field()]

    Component_7_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_7_Name: Annotated[str, Field()]

    Component_8_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_8_Name: Annotated[str, Field()]

    Component_9_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_9_Name: Annotated[str, Field()]

    Component_10_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_10_Name: Annotated[str, Field()]

    Component_11_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_11_Name: Annotated[str, Field()]

    Component_12_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_12_Name: Annotated[str, Field()]

    Component_13_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_13_Name: Annotated[str, Field()]

    Component_14_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_14_Name: Annotated[str, Field()]

    Component_15_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_15_Name: Annotated[str, Field()]

    Component_16_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_16_Name: Annotated[str, Field()]

    Component_17_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_17_Name: Annotated[str, Field()]

    Component_18_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_18_Name: Annotated[str, Field()]

    Component_19_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_19_Name: Annotated[str, Field()]

    Component_20_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_20_Name: Annotated[str, Field()]

    Component_21_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_21_Name: Annotated[str, Field()]

    Component_22_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_22_Name: Annotated[str, Field()]

    Component_23_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_23_Name: Annotated[str, Field()]

    Component_24_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_24_Name: Annotated[str, Field()]

    Component_25_Object_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ReturnPlenum'], Field()]

    Component_25_Name: Annotated[str, Field()]