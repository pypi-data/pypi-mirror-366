from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Pump_Variablespeed_Condensate(EpBunch):
    """This pump model is described in the ASHRAE secondary HVAC toolkit."""

    Name: Annotated[str, Field(default=...)]

    Inlet_Node_Name: Annotated[str, Field(default=...)]

    Outlet_Node_Name: Annotated[str, Field(default=...)]

    Design_Steam_Volume_Flow_Rate: Annotated[str, Field()]
    """this is the volume of steam before condensation, the volume of condensate is much lower and calculated from steam density"""

    Design_Pump_Head: Annotated[str, Field(default='179352')]
    """default head is 60 feet"""

    Design_Power_Consumption: Annotated[str, Field()]
    """When autosized the type of scaling factor is chosen in the input field Design Power Sizing Method"""

    Motor_Efficiency: Annotated[float, Field(gt=0.0, le=1.0, default=0.9)]
    """This is the motor efficiency only. When the Design Power Consumption is autosized using PowerPerFlowPerPressure,"""

    Fraction_Of_Motor_Inefficiencies_To_Fluid_Stream: Annotated[str, Field(default='0.0')]

    Coefficient_1_Of_The_Part_Load_Performance_Curve: Annotated[str, Field(default='0.0')]

    Coefficient_2_Of_The_Part_Load_Performance_Curve: Annotated[str, Field(default='1.0')]

    Coefficient_3_Of_The_Part_Load_Performance_Curve: Annotated[str, Field(default='0.0')]

    Coefficient_4_Of_The_Part_Load_Performance_Curve: Annotated[str, Field(default='0.0')]

    Pump_Flow_Rate_Schedule_Name: Annotated[str, Field()]
    """Modifies the rated flow rate of the pump on a time basis. Default is"""

    Zone_Name: Annotated[str, Field()]
    """optional, if used pump losses transfered to zone as internal gains"""

    Skin_Loss_Radiative_Fraction: Annotated[float, Field(ge=0.0, le=1.0)]
    """optional. If zone identified in previous field then this determines"""

    Design_Power_Sizing_Method: Annotated[Literal['PowerPerFlow', 'PowerPerFlowPerPressure'], Field(default='PowerPerFlowPerPressure')]
    """Used to indicate which sizing factor is used to calculate Design Power Consumption."""

    Design_Electric_Power_Per_Unit_Flow_Rate: Annotated[float, Field(gt=0, default=348701.1)]
    """Used to size Design Power Consumption from design flow rate"""

    Design_Shaft_Power_Per_Unit_Flow_Rate_Per_Unit_Head: Annotated[float, Field(gt=0, default=1.282051282)]
    """Used to size Design Power Consumption from design flow rate for head and motor efficiency"""

    End_Use_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""