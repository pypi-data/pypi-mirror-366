from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Plantequipmentoperation_Componentsetpoint(EpBunch):
    """Plant equipment operation scheme for component setpoint operation. Specifies one or"""

    Name: Annotated[str, Field(default=...)]

    Equipment_1_Object_Type: Annotated[str, Field(default=...)]

    Equipment_1_Name: Annotated[str, Field(default=...)]

    Demand_Calculation_1_Node_Name: Annotated[str, Field(default=...)]

    Setpoint_1_Node_Name: Annotated[str, Field(default=...)]

    Component_1_Flow_Rate: Annotated[float, Field(default=...)]

    Operation_1_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field(default=...)]

    Equipment_2_Object_Type: Annotated[str, Field()]

    Equipment_2_Name: Annotated[str, Field()]

    Demand_Calculation_2_Node_Name: Annotated[str, Field()]

    Setpoint_2_Node_Name: Annotated[str, Field()]

    Component_2_Flow_Rate: Annotated[float, Field()]

    Operation_2_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]

    Equipment_3_Object_Type: Annotated[str, Field()]

    Equipment_3_Name: Annotated[str, Field()]

    Demand_Calculation_3_Node_Name: Annotated[str, Field()]

    Setpoint_3_Node_Name: Annotated[str, Field()]

    Component_3_Flow_Rate: Annotated[float, Field()]

    Operation_3_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]

    Equipment_4_Object_Type: Annotated[str, Field()]

    Equipment_4_Name: Annotated[str, Field()]

    Demand_Calculation_4_Node_Name: Annotated[str, Field()]

    Setpoint_4_Node_Name: Annotated[str, Field()]

    Component_4_Flow_Rate: Annotated[float, Field()]

    Operation_4_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]

    Equipment_5_Object_Type: Annotated[str, Field()]

    Equipment_5_Name: Annotated[str, Field()]

    Demand_Calculation_5_Node_Name: Annotated[str, Field()]

    Setpoint_5_Node_Name: Annotated[str, Field()]

    Component_5_Flow_Rate: Annotated[float, Field()]

    Operation_5_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]

    Equipment_6_Object_Type: Annotated[str, Field()]

    Equipment_6_Name: Annotated[str, Field()]

    Demand_Calculation_6_Node_Name: Annotated[str, Field()]

    Setpoint_6_Node_Name: Annotated[str, Field()]

    Component_6_Flow_Rate: Annotated[float, Field()]

    Operation_6_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]

    Equipment_7_Object_Type: Annotated[str, Field()]

    Equipment_7_Name: Annotated[str, Field()]

    Demand_Calculation_7_Node_Name: Annotated[str, Field()]

    Setpoint_7_Node_Name: Annotated[str, Field()]

    Component_7_Flow_Rate: Annotated[float, Field()]

    Operation_7_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]

    Equipment_8_Object_Type: Annotated[str, Field()]

    Equipment_8_Name: Annotated[str, Field()]

    Demand_Calculation_8_Node_Name: Annotated[str, Field()]

    Setpoint_8_Node_Name: Annotated[str, Field()]

    Component_8_Flow_Rate: Annotated[float, Field()]

    Operation_8_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]

    Equipment_9_Object_Type: Annotated[str, Field()]

    Equipment_9_Name: Annotated[str, Field()]

    Demand_Calculation_9_Node_Name: Annotated[str, Field()]

    Setpoint_9_Node_Name: Annotated[str, Field()]

    Component_9_Flow_Rate: Annotated[float, Field()]

    Operation_9_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]

    Equipment_10_Object_Type: Annotated[str, Field()]

    Equipment_10_Name: Annotated[str, Field()]

    Demand_Calculation_10_Node_Name: Annotated[str, Field()]

    Setpoint_10_Node_Name: Annotated[str, Field()]

    Component_10_Flow_Rate: Annotated[float, Field()]

    Operation_10_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]