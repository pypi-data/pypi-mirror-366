from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Foundation_Kiva(EpBunch):
    """Refined definition of the foundation surface construction used to"""

    Name: Annotated[str, Field(default=...)]

    Initial_Indoor_Air_Temperature: Annotated[float, Field()]
    """Indoor air temperature used for Kiva initialization (prior to warmup period)"""

    Interior_Horizontal_Insulation_Material_Name: Annotated[str, Field()]

    Interior_Horizontal_Insulation_Depth: Annotated[float, Field(ge=0.0, default=0.0)]
    """Distance from the slab bottom to the top of interior horizontal"""

    Interior_Horizontal_Insulation_Width: Annotated[float, Field(gt=0.0)]
    """Extent of insulation as measured from the wall interior"""

    Interior_Vertical_Insulation_Material_Name: Annotated[str, Field()]

    Interior_Vertical_Insulation_Depth: Annotated[float, Field(gt=0.0)]
    """Extent of insulation as measured from the wall top to the bottom"""

    Exterior_Horizontal_Insulation_Material_Name: Annotated[str, Field()]

    Exterior_Horizontal_Insulation_Depth: Annotated[float, Field(ge=0.0)]
    """Distance from the exterior grade to the top of exterior horizontal"""

    Exterior_Horizontal_Insulation_Width: Annotated[float, Field(ge=0.0, default=0.0)]
    """Extent of insulation as measured from the wall exterior"""

    Exterior_Vertical_Insulation_Material_Name: Annotated[str, Field()]

    Exterior_Vertical_Insulation_Depth: Annotated[float, Field(gt=0.0)]
    """Extent of insulation as measured from the wall top to the bottom"""

    Wall_Height_Above_Grade: Annotated[float, Field(ge=0.0, default=0.2)]
    """Distance from the exterior grade to the wall top"""

    Wall_Depth_Below_Slab: Annotated[float, Field(ge=0.0, default=0.0)]
    """Distance from the slab bottom to the bottom of the foundation wall"""

    Footing_Wall_Construction_Name: Annotated[str, Field()]
    """Defines the below-grade surface construction for slabs. Required"""

    Footing_Material_Name: Annotated[str, Field()]

    Footing_Depth: Annotated[float, Field(gt=0.0, default=0.3)]
    """Top-to-bottom dimension of the footing (not to be confused with its"""

    Custom_Block_1_Material_Name: Annotated[str, Field()]

    Custom_Block_1_Depth: Annotated[float, Field(gt=0.0)]
    """Top-to-bottom dimension of the block downward."""

    Custom_Block_1_X_Position: Annotated[float, Field()]
    """Position outward (+) or inward (-) relative to the foundation wall"""

    Custom_Block_1_Z_Position: Annotated[float, Field()]
    """Position downward (+) relative to the foundation wall top"""

    Custom_Block_2_Material_Name: Annotated[str, Field()]

    Custom_Block_2_Depth: Annotated[float, Field(gt=0.0)]

    Custom_Block_2_X_Position: Annotated[float, Field()]

    Custom_Block_2_Z_Position: Annotated[float, Field()]

    Custom_Block_3_Material_Name: Annotated[str, Field()]

    Custom_Block_3_Depth: Annotated[float, Field(gt=0.0)]

    Custom_Block_3_X_Position: Annotated[float, Field()]

    Custom_Block_3_Z_Position: Annotated[float, Field()]

    Custom_Block_4_Material_Name: Annotated[str, Field()]

    Custom_Block_4_Depth: Annotated[float, Field(gt=0.0)]

    Custom_Block_4_X_Position: Annotated[float, Field()]

    Custom_Block_4_Z_Position: Annotated[float, Field()]

    Custom_Block_5_Material_Name: Annotated[str, Field()]

    Custom_Block_5_Depth: Annotated[float, Field(gt=0.0)]

    Custom_Block_5_X_Position: Annotated[float, Field()]

    Custom_Block_5_Z_Position: Annotated[float, Field()]

    Custom_Block_6_Material_Name: Annotated[str, Field()]

    Custom_Block_6_Depth: Annotated[float, Field(gt=0.0)]

    Custom_Block_6_X_Position: Annotated[float, Field()]

    Custom_Block_6_Z_Position: Annotated[float, Field()]

    Custom_Block_7_Material_Name: Annotated[str, Field()]

    Custom_Block_7_Depth: Annotated[float, Field(gt=0.0)]

    Custom_Block_7_X_Position: Annotated[float, Field()]

    Custom_Block_7_Z_Position: Annotated[float, Field()]

    Custom_Block_8_Material_Name: Annotated[str, Field()]

    Custom_Block_8_Depth: Annotated[float, Field(gt=0.0)]

    Custom_Block_8_X_Position: Annotated[float, Field()]

    Custom_Block_8_Z_Position: Annotated[float, Field()]

    Custom_Block_9_Material_Name: Annotated[str, Field()]

    Custom_Block_9_Depth: Annotated[float, Field(gt=0.0)]

    Custom_Block_9_X_Position: Annotated[float, Field()]

    Custom_Block_9_Z_Position: Annotated[float, Field()]

    Custom_Block_10_Material_Name: Annotated[str, Field()]

    Custom_Block_10_Depth: Annotated[float, Field()]

    Custom_Block_10_X_Position: Annotated[float, Field(gt=0.0)]

    Custom_Block_10_Z_Position: Annotated[float, Field()]