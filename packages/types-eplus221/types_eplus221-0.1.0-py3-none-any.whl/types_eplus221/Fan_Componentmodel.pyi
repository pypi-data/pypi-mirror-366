from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Fan_Componentmodel(EpBunch):
    """A detailed fan type for constant-air-volume (CAV) and variable-air-volume (VAV)"""

    Name: Annotated[str, Field(default=...)]

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Maximum_Flow_Rate: Annotated[str, Field()]

    Minimum_Flow_Rate: Annotated[str, Field()]

    Fan_Sizing_Factor: Annotated[float, Field(ge=1.0, default=1.0)]
    """Applied to specified or autosized max fan airflow"""

    Fan_Wheel_Diameter: Annotated[float, Field(default=..., gt=0.0)]
    """Diameter of wheel outer circumference"""

    Fan_Outlet_Area: Annotated[float, Field(default=..., gt=0.0)]
    """Area at fan outlet plane for determining discharge velocity pressure"""

    Maximum_Fan_Static_Efficiency: Annotated[float, Field(default=..., gt=0.0, le=1.0)]
    """Maximum ratio between power delivered to air and fan shaft input power"""

    Euler_Number_At_Maximum_Fan_Static_Efficiency: Annotated[float, Field(default=..., gt=0.0)]
    """Euler number (Eu) determined from fan performance data"""

    Maximum_Dimensionless_Fan_Airflow: Annotated[float, Field(default=..., gt=0.0)]
    """Corresponds to maximum ratio between fan airflow and"""

    Motor_Fan_Pulley_Ratio: Annotated[float, Field(gt=0.0, default=1.0)]
    """Ratio of motor pulley diameter to fan pulley diameter"""

    Belt_Maximum_Torque: Annotated[float, Field(default=..., gt=0.0)]
    """Maximum torque transmitted by belt"""

    Belt_Sizing_Factor: Annotated[float, Field(ge=1.0, default=1.0)]
    """Applied to specified or autosized max torque transmitted by belt"""

    Belt_Fractional_Torque_Transition: Annotated[float, Field(ge=0.0, le=1.0, default=0.167)]
    """Region 1 to 2 curve transition for belt normalized efficiency"""

    Motor_Maximum_Speed: Annotated[float, Field(default=..., gt=0.0)]
    """Maximum rotational speed of fan motor shaft"""

    Maximum_Motor_Output_Power: Annotated[float, Field(default=..., gt=0.0)]
    """Maximum power input to drive belt by motor"""

    Motor_Sizing_Factor: Annotated[float, Field(ge=1.0, default=1.0)]
    """Applied to specified or autosized motor output power"""

    Motor_In_Airstream_Fraction: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]
    """0.0 means motor outside air stream"""

    Vfd_Efficiency_Type: Annotated[Literal['Speed', 'Power'], Field()]
    """Efficiency depends on fraction of full-load motor speed"""

    Maximum_Vfd_Output_Power: Annotated[float, Field(default=..., gt=0.0)]
    """Maximum power input to motor by VFD"""

    Vfd_Sizing_Factor: Annotated[float, Field(ge=1.0, default=1.0)]
    """Applied to specified or autosized VFD output power"""

    Fan_Pressure_Rise_Curve_Name: Annotated[str, Field(default=...)]
    """Pressure rise depends on volumetric flow, system resistances,"""

    Duct_Static_Pressure_Reset_Curve_Name: Annotated[str, Field(default=...)]
    """Function of fan volumetric flow"""

    Normalized_Fan_Static_Efficiency_Curve_Name_Non_Stall_Region: Annotated[str, Field(default=...)]
    """xfan <= 0"""

    Normalized_Fan_Static_Efficiency_Curve_Name_Stall_Region: Annotated[str, Field(default=...)]
    """xfan > 0"""

    Normalized_Dimensionless_Airflow_Curve_Name_Non_Stall_Region: Annotated[str, Field(default=...)]
    """xspd <= 0"""

    Normalized_Dimensionless_Airflow_Curve_Name_Stall_Region: Annotated[str, Field(default=...)]
    """xspd > 0"""

    Maximum_Belt_Efficiency_Curve_Name: Annotated[str, Field()]
    """Determines maximum fan drive belt efficiency in log space"""

    Normalized_Belt_Efficiency_Curve_Name___Region_1: Annotated[str, Field()]
    """Region 1 (0 <= xbelt < xbelt,trans)"""

    Normalized_Belt_Efficiency_Curve_Name___Region_2: Annotated[str, Field()]
    """Region 2 (xbelt,trans <= xbelt <= 1)"""

    Normalized_Belt_Efficiency_Curve_Name___Region_3: Annotated[str, Field()]
    """Determines normalized drive belt efficiency Region 3 (xbelt > 1)"""

    Maximum_Motor_Efficiency_Curve_Name: Annotated[str, Field()]
    """Curve should have minimum > 0.0 and maximum of 1.0"""

    Normalized_Motor_Efficiency_Curve_Name: Annotated[str, Field()]
    """Curve should have minimum > 0.0 and maximum of 1.0"""

    Vfd_Efficiency_Curve_Name: Annotated[str, Field()]
    """Determines VFD efficiency as function of motor load or speed fraction"""

    End_Use_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""