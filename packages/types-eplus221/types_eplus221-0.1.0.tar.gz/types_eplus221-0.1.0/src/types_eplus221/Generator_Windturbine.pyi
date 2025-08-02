from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Generator_Windturbine(EpBunch):
    """Wind turbine generator."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Rotor_Type: Annotated[Literal['HorizontalAxisWindTurbine', 'VerticalAxisWindTurbine'], Field(default='HorizontalAxisWindTurbine')]
    """allowed values are: Horizontal Axis Wind Turbine or Vertical Axis Wind Turbine"""

    Power_Control: Annotated[Literal['FixedSpeedFixedPitch', 'FixedSpeedVariablePitch', 'VariableSpeedFixedPitch', 'VariableSpeedVariablePitch'], Field(default='VariableSpeedVariablePitch')]
    """Constant power output is obtained in the last three control types"""

    Rated_Rotor_Speed: Annotated[float, Field(default=..., gt=0.0)]

    Rotor_Diameter: Annotated[float, Field(default=..., gt=0.0)]
    """This field is the diameter of the perpendicular circle of the Vertical Axis Wind Turbine system"""

    Overall_Height: Annotated[float, Field(default=..., gt=0.0)]
    """This field is the height of the hub for the Horizontal Axis Wind Turbines and"""

    Number_Of_Blades: Annotated[str, Field(default='3')]

    Rated_Power: Annotated[float, Field(default=..., gt=0.0)]
    """This field is the nominal power at the rated wind speed."""

    Rated_Wind_Speed: Annotated[float, Field(default=..., gt=0.0)]

    Cut_In_Wind_Speed: Annotated[float, Field(default=..., gt=0.0)]

    Cut_Out_Wind_Speed: Annotated[float, Field(default=..., gt=0.0)]

    Fraction_System_Efficiency: Annotated[float, Field(gt=0.0, le=1.0, default=0.835)]

    Maximum_Tip_Speed_Ratio: Annotated[float, Field(gt=0.0, le=12.0, default=5.0)]

    Maximum_Power_Coefficient: Annotated[float, Field(gt=0.0, le=0.59, default=0.25)]
    """This field should be input if the rotor type is Horizontal Axis Wind Turbine"""

    Annual_Local_Average_Wind_Speed: Annotated[float, Field(gt=0.0)]

    Height_For_Local_Average_Wind_Speed: Annotated[float, Field(gt=0.0, default=50.0)]

    Blade_Chord_Area: Annotated[float, Field()]

    Blade_Drag_Coefficient: Annotated[float, Field(default=0.9)]
    """This field is only for Vertical Axis Wind Turbine.."""

    Blade_Lift_Coefficient: Annotated[float, Field(default=0.05)]
    """This field is only for Vertical Axis Wind Turbine.."""

    Power_Coefficient_C1: Annotated[float, Field(gt=0.0, default=0.5176)]
    """This field is only available for Horizontal Axis Wind Turbine."""

    Power_Coefficient_C2: Annotated[float, Field(gt=0.0, default=116.0)]

    Power_Coefficient_C3: Annotated[float, Field(gt=0.0, default=0.4)]

    Power_Coefficient_C4: Annotated[float, Field(ge=0.0, default=0.0)]

    Power_Coefficient_C5: Annotated[float, Field(gt=0.0, default=5.0)]

    Power_Coefficient_C6: Annotated[float, Field(gt=0.0, default=21.0)]