from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceconvectionalgorithm_Outside_Adaptivemodelselections(EpBunch):
    """Options to change the individual convection model equations for dynamic selection when using AdaptiveConvectiongAlgorithm"""

    Name: Annotated[str, Field()]

    Wind_Convection_Windward_Vertical_Wall_Equation_Source: Annotated[Literal['SimpleCombined', 'TARPWindward', 'MoWiTTWindward', 'DOE2Windward', 'NusseltJurges', 'McAdams', 'Mitchell', 'BlockenWindward', 'EmmelVertical', 'UserCurve'], Field(default='TARPWindward')]

    Wind_Convection_Windward_Equation_Vertical_Wall_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Outside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Wind_Convection_Leeward_Vertical_Wall_Equation_Source: Annotated[Literal['SimpleCombined', 'TARPLeeward', 'MoWiTTLeeward', 'DOE2Leeward', 'EmmelVertical', 'NusseltJurges', 'McAdams', 'Mitchell', 'UserCurve'], Field(default='TARPLeeward')]

    Wind_Convection_Leeward_Vertical_Wall_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Outside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Wind_Convection_Horizontal_Roof_Equation_Source: Annotated[Literal['SimpleCombined', 'TARPWindward', 'MoWiTTWindward', 'DOE2Windward', 'NusseltJurges', 'McAdams', 'Mitchell', 'BlockenWindward', 'EmmelRoof', 'ClearRoof', 'UserCurve'], Field(default='ClearRoof')]

    Wind_Convection_Horizontal_Roof_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Outside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Natural_Convection_Vertical_Wall_Equation_Source: Annotated[Literal['ASHRAEVerticalWall', 'AlamdariHammondVerticalWall', 'FohannoPolidoriVerticalWall', 'ISO15099Windows', 'UserCurve', 'None'], Field(default='ASHRAEVerticalWall')]
    """This is for vertical walls"""

    Natural_Convection_Vertical_Wall_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Outside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Natural_Convection_Stable_Horizontal_Equation_Source: Annotated[Literal['WaltonStableHorizontalOrTilt', 'AlamdariHammondStableHorizontal', 'UserCurve', 'None'], Field(default='WaltonStableHorizontalOrTilt')]
    """This is for horizontal surfaces with heat flow directed for stable thermal stratification"""

    Natural_Convection_Stable_Horizontal_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Outside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Natural_Convection_Unstable_Horizontal_Equation_Source: Annotated[Literal['WaltonUnstableHorizontalOrTilt', 'AlamdariHammondUnstableHorizontal', 'UserCurve', 'None'], Field(default='WaltonUnstableHorizontalOrTilt')]

    Natural_Convection_Unstable_Horizontal_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Outside:UserCurve named in this field is used when the previous field is set to UserCurve"""