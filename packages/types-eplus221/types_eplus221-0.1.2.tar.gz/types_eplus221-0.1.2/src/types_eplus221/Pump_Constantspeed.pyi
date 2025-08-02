from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Pump_Constantspeed(EpBunch):
    """This pump model is described in the ASHRAE secondary HVAC toolkit."""

    Name: Annotated[str, Field(default=...)]

    Inlet_Node_Name: Annotated[str, Field(default=...)]

    Outlet_Node_Name: Annotated[str, Field(default=...)]

    Design_Flow_Rate: Annotated[str, Field()]

    Design_Pump_Head: Annotated[str, Field(default='179352')]
    """default head is 60 feet"""

    Design_Power_Consumption: Annotated[str, Field()]
    """When autosized the type of scaling factor is chosen in the input field Design Power Sizing Method"""

    Motor_Efficiency: Annotated[float, Field(gt=0.0, le=1.0, default=0.9)]
    """This is the motor efficiency only. When the Design Power Consumption is autosized using PowerPerFlowPerPressure,"""

    Fraction_of_Motor_Inefficiencies_to_Fluid_Stream: Annotated[str, Field(default='0.0')]

    Pump_Control_Type: Annotated[Literal['Continuous', 'Intermittent'], Field(default='Continuous')]

    Pump_Flow_Rate_Schedule_Name: Annotated[str, Field()]
    """Modifies the rated flow rate of the pump on a time basis. Default is"""

    Pump_Curve_Name: Annotated[str, Field()]
    """This references any single independent variable polynomial curve in order to"""

    Impeller_Diameter: Annotated[float, Field()]
    """"D" in above expression in field A6"""

    Rotational_Speed: Annotated[float, Field()]
    """"N" in above expression in field A6"""

    Zone_Name: Annotated[str, Field()]
    """optional, if used pump losses transfered to zone as internal gains"""

    Skin_Loss_Radiative_Fraction: Annotated[float, Field(ge=0.0, le=1.0)]
    """optional. If zone identified in previous field then this determines"""

    Design_Power_Sizing_Method: Annotated[Literal['PowerPerFlow', 'PowerPerFlowPerPressure'], Field(default='PowerPerFlowPerPressure')]
    """Used to indicate which sizing factor is used to calculate Design Power Consumption."""

    Design_Electric_Power_per_Unit_Flow_Rate: Annotated[float, Field(gt=0, default=348701.1)]
    """Used to size Design Power Consumption from design flow rate"""

    Design_Shaft_Power_per_Unit_Flow_Rate_per_Unit_Head: Annotated[float, Field(gt=0, default=1.282051282)]
    """Used to size Design Power Consumption from design flow rate for head and motor efficiency"""

    EndUse_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""