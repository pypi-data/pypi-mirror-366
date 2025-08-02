from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceproperty_Convectioncoefficients_Multiplesurface(EpBunch):
    """Allow user settable interior and/or exterior convection coefficients."""

    Surface_Type: Annotated[Literal['AllExteriorSurfaces', 'AllExteriorWindows', 'AllExteriorWalls', 'AllExteriorRoofs', 'AllExteriorFloors', 'AllInteriorSurfaces', 'AllInteriorWalls', 'AllInteriorWindows', 'AllInteriorCeilings', 'AllInteriorFloors'], Field(default=...)]

    Convection_Coefficient_1_Location: Annotated[Literal['Outside', 'Inside'], Field(default=...)]

    Convection_Coefficient_1_Type: Annotated[Literal['Value', 'Schedule', 'Simple', 'SimpleCombined', 'TARP', 'DOE-2', 'MoWitt', 'AdaptiveConvectionAlgorithm', 'ASHRAEVerticalWall', 'WaltonUnstableHorizontalOrTilt', 'WaltonStableHorizontalOrTilt', 'FisherPedersenCeilingDiffuserWalls', 'FisherPedersenCeilingDiffuserCeiling', 'FisherPedersenCeilingDiffuserFloor', 'AlamdariHammondStableHorizontal', 'AlamdariHammondUnstableHorizontal', 'AlamdariHammondVerticalWall', 'KhalifaEq3WallAwayFromHeat', 'KhalifaEq4CeilingAwayFromHeat', 'KhalifaEq5WallNearHeat', 'KhalifaEq6NonHeatedWalls', 'KhalifaEq7Ceiling', 'AwbiHattonHeatedFloor', 'AwbiHattonHeatedWall', 'BeausoleilMorrisonMixedAssistedWall', 'BeausoleilMorrisonMixedOpposingWall', 'BeausoleilMorrisonMixedStableFloor', 'BeausoleilMorrisonMixedUnstableFloor', 'BeausoleilMorrisonMixedStableCeiling', 'BeausoleilMorrisonMixedUnstableCeiling', 'FohannoPolidoriVerticalWall', 'KaradagChilledCeiling', 'ISO15099Windows', 'GoldsteinNovoselacCeilingDiffuserWindow', 'GoldsteinNovoselacCeilingDiffuserWalls', 'GoldsteinNovoselacCeilingDiffuserFloor', 'NusseltJurges', 'McAdams', 'Mitchell', 'BlockenWindard', 'EmmelVertical', 'EmmelRoof', 'ClearRoof', 'UserCurve'], Field(default=...)]

    Convection_Coefficient_1: Annotated[str, Field()]
    """used if Convection Type=Value, min and max limits are set in HeatBalanceAlgorithm object."""

    Convection_Coefficient_1_Schedule_Name: Annotated[str, Field()]
    """used if Convection Type=Schedule, min and max limits are set in HeatBalanceAlgorithm object."""

    Convection_Coefficient_1_User_Curve_Name: Annotated[str, Field()]
    """used if Convection Type = UserCurve"""

    Convection_Coefficient_2_Location: Annotated[Literal['Outside', 'Inside'], Field()]

    Convection_Coefficient_2_Type: Annotated[Literal['Value', 'Schedule', 'Simple', 'SimpleCombined', 'TARP', 'DOE-2', 'MoWitt', 'AdaptiveConvectionAlgorithm', 'ASHRAEVerticalWall', 'WaltonUnstableHorizontalOrTilt', 'WaltonStableHorizontalOrTilt', 'FisherPedersenCeilingDiffuserWalls', 'FisherPedersenCeilingDiffuserCeiling', 'FisherPedersenCeilingDiffuserFloor', 'AlamdariHammondStableHorizontal', 'AlamdariHammondUnstableHorizontal', 'AlamdariHammondVerticalWall', 'KhalifaEq3WallAwayFromHeat', 'KhalifaEq4CeilingAwayFromHeat', 'KhalifaEq5WallNearHeat', 'KhalifaEq6NonHeatedWalls', 'KhalifaEq7Ceiling', 'AwbiHattonHeatedFloor', 'AwbiHattonHeatedWall', 'BeausoleilMorrisonMixedAssistedWall', 'BeausoleilMorrisonMixedOpposingWall', 'BeausoleilMorrisonMixedStableFloor', 'BeausoleilMorrisonMixedUnstableFloor', 'BeausoleilMorrisonMixedStableCeiling', 'BeausoleilMorrisonMixedUnstableCeiling', 'FohannoPolidoriVerticalWall', 'KaradagChilledCeiling', 'ISO15099Windows', 'GoldsteinNovoselacCeilingDiffuserWindow', 'GoldsteinNovoselacCeilingDiffuserWalls', 'GoldsteinNovoselacCeilingDiffuserFloor', 'NusseltJurges', 'McAdams', 'Mitchell', 'BlockenWindard', 'EmmelVertical', 'EmmelRoof', 'ClearRoof', 'UserCurve'], Field()]

    Convection_Coefficient_2: Annotated[str, Field(default='.1')]
    """used if Convection Type=Value, min and max limits are set in HeatBalanceAlgorithm object."""

    Convection_Coefficient_2_Schedule_Name: Annotated[str, Field()]
    """used if Convection Type=Schedule, min and max limits are set in HeatBalanceAlgorithm object."""

    Convection_Coefficient_2_User_Curve_Name: Annotated[str, Field()]
    """used if Convection Type = UserCurve"""