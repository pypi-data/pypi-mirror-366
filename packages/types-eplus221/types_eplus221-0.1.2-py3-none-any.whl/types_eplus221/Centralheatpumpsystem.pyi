from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Centralheatpumpsystem(EpBunch):
    """This chiller bank can contain multiple chiller heaters and heat pump performance objects."""

    Name: Annotated[str, Field(default=...)]

    Control_Method: Annotated[Literal['SmartMixing'], Field(default='SmartMixing')]

    Cooling_Loop_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Cooling_Loop_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Source_Loop_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Source_Loop_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Heating_Loop_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Heating_Loop_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Ancillary_Power: Annotated[float, Field(ge=0.0, default=0.0)]
    """Power as demanded from any auxiliary controls"""

    Ancillary_Operation_Schedule_Name: Annotated[str, Field()]
    """This value from this schedule is multiplied times the Ancillary Power"""

    Chiller_Heater_Modules_Performance_Component_Object_Type_1: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field(default=...)]

    Chiller_Heater_Modules_Performance_Component_Name_1: Annotated[str, Field(default=...)]

    Chiller_Heater_Modules_Control_Schedule_Name_1: Annotated[str, Field(default=...)]

    Number_of_Chiller_Heater_Modules_1: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_2: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Modules_Performance_Component_Name_2: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Schedule_Name_2: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_2: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Performance_Component_Object_Type_3: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Performance_Component_Name_3: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Schedule_Name_3: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_3: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_4: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Modules_Performance_Component_Name_4: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Schedule_Name_4: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_4: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_5: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Models_Performance_Component_Name_5: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Schedule_Name_5: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_5: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_6: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Modules_Performance_Component_Name_6: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Schedule_Name_6: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_6: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_7: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Modules_Performance_Component_Name_7: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Schedule_Name_7: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_7: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_8: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Modules_Performance_Component_Name_8: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Schedule_Name_8: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_8: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_9: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Modules_Performance_Component_Name_9: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Schedule_Name_9: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_9: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_10: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Modules_Performance_Component_Name_10: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Schedule_Name_10: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_10: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_11: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Modules_Performance_Component_Name_11: Annotated[str, Field()]

    Chiller_Heater_Module_Control_Schedule_Name_11: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_11: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_12: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Modules_Performance_Component_Name_12: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Schedule_Name_12: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_12: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_13: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Modules_Performance_Component_Name_13: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Schedule_Name_13: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_13: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_14: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Modules_Performance_Component_Name_14: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Schedule_Name_14: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_14: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_15: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Modules_Performance_Component_Name_15: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Schedule_Name_15: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_15: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_16: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Modules_Performance_Component_Name_16: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Schedule_Name_16: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_16: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_17: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Modules_Performance_Component_Name_17: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Schedule_Name_17: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_17: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_18: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Modules_Performance_Component_Name_18: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Control_Schedule_Name_18: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_18: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_19: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Modules_Performance_Component_Name_19: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Schedule_Name_19: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_19: Annotated[int, Field(ge=1, default=1)]

    Chiller_Heater_Modules_Performance_Component_Object_Type_20: Annotated[Literal['ChillerHeaterPerformance:Electric:EIR'], Field()]

    Chiller_Heater_Modules_Performance_Component_Name_20: Annotated[str, Field()]

    Chiller_Heater_Modules_Control_Schedule_Name_20: Annotated[str, Field()]

    Number_of_Chiller_Heater_Modules_20: Annotated[int, Field(ge=1, default=1)]