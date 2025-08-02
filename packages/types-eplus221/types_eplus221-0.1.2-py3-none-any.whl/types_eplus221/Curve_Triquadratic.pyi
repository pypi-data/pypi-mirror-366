from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Curve_Triquadratic(EpBunch):
    """Quadratic curve with three independent variables. Input consists of the curve name,"""

    Name: Annotated[str, Field(default=...)]

    Coefficient1_Constant: Annotated[float, Field()]

    Coefficient2_x2: Annotated[float, Field()]

    Coefficient3_x: Annotated[float, Field()]

    Coefficient4_y2: Annotated[float, Field()]

    Coefficient5_y: Annotated[float, Field()]

    Coefficient6_z2: Annotated[float, Field()]

    Coefficient7_z: Annotated[float, Field()]

    Coefficient8_x2y2: Annotated[float, Field()]

    Coefficient9_xy: Annotated[float, Field()]

    Coefficient10_xy2: Annotated[float, Field()]

    Coefficient11_x2y: Annotated[float, Field()]

    Coefficient12_x2z2: Annotated[float, Field()]

    Coefficient13_xz: Annotated[float, Field()]

    Coefficient14_xz2: Annotated[float, Field()]

    Coefficient15_x2z: Annotated[float, Field()]

    Coefficient16_y2z2: Annotated[float, Field()]

    Coefficient17_yz: Annotated[float, Field()]

    Coefficient18_yz2: Annotated[float, Field()]

    Coefficient19_y2z: Annotated[float, Field()]

    Coefficient20_x2y2z2: Annotated[float, Field()]

    Coefficient21_x2y2z: Annotated[float, Field()]

    Coefficient22_x2yz2: Annotated[float, Field()]

    Coefficient23_xy2z2: Annotated[float, Field()]

    Coefficient24_x2yz: Annotated[float, Field()]

    Coefficient25_xy2z: Annotated[float, Field()]

    Coefficient26_xyz2: Annotated[float, Field()]

    Coefficient27_xyz: Annotated[float, Field()]

    Minimum_Value_of_x: Annotated[float, Field()]

    Maximum_Value_of_x: Annotated[float, Field()]

    Minimum_Value_of_y: Annotated[float, Field()]

    Maximum_Value_of_y: Annotated[float, Field()]

    Minimum_Value_of_z: Annotated[float, Field()]

    Maximum_Value_of_z: Annotated[float, Field()]

    Minimum_Curve_Output: Annotated[float, Field()]
    """Specify the minimum value calculated by this curve object"""

    Maximum_Curve_Output: Annotated[float, Field()]
    """Specify the maximum value calculated by this curve object"""

    Input_Unit_Type_for_X: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance'], Field(default='Dimensionless')]

    Input_Unit_Type_for_Y: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance'], Field(default='Dimensionless')]

    Input_Unit_Type_for_Z: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance'], Field(default='Dimensionless')]

    Output_Unit_Type: Annotated[Literal['Dimensionless', 'Capacity', 'Power', 'Temperature'], Field(default='Dimensionless')]