from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Cooling_Water_Detailedgeometry(EpBunch):
    """Chilled water cooling coil, detailed flat fin coil model for continuous plate fins,"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Maximum_Water_Flow_Rate: Annotated[str, Field(default='autosize')]

    Tube_Outside_Surface_Area: Annotated[str, Field(default='autosize')]
    """Tube Primary Surface Area"""

    Total_Tube_Inside_Area: Annotated[str, Field(default='autosize')]
    """Total tube inside surface area"""

    Fin_Surface_Area: Annotated[str, Field(default='autosize')]

    Minimum_Airflow_Area: Annotated[str, Field(default='autosize')]

    Coil_Depth: Annotated[str, Field(default='autosize')]

    Fin_Diameter: Annotated[str, Field(default='autosize')]
    """Fin diameter or the coil height"""

    Fin_Thickness: Annotated[float, Field(gt=0.0, default=.0015)]

    Tube_Inside_Diameter: Annotated[str, Field(default='.01445')]
    """Inner diameter of tubes"""

    Tube_Outside_Diameter: Annotated[str, Field(default='.0159')]
    """Outer diameter of tubes"""

    Tube_Thermal_Conductivity: Annotated[float, Field(ge=1.0, default=386.0)]

    Fin_Thermal_Conductivity: Annotated[float, Field(ge=1.0, default=204.0)]

    Fin_Spacing: Annotated[str, Field(default='.0018')]
    """Fin spacing or distance"""

    Tube_Depth_Spacing: Annotated[str, Field(default='.026')]

    Number_Of_Tube_Rows: Annotated[str, Field(default='4')]

    Number_Of_Tubes_Per_Row: Annotated[str, Field(default='autosize')]

    Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Condensate_Collection_Water_Storage_Tank_Name: Annotated[str, Field()]

    Design_Water_Temperature_Difference: Annotated[float, Field(gt=0.0)]
    """This input field is optional. If specified, it is used for sizing the Design Water Flow Rate."""