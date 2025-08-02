from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Daylighting_Controls(EpBunch):
    """Dimming of overhead electric lighting is determined from each reference point."""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Daylighting_Method: Annotated[Literal['SplitFlux', 'DElight'], Field(default='SplitFlux')]

    Availability_Schedule_Name: Annotated[str, Field()]

    Lighting_Control_Type: Annotated[Literal['Continuous', 'Stepped', 'ContinuousOff'], Field(default='Continuous')]

    Minimum_Input_Power_Fraction_For_Continuous_Or_Continuousoff_Dimming_Control: Annotated[float, Field(ge=0.0, le=0.6, default=0.3)]

    Minimum_Light_Output_Fraction_For_Continuous_Or_Continuousoff_Dimming_Control: Annotated[float, Field(ge=0.0, le=0.6, default=0.2)]

    Number_Of_Stepped_Control_Steps: Annotated[int, Field(ge=1, default=1)]
    """The number of steps, excluding off, in a stepped lighting control system."""

    Probability_Lighting_Will_Be_Reset_When_Needed_In_Manual_Stepped_Control: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Glare_Calculation_Daylighting_Reference_Point_Name: Annotated[str, Field()]

    Glare_Calculation_Azimuth_Angle_Of_View_Direction_Clockwise_From_Zone_Y_Axis: Annotated[str, Field(default='0')]

    Maximum_Allowable_Discomfort_Glare_Index: Annotated[float, Field(ge=1, default=22)]
    """The default is for general office work"""

    Delight_Gridding_Resolution: Annotated[float, Field(gt=0.0)]
    """Maximum surface area for nodes in gridding all surfaces in the DElight zone."""

    Daylighting_Reference_Point_1_Name: Annotated[str, Field(default=...)]

    Fraction_Of_Zone_Controlled_By_Reference_Point_1: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Illuminance_Setpoint_At_Reference_Point_1: Annotated[float, Field(ge=0.0, default=500)]

    Daylighting_Reference_Point_2_Name: Annotated[str, Field()]

    Fraction_Of_Zone_Controlled_By_Reference_Point_2: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Illuminance_Setpoint_At_Reference_Point_2: Annotated[float, Field(ge=0.0, default=500)]

    Daylighting_Reference_Point_3_Name: Annotated[str, Field()]

    Fraction_Of_Zone_Controlled_By_Reference_Point_3: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Illuminance_Setpoint_At_Reference_Point_3: Annotated[float, Field(ge=0.0, default=500)]

    Daylighting_Reference_Point_4_Name: Annotated[str, Field()]

    Fraction_Of_Zone_Controlled_By_Reference_Point_4: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Illuminance_Setpoint_At_Reference_Point_4: Annotated[float, Field(ge=0.0, default=500)]

    Daylighting_Reference_Point_5_Name: Annotated[str, Field()]

    Fraction_Of_Zone_Controlled_By_Reference_Point_5: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Illuminance_Setpoint_At_Reference_Point_5: Annotated[float, Field(ge=0.0, default=500)]

    Daylighting_Reference_Point_6_Name: Annotated[str, Field()]

    Fraction_Of_Zone_Controlled_By_Reference_Point_6: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Illuminance_Setpoint_At_Reference_Point_6: Annotated[float, Field(ge=0.0, default=500)]

    Daylighting_Reference_Point_7_Name: Annotated[str, Field()]

    Fraction_Of_Zone_Controlled_By_Reference_Point_7: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Illuminance_Setpoint_At_Reference_Point_7: Annotated[float, Field(ge=0.0, default=500)]

    Daylighting_Reference_Point_8_Name: Annotated[str, Field()]

    Fraction_Of_Zone_Controlled_By_Reference_Point_8: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Illuminance_Setpoint_At_Reference_Point_8: Annotated[float, Field(ge=0.0, default=500)]

    Daylighting_Reference_Point_9_Name: Annotated[str, Field()]

    Fraction_Of_Zone_Controlled_By_Reference_Point_9: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Illuminance_Setpoint_At_Reference_Point_9: Annotated[float, Field(ge=0.0, default=500)]

    Daylighting_Reference_Point_10_Name: Annotated[str, Field()]

    Fraction_Of_Zone_Controlled_By_Reference_Point_10: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Illuminance_Setpoint_At_Reference_Point_10: Annotated[float, Field(ge=0.0, default=500)]