from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Thermalstorage_Chilledwater_Stratified(EpBunch):
    """Chilled water storage with a stratified, multi-node tank. The chilled water is"""

    Name: Annotated[str, Field(default=...)]

    Tank_Volume: Annotated[float, Field(default=..., gt=0.0)]

    Tank_Height: Annotated[float, Field(default=..., gt=0.0)]
    """Height is measured in the axial direction for horizontal cylinders"""

    Tank_Shape: Annotated[Literal['VerticalCylinder', 'HorizontalCylinder', 'Other'], Field(default='VerticalCylinder')]

    Tank_Perimeter: Annotated[float, Field(ge=0.0)]
    """Only used if Tank Shape is Other"""

    Setpoint_Temperature_Schedule_Name: Annotated[str, Field()]

    Deadband_Temperature_Difference: Annotated[float, Field(ge=0.0, default=0.0)]

    Temperature_Sensor_Height: Annotated[str, Field()]

    Minimum_Temperature_Limit: Annotated[float, Field()]

    Nominal_Cooling_Capacity: Annotated[float, Field()]

    Ambient_Temperature_Indicator: Annotated[Literal['Schedule', 'Zone', 'Outdoors'], Field(default=...)]

    Ambient_Temperature_Schedule_Name: Annotated[str, Field()]

    Ambient_Temperature_Zone_Name: Annotated[str, Field()]

    Ambient_Temperature_Outdoor_Air_Node_Name: Annotated[str, Field()]
    """required for Ambient Temperature Indicator=Outdoors"""

    Uniform_Skin_Loss_Coefficient_per_Unit_Area_to_Ambient_Temperature: Annotated[float, Field(ge=0.0)]

    Use_Side_Inlet_Node_Name: Annotated[str, Field()]

    Use_Side_Outlet_Node_Name: Annotated[str, Field()]

    Use_Side_Heat_Transfer_Effectiveness: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]
    """The use side effectiveness in the stratified tank model is a simplified analogy of"""

    Use_Side_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for use side. Schedule value > 0 means the system is available."""

    Use_Side_Inlet_Height: Annotated[float, Field(ge=0.0, default=autocalculate)]
    """Defaults to top of tank"""

    Use_Side_Outlet_Height: Annotated[float, Field(ge=0.0, default=0.0)]
    """Defaults to bottom of tank"""

    Use_Side_Design_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]

    Source_Side_Inlet_Node_Name: Annotated[str, Field()]

    Source_Side_Outlet_Node_Name: Annotated[str, Field()]

    Source_Side_Heat_Transfer_Effectiveness: Annotated[float, Field(gt=0.0, le=1.0, default=1.0)]
    """The source side effectiveness in the stratified tank model is a simplified analogy of"""

    Source_Side_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for use side. Schedule value > 0 means the system is available."""

    Source_Side_Inlet_Height: Annotated[float, Field(ge=0.0, default=0.0)]
    """Defaults to bottom of tank"""

    Source_Side_Outlet_Height: Annotated[float, Field(ge=0.0, default=autocalculate)]
    """Defaults to top of tank"""

    Source_Side_Design_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]

    Tank_Recovery_Time: Annotated[float, Field(gt=0.0, default=4.0)]
    """Parameter for autosizing design flow rates for indirectly cooled water tanks"""

    Inlet_Mode: Annotated[Literal['Fixed', 'Seeking'], Field(default='Fixed')]

    Number_of_Nodes: Annotated[int, Field(ge=1, le=10, default=1)]

    Additional_Destratification_Conductivity: Annotated[float, Field(ge=0.0, default=0.0)]

    Node_1_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_2_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_3_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_4_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_5_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_6_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_7_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_8_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_9_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_10_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]