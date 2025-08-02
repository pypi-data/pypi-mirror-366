from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Construction_Complexfenestrationstate(EpBunch):
    """Describes one state for a complex glazing system"""

    Name: Annotated[str, Field(default=...)]

    Basis_Type: Annotated[Literal['LBNLWINDOW', 'UserDefined'], Field(default='LBNLWINDOW')]

    Basis_Symmetry_Type: Annotated[Literal['Axisymmetric', 'None'], Field()]

    Window_Thermal_Model: Annotated[str, Field(default=...)]

    Basis_Matrix_Name: Annotated[str, Field(default=...)]

    Solar_Optical_Complex_Front_Transmittance_Matrix_Name: Annotated[str, Field(default=...)]

    Solar_Optical_Complex_Back_Reflectance_Matrix_Name: Annotated[str, Field(default=...)]

    Visible_Optical_Complex_Front_Transmittance_Matrix_Name: Annotated[str, Field(default=...)]

    Visible_Optical_Complex_Back_Transmittance_Matrix_Name: Annotated[str, Field(default=...)]

    Outside_Layer_Name: Annotated[str, Field(default=...)]

    Outside_Layer_Directional_Front_Absoptance_Matrix_Name: Annotated[str, Field(default=...)]

    Outside_Layer_Directional_Back_Absoptance_Matrix_Name: Annotated[str, Field(default=...)]

    Gap_1_Name: Annotated[str, Field()]

    CFS_Gap_1_Directional_Front_Absoptance_Matrix_Name: Annotated[str, Field()]
    """Reserved for future use. Leave it blank for this version"""

    CFS_Gap_1_Directional_Back_Absoptance_Matrix_Name: Annotated[str, Field()]
    """Reserved for future use. Leave it blank for this version"""

    Layer_2_Name: Annotated[str, Field()]

    Layer_2_Directional_Front_Absoptance_Matrix_Name: Annotated[str, Field()]

    Layer_2_Directional_Back_Absoptance_Matrix_Name: Annotated[str, Field()]

    Gap_2_Name: Annotated[str, Field()]

    Gap_2_Directional_Front_Absoptance_Matrix_Name: Annotated[str, Field()]
    """Reserved for future use. Leave it blank for this version"""

    Gap_2_Directional_Back_Absoptance_Matrix_Name: Annotated[str, Field()]
    """Reserved for future use. Leave it blank for this version"""

    Layer_3_Material: Annotated[str, Field()]

    Layer_3_Directional_Front_Absoptance_Matrix_Name: Annotated[str, Field()]

    Layer_3_Directional_Back_Absoptance_Matrix_Name: Annotated[str, Field()]

    Gap_3_Name: Annotated[str, Field()]

    Gap_3_Directional_Front_Absoptance_Matrix_Name: Annotated[str, Field()]
    """Reserved for future use. Leave it blank for this version"""

    Gap_3_Directional_Back_Absoptance_Matrix_Name: Annotated[str, Field()]
    """Reserved for future use. Leave it blank for this version"""

    Layer_4_Name: Annotated[str, Field()]

    Layer_4_Directional_Front_Absoptance_Matrix_Name: Annotated[str, Field()]

    Layer_4_Directional_Back_Absoptance_Matrix_Name: Annotated[str, Field()]

    Gap_4_Name: Annotated[str, Field()]

    Gap_4_Directional_Front_Absoptance_Matrix_Name: Annotated[str, Field()]
    """Reserved for future use. Leave it blank for this version"""

    Gap_4_Directional_Back_Absoptance_Matrix_Name: Annotated[str, Field()]
    """Reserved for future use. Leave it blank for this version"""

    Layer_5_Name: Annotated[str, Field()]

    Layer_5_Directional_Front_Absoptance_Matrix_Name: Annotated[str, Field()]

    Layer_5_Directional_Back_Absoptance_Matrix_Name: Annotated[str, Field()]