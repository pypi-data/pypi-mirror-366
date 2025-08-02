from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Curve_Quadlinear(EpBunch):
    """Linear curve with four independent variables."""

    Name: Annotated[str, Field(default=...)]

    Coefficient1_Constant: Annotated[float, Field(default=...)]

    Coefficient2_w: Annotated[float, Field(default=...)]

    Coefficient3_x: Annotated[float, Field(default=...)]

    Coefficient4_y: Annotated[float, Field(default=...)]

    Coefficient5_z: Annotated[float, Field(default=...)]

    Minimum_Value_of_w: Annotated[float, Field(default=...)]

    Maximum_Value_of_w: Annotated[float, Field(default=...)]

    Minimum_Value_of_x: Annotated[float, Field(default=...)]

    Maximum_Value_of_x: Annotated[float, Field(default=...)]

    Minimum_Value_of_y: Annotated[float, Field(default=...)]

    Maximum_Value_of_y: Annotated[float, Field(default=...)]

    Minimum_Value_of_z: Annotated[float, Field(default=...)]

    Maximum_Value_of_z: Annotated[float, Field(default=...)]

    Minimum_Curve_Output: Annotated[float, Field()]
    """Specify the minimum value calculated by this curve object"""

    Maximum_Curve_Output: Annotated[float, Field()]
    """Specify the maximum value calculated by this curve object"""

    Input_Unit_Type_for_w: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance', 'VolumetricFlowPerPower'], Field(default='Dimensionless')]

    Input_Unit_Type_for_x: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance', 'VolumetricFlowPerPower'], Field(default='Dimensionless')]

    Input_Unit_Type_for_y: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance', 'VolumetricFlowPerPower'], Field(default='Dimensionless')]

    Input_Unit_Type_for_z: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance', 'VolumetricFlowPerPower'], Field(default='Dimensionless')]