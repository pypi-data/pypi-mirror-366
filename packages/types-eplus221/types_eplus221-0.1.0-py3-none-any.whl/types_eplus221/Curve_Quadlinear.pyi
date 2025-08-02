from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Curve_Quadlinear(EpBunch):
    """Linear curve with four independent variables."""

    Name: Annotated[str, Field(default=...)]

    Coefficient1_Constant: Annotated[float, Field(default=...)]

    Coefficient2_W: Annotated[float, Field(default=...)]

    Coefficient3_X: Annotated[float, Field(default=...)]

    Coefficient4_Y: Annotated[float, Field(default=...)]

    Coefficient5_Z: Annotated[float, Field(default=...)]

    Minimum_Value_Of_W: Annotated[float, Field(default=...)]

    Maximum_Value_Of_W: Annotated[float, Field(default=...)]

    Minimum_Value_Of_X: Annotated[float, Field(default=...)]

    Maximum_Value_Of_X: Annotated[float, Field(default=...)]

    Minimum_Value_Of_Y: Annotated[float, Field(default=...)]

    Maximum_Value_Of_Y: Annotated[float, Field(default=...)]

    Minimum_Value_Of_Z: Annotated[float, Field(default=...)]

    Maximum_Value_Of_Z: Annotated[float, Field(default=...)]

    Minimum_Curve_Output: Annotated[float, Field()]
    """Specify the minimum value calculated by this curve object"""

    Maximum_Curve_Output: Annotated[float, Field()]
    """Specify the maximum value calculated by this curve object"""

    Input_Unit_Type_For_W: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance', 'VolumetricFlowPerPower'], Field(default='Dimensionless')]

    Input_Unit_Type_For_X: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance', 'VolumetricFlowPerPower'], Field(default='Dimensionless')]

    Input_Unit_Type_For_Y: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance', 'VolumetricFlowPerPower'], Field(default='Dimensionless')]

    Input_Unit_Type_For_Z: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance', 'VolumetricFlowPerPower'], Field(default='Dimensionless')]