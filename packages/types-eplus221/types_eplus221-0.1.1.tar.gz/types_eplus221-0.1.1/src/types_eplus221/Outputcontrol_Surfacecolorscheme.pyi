from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Outputcontrol_Surfacecolorscheme(EpBunch):
    """This object is used to set colors for reporting on various building elements particularly for the"""

    Name: Annotated[str, Field(default=...)]
    """choose a name or use one of the DataSets"""

    Drawing_Element_1_Type: Annotated[Literal['Text', 'Walls', 'Windows', 'GlassDoors', 'Doors', 'Roofs', 'Floors', 'DetachedBuildingShades', 'DetachedFixedShades', 'AttachedBuildingShades', 'Photovoltaics', 'TubularDaylightDomes', 'TubularDaylightDiffusers', 'DaylightReferencePoint1', 'DaylightReferencePoint2'], Field()]

    Color_For_Drawing_Element_1: Annotated[int, Field(ge=0, le=255)]
    """use color number for output assignment (e.g. DXF)"""

    Drawing_Element_2_Type: Annotated[Literal['Text', 'Walls', 'Windows', 'GlassDoors', 'Doors', 'Roofs', 'Floors', 'DetachedBuildingShades', 'DetachedFixedShades', 'AttachedBuildingShades', 'Photovoltaics', 'TubularDaylightDomes', 'TubularDaylightDiffusers', 'DaylightReferencePoint1', 'DaylightReferencePoint2'], Field()]

    Color_For_Drawing_Element_2: Annotated[int, Field(ge=0, le=255)]
    """use color number for output assignment (e.g. DXF)"""

    Drawing_Element_3_Type: Annotated[Literal['Text', 'Walls', 'Windows', 'GlassDoors', 'Doors', 'Roofs', 'Floors', 'DetachedBuildingShades', 'DetachedFixedShades', 'AttachedBuildingShades', 'Photovoltaics', 'TubularDaylightDomes', 'TubularDaylightDiffusers', 'DaylightReferencePoint1', 'DaylightReferencePoint2'], Field()]

    Color_For_Drawing_Element_3: Annotated[int, Field(ge=0, le=255)]
    """use color number for output assignment (e.g. DXF)"""

    Drawing_Element_4_Type: Annotated[Literal['Text', 'Walls', 'Windows', 'GlassDoors', 'Doors', 'Roofs', 'Floors', 'DetachedBuildingShades', 'DetachedFixedShades', 'AttachedBuildingShades', 'Photovoltaics', 'TubularDaylightDomes', 'TubularDaylightDiffusers', 'DaylightReferencePoint1', 'DaylightReferencePoint2'], Field()]

    Color_For_Drawing_Element_4: Annotated[int, Field(ge=0, le=255)]
    """use color number for output assignment (e.g. DXF)"""

    Drawing_Element_5_Type: Annotated[Literal['Text', 'Walls', 'Windows', 'GlassDoors', 'Doors', 'Roofs', 'Floors', 'DetachedBuildingShades', 'DetachedFixedShades', 'AttachedBuildingShades', 'Photovoltaics', 'TubularDaylightDomes', 'TubularDaylightDiffusers', 'DaylightReferencePoint1', 'DaylightReferencePoint2'], Field()]

    Color_For_Drawing_Element_5: Annotated[int, Field(ge=0, le=255)]
    """use color number for output assignment (e.g. DXF)"""

    Drawing_Element_6_Type: Annotated[Literal['Text', 'Walls', 'Windows', 'GlassDoors', 'Doors', 'Roofs', 'Floors', 'DetachedBuildingShades', 'DetachedFixedShades', 'AttachedBuildingShades', 'Photovoltaics', 'TubularDaylightDomes', 'TubularDaylightDiffusers', 'DaylightReferencePoint1', 'DaylightReferencePoint2'], Field()]

    Color_For_Drawing_Element_6: Annotated[int, Field(ge=0, le=255)]
    """use color number for output assignment (e.g. DXF)"""

    Drawing_Element_7_Type: Annotated[Literal['Text', 'Walls', 'Windows', 'GlassDoors', 'Doors', 'Roofs', 'Floors', 'DetachedBuildingShades', 'DetachedFixedShades', 'AttachedBuildingShades', 'Photovoltaics', 'TubularDaylightDomes', 'TubularDaylightDiffusers', 'DaylightReferencePoint1', 'DaylightReferencePoint2'], Field()]

    Color_For_Drawing_Element_7: Annotated[int, Field(ge=0, le=255)]
    """use color number for output assignment (e.g. DXF)"""

    Drawing_Element_8_Type: Annotated[Literal['Text', 'Walls', 'Windows', 'GlassDoors', 'Doors', 'Roofs', 'Floors', 'DetachedBuildingShades', 'DetachedFixedShades', 'AttachedBuildingShades', 'Photovoltaics', 'TubularDaylightDomes', 'TubularDaylightDiffusers', 'DaylightReferencePoint1', 'DaylightReferencePoint2'], Field()]

    Color_For_Drawing_Element_8: Annotated[int, Field(ge=0, le=255)]
    """use color number for output assignment (e.g. DXF)"""

    Drawing_Element_9_Type: Annotated[Literal['Text', 'Walls', 'Windows', 'GlassDoors', 'Doors', 'Roofs', 'Floors', 'DetachedBuildingShades', 'DetachedFixedShades', 'AttachedBuildingShades', 'Photovoltaics', 'TubularDaylightDomes', 'TubularDaylightDiffusers', 'DaylightReferencePoint1', 'DaylightReferencePoint2'], Field()]

    Color_For_Drawing_Element_9: Annotated[int, Field(ge=0, le=255)]
    """use color number for output assignment (e.g. DXF)"""

    Drawing_Element_10_Type: Annotated[Literal['Text', 'Walls', 'Windows', 'GlassDoors', 'Doors', 'Roofs', 'Floors', 'DetachedBuildingShades', 'DetachedFixedShades', 'AttachedBuildingShades', 'Photovoltaics', 'TubularDaylightDomes', 'TubularDaylightDiffusers', 'DaylightReferencePoint1', 'DaylightReferencePoint2'], Field()]

    Color_For_Drawing_Element_10: Annotated[int, Field(ge=0, le=255)]
    """use color number for output assignment (e.g. DXF)"""

    Drawing_Element_11_Type: Annotated[Literal['Text', 'Walls', 'Windows', 'GlassDoors', 'Doors', 'Roofs', 'Floors', 'DetachedBuildingShades', 'DetachedFixedShades', 'AttachedBuildingShades', 'Photovoltaics', 'TubularDaylightDomes', 'TubularDaylightDiffusers', 'DaylightReferencePoint1', 'DaylightReferencePoint2'], Field()]

    Color_For_Drawing_Element_11: Annotated[int, Field(ge=0, le=255)]
    """use color number for output assignment (e.g. DXF)"""

    Drawing_Element_12_Type: Annotated[Literal['Text', 'Walls', 'Windows', 'GlassDoors', 'Doors', 'Roofs', 'Floors', 'DetachedBuildingShades', 'DetachedFixedShades', 'AttachedBuildingShades', 'Photovoltaics', 'TubularDaylightDomes', 'TubularDaylightDiffusers', 'DaylightReferencePoint1', 'DaylightReferencePoint2'], Field()]

    Color_For_Drawing_Element_12: Annotated[int, Field(ge=0, le=255)]
    """use color number for output assignment (e.g. DXF)"""

    Drawing_Element_13_Type: Annotated[Literal['Text', 'Walls', 'Windows', 'GlassDoors', 'Doors', 'Roofs', 'Floors', 'DetachedBuildingShades', 'DetachedFixedShades', 'AttachedBuildingShades', 'Photovoltaics', 'TubularDaylightDomes', 'TubularDaylightDiffusers', 'DaylightReferencePoint1', 'DaylightReferencePoint2'], Field()]

    Color_For_Drawing_Element_13: Annotated[int, Field(ge=0, le=255)]
    """use color number for output assignment (e.g. DXF)"""

    Drawing_Element_14_Type: Annotated[Literal['Text', 'Walls', 'Windows', 'GlassDoors', 'Doors', 'Roofs', 'Floors', 'DetachedBuildingShades', 'DetachedFixedShades', 'AttachedBuildingShades', 'Photovoltaics', 'TubularDaylightDomes', 'TubularDaylightDiffusers', 'DaylightReferencePoint1', 'DaylightReferencePoint2'], Field()]

    Color_For_Drawing_Element_14: Annotated[int, Field(ge=0, le=255)]
    """use color number for output assignment (e.g. DXF)"""

    Drawing_Element_15_Type: Annotated[Literal['Text', 'Walls', 'Windows', 'GlassDoors', 'Doors', 'Roofs', 'Floors', 'DetachedBuildingShades', 'DetachedFixedShades', 'AttachedBuildingShades', 'Photovoltaics', 'TubularDaylightDomes', 'TubularDaylightDiffusers', 'DaylightReferencePoint1', 'DaylightReferencePoint2'], Field()]

    Color_For_Drawing_Element_15: Annotated[int, Field(ge=0, le=255)]
    """use color number for output assignment (e.g. DXF)"""