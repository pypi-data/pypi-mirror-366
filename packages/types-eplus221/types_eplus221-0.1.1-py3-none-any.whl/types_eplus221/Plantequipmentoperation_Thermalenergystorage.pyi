from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Plantequipmentoperation_Thermalenergystorage(EpBunch):
    """Plant equipment operation scheme for simpler input to control thermal (ice)"""

    Name: Annotated[str, Field(default=...)]

    On_Peak_Schedule: Annotated[str, Field(default=...)]

    Charging_Availability_Schedule: Annotated[str, Field(default=...)]

    Non_Charging_Chilled_Water_Temperature: Annotated[float, Field(default=...)]
    """Single temperature for chiller outlet when not in cooling season"""

    Charging_Chilled_Water_Temperature: Annotated[float, Field(default=...)]
    """Single temperature for chiller outlet when off-peak during cooling"""

    Component_1_Object_Type: Annotated[Literal['ThermalStorage:Ice:Simple', 'ThermalStorage:Ice:Detailed', 'Chiller:Electric:EIR', 'Chiller:Electric:ReformulatedEIR', 'Chiller:Electric', 'Chiller:Absorption:Indirect', 'Chiller:Absorption', 'Chiller:ConstantCOP', 'Chiller:EngineDriven', 'Chiller:CombustionTurbine'], Field(default=...)]
    """This field is the type of object and should either be a chiller or some"""

    Component_1_Name: Annotated[str, Field(default=...)]
    """This field is the name of either the chiller or ice storage equipment"""

    Component_1_Demand_Calculation_Node_Name: Annotated[str, Field(default=...)]
    """This field is the name of the inlet node for the component defined in"""

    Component_1_Setpoint_Node_Name: Annotated[str, Field(default=...)]
    """This field is the name of the outlet node for the component listed above."""

    Component_1_Flow_Rate: Annotated[float, Field(default=...)]
    """This field is the flow rate for the component listed above."""

    Component_1_Operation_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field(default=...)]
    """This field is the operation type for the component listed above. For this"""

    Component_2_Object_Type: Annotated[Literal['ThermalStorage:Ice:Simple', 'ThermalStorage:Ice:Detailed', 'Chiller:Electric:EIR', 'Chiller:Electric:ReformulatedEIR', 'Chiller:Electric', 'Chiller:Absorption:Indirect', 'Chiller:Absorption', 'Chiller:ConstantCOP', 'Chiller:EngineDriven', 'Chiller:CombustionTurbine'], Field()]

    Component_2_Name: Annotated[str, Field()]

    Component_2_Demand_Calculation_Node_Name: Annotated[str, Field()]

    Component_2_Setpoint_Node_Name: Annotated[str, Field()]

    Component_2_Flow_Rate: Annotated[float, Field()]

    Component_2_Operation_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]

    Component_3_Object_Type: Annotated[Literal['ThermalStorage:Ice:Simple', 'ThermalStorage:Ice:Detailed', 'Chiller:Electric:EIR', 'Chiller:Electric:ReformulatedEIR', 'Chiller:Electric', 'Chiller:Absorption:Indirect', 'Chiller:Absorption', 'Chiller:ConstantCOP', 'Chiller:EngineDriven', 'Chiller:CombustionTurbine'], Field()]

    Component_3_Name: Annotated[str, Field()]

    Component_3_Demand_Calculation_Node_Name: Annotated[str, Field()]

    Component_3_Setpoint_Node_Name: Annotated[str, Field()]

    Component_3_Flow_Rate: Annotated[float, Field()]

    Component_3_Operation_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]

    Component_4_Object_Type: Annotated[Literal['ThermalStorage:Ice:Simple', 'ThermalStorage:Ice:Detailed', 'Chiller:Electric:EIR', 'Chiller:Electric:ReformulatedEIR', 'Chiller:Electric', 'Chiller:Absorption:Indirect', 'Chiller:Absorption', 'Chiller:ConstantCOP', 'Chiller:EngineDriven', 'Chiller:CombustionTurbine'], Field()]

    Component_4_Name: Annotated[str, Field()]

    Component_4_Demand_Calculation_Node_Name: Annotated[str, Field()]

    Component_4_Setpoint_Node_Name: Annotated[str, Field()]

    Component_4_Flow_Rate: Annotated[float, Field()]

    Component_4_Operation_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]

    Component_5_Object_Type: Annotated[Literal['ThermalStorage:Ice:Simple', 'ThermalStorage:Ice:Detailed', 'Chiller:Electric:EIR', 'Chiller:Electric:ReformulatedEIR', 'Chiller:Electric', 'Chiller:Absorption:Indirect', 'Chiller:Absorption', 'Chiller:ConstantCOP', 'Chiller:EngineDriven', 'Chiller:CombustionTurbine'], Field()]

    Component_5_Name: Annotated[str, Field()]

    Component_5_Demand_Calculation_Node_Name: Annotated[str, Field()]

    Component_5_Setpoint_Node_Name: Annotated[str, Field()]

    Component_5_Flow_Rate: Annotated[float, Field()]

    Component_5_Operation_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]

    Component_6_Object_Type: Annotated[Literal['ThermalStorage:Ice:Simple', 'ThermalStorage:Ice:Detailed', 'Chiller:Electric:EIR', 'Chiller:Electric:ReformulatedEIR', 'Chiller:Electric', 'Chiller:Absorption:Indirect', 'Chiller:Absorption', 'Chiller:ConstantCOP', 'Chiller:EngineDriven', 'Chiller:CombustionTurbine'], Field()]

    Component_6_Name: Annotated[str, Field()]

    Component_6_Demand_Calculation_Node_Name: Annotated[str, Field()]

    Component_6_Setpoint_Node_Name: Annotated[str, Field()]

    Component_6_Flow_Rate: Annotated[float, Field()]

    Component_6_Operation_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]

    Component_7_Object_Type: Annotated[Literal['ThermalStorage:Ice:Simple', 'ThermalStorage:Ice:Detailed', 'Chiller:Electric:EIR', 'Chiller:Electric:ReformulatedEIR', 'Chiller:Electric', 'Chiller:Absorption:Indirect', 'Chiller:Absorption', 'Chiller:ConstantCOP', 'Chiller:EngineDriven', 'Chiller:CombustionTurbine'], Field()]

    Component_7_Name: Annotated[str, Field()]

    Component_7_Demand_Calculation_Node_Name: Annotated[str, Field()]

    Component_7_Setpoint_Node_Name: Annotated[str, Field()]

    Component_7_Flow_Rate: Annotated[float, Field()]

    Component_7_Operation_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]

    Component_8_Object_Type: Annotated[Literal['ThermalStorage:Ice:Simple', 'ThermalStorage:Ice:Detailed', 'Chiller:Electric:EIR', 'Chiller:Electric:ReformulatedEIR', 'Chiller:Electric', 'Chiller:Absorption:Indirect', 'Chiller:Absorption', 'Chiller:ConstantCOP', 'Chiller:EngineDriven', 'Chiller:CombustionTurbine'], Field()]

    Component_8_Name: Annotated[str, Field()]

    Component_8_Demand_Calculation_Node_Name: Annotated[str, Field()]

    Component_8_Setpoint_Node_Name: Annotated[str, Field()]

    Component_8_Flow_Rate: Annotated[float, Field()]

    Component_8_Operation_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]

    Component_9_Object_Type: Annotated[Literal['ThermalStorage:Ice:Simple', 'ThermalStorage:Ice:Detailed', 'Chiller:Electric:EIR', 'Chiller:Electric:ReformulatedEIR', 'Chiller:Electric', 'Chiller:Absorption:Indirect', 'Chiller:Absorption', 'Chiller:ConstantCOP', 'Chiller:EngineDriven', 'Chiller:CombustionTurbine'], Field()]

    Component_9_Name: Annotated[str, Field()]

    Component_9_Demand_Calculation_Node_Name: Annotated[str, Field()]

    Component_9_Setpoint_Node_Name: Annotated[str, Field()]

    Component_9_Flow_Rate: Annotated[float, Field()]

    Component_9_Operation_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]

    Component_10_Object_Type: Annotated[Literal['ThermalStorage:Ice:Simple', 'ThermalStorage:Ice:Detailed', 'Chiller:Electric:EIR', 'Chiller:Electric:ReformulatedEIR', 'Chiller:Electric', 'Chiller:Absorption:Indirect', 'Chiller:Absorption', 'Chiller:ConstantCOP', 'Chiller:EngineDriven', 'Chiller:CombustionTurbine'], Field()]

    Component_10_Name: Annotated[str, Field()]

    Component_10_Demand_Calculation_Node_Name: Annotated[str, Field()]

    Component_10_Setpoint_Node_Name: Annotated[str, Field()]

    Component_10_Flow_Rate: Annotated[float, Field()]

    Component_10_Operation_Type: Annotated[Literal['Heating', 'Cooling', 'Dual'], Field()]