from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Heating_Gas_Multistage(EpBunch):
    """Gas heating coil, multi-stage. If the coil is located directly in an air loop"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Temperature_Setpoint_Node_Name: Annotated[str, Field()]
    """optional, used if coil is temperature control and not load-base"""

    Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field()]
    """quadratic curve, PLF = a + b*PLR + c*PLR**2"""

    Parasitic_Gas_Load: Annotated[str, Field()]
    """parasitic gas load associated with the gas coil operation (i.e.,"""

    Number_of_Stages: Annotated[int, Field(default=..., ge=1, le=4)]
    """Enter the number of the following sets of data for coil"""

    Stage_1_Gas_Burner_Efficiency: Annotated[float, Field(default=..., gt=0.0)]

    Stage_1_Nominal_Capacity: Annotated[float, Field(default=..., gt=0.0)]

    Stage_1_Parasitic_Electric_Load: Annotated[str, Field()]
    """Stage 1 parasitic electric load associated with the gas coil operation"""

    Stage_2_Gas_Burner_Efficiency: Annotated[float, Field(gt=0.0)]

    Stage_2_Nominal_Capacity: Annotated[float, Field(gt=0.0)]

    Stage_2_Parasitic_Electric_Load: Annotated[str, Field()]
    """Stage 2 parasitic electric load associated with the gas coil operation"""

    Stage_3_Gas_Burner_Efficiency: Annotated[float, Field(gt=0.0)]

    Stage_3_Nominal_Capacity: Annotated[float, Field(gt=0.0)]

    Stage_3_Parasitic_Electric_Load: Annotated[str, Field()]
    """Stage 3 parasitic electric load associated with the gas coil operation"""

    Stage_4_Gas_Burner_Efficiency: Annotated[float, Field(gt=0.0)]

    Stage_4_Nominal_Capacity: Annotated[float, Field(gt=0.0)]

    Stage_4_Parasitic_Electric_Load: Annotated[str, Field()]
    """Stage 4 parasitic electric load associated with the gas coil operation"""