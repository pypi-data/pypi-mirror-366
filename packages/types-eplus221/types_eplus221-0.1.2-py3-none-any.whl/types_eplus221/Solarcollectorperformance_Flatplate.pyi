from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Solarcollectorperformance_Flatplate(EpBunch):
    """Thermal and optical performance parameters for a single flat plate solar collector"""

    Name: Annotated[str, Field(default=...)]

    Gross_Area: Annotated[float, Field(default=..., gt=0)]

    Test_Fluid: Annotated[Literal['Water'], Field(default='Water')]

    Test_Flow_Rate: Annotated[float, Field(default=..., gt=0)]

    Test_Correlation_Type: Annotated[Literal['Inlet', 'Average', 'Outlet'], Field(default=...)]

    Coefficient_1_of_Efficiency_Equation: Annotated[float, Field(default=...)]
    """Y-intercept term"""

    Coefficient_2_of_Efficiency_Equation: Annotated[float, Field(default=...)]
    """1st Order term"""

    Coefficient_3_of_Efficiency_Equation: Annotated[float, Field()]
    """2nd order term"""

    Coefficient_2_of_Incident_Angle_Modifier: Annotated[float, Field()]
    """1st order term"""

    Coefficient_3_of_Incident_Angle_Modifier: Annotated[float, Field()]
    """2nd order term"""