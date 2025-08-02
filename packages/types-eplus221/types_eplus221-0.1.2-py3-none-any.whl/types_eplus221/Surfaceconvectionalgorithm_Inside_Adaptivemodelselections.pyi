from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceconvectionalgorithm_Inside_Adaptivemodelselections(EpBunch):
    """Options to change the individual convection model equations for dynamic selection when using AdaptiveConvectiongAlgorithm"""

    Name: Annotated[str, Field()]

    Simple_Buoyancy_Vertical_Wall_Equation_Source: Annotated[Literal['ASHRAEVerticalWall', 'AlamdariHammondVerticalWall', 'KhalifaEq3WallAwayFromHeat', 'KhalifaEq6NonHeatedWalls', 'FohannoPolidoriVerticalWall', 'ISO15099Windows', 'UserCurve'], Field(default='FohannoPolidoriVerticalWall')]
    """Applies to zone with no HVAC or when HVAC is off"""

    Simple_Buoyancy_Vertical_Wall_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Simple_Buoyancy_Stable_Horizontal_Equation_Source: Annotated[Literal['WaltonStableHorizontalOrTilt', 'AlamdariHammondStableHorizontal', 'UserCurve'], Field(default='AlamdariHammondStableHorizontal')]
    """Applies to zone with no HVAC or when HVAC is off"""

    Simple_Buoyancy_Stable_Horizontal_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Simple_Buoyancy_Unstable_Horizontal_Equation_Source: Annotated[Literal['WaltonUnstableHorizontalOrTilt', 'AlamdariHammondUnstableHorizontal', 'UserCurve'], Field(default='AlamdariHammondUnstableHorizontal')]
    """Applies to zone with no HVAC or when HVAC is off"""

    Simple_Buoyancy_Unstable_Horizontal_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Simple_Buoyancy_Stable_Tilted_Equation_Source: Annotated[Literal['WaltonStableHorizontalOrTilt', 'AlamdariHammondStableHorizontal', 'UserCurve'], Field(default='WaltonStableHorizontalOrTilt')]
    """Applies to zone with no HVAC or when HVAC is off"""

    Simple_Buoyancy_Stable_Tilted_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Simple_Buoyancy_Unstable_Tilted_Equation_Source: Annotated[Literal['WaltonUnstableHorizontalOrTilt', 'AlamdariHammondUnstableHorizontal', 'UserCurve'], Field(default='WaltonUnstableHorizontalOrTilt')]
    """Applies to zone with no HVAC or when HVAC is off"""

    Simple_Buoyancy_Unstable_Tilted_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Simple_Buoyancy_Windows_Equation_Source: Annotated[Literal['ASHRAEVerticalWall', 'AlamdariHammondVerticalWall', 'FohannoPolidoriVerticalWall', 'KaradagChilledCeiling', 'ISO15099Windows', 'UserCurve'], Field(default='ISO15099Windows')]
    """Applies to zone with no HVAC or when HVAC is off"""

    Simple_Buoyancy_Windows_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Floor_Heat_Ceiling_Cool_Vertical_Wall_Equation_Source: Annotated[Literal['ASHRAEVerticalWall', 'AlamdariHammondVerticalWall', 'KhalifaEq3WallAwayFromHeat', 'FohannoPolidoriVerticalWall', 'ISO15099Windows', 'UserCurve'], Field(default='KhalifaEq3WallAwayFromHeat')]
    """Applies to zone with in-floor heating and/or in-ceiling cooling"""

    Floor_Heat_Ceiling_Cool_Vertical_Wall_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Floor_Heat_Ceiling_Cool_Stable_Horizontal_Equation_Source: Annotated[Literal['WaltonStableHorizontalOrTilt', 'AlamdariHammondStableHorizontal', 'UserCurve'], Field(default='AlamdariHammondStableHorizontal')]
    """Applies to zone with in-floor heating and/or in-ceiling cooling"""

    Floor_Heat_Ceiling_Cool_Stable_Horizontal_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Floor_Heat_Ceiling_Cool_Unstable_Horizontal_Equation_Source: Annotated[Literal['WaltonUnstableHorizontalOrTilt', 'AlamdariHammondUnstableHorizontal', 'KhalifaEq4CeilingAwayFromHeat', 'UserCurve'], Field(default='KhalifaEq4CeilingAwayFromHeat')]
    """Applies to zone with in-floor heating and/or in-ceiling cooling"""

    Floor_Heat_Ceiling_Cool_Unstable_Horizontal_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Floor_Heat_Ceiling_Cool_Heated_Floor_Equation_Source: Annotated[Literal['WaltonUnstableHorizontalOrTilt', 'AlamdariHammondUnstableHorizontal', 'AwbiHattonHeatedFloor', 'UserCurve'], Field(default='AwbiHattonHeatedFloor')]
    """Applies to zone with in-floor heating and/or in-ceiling cooling"""

    Floor_Heat_Ceiling_Cool_Heated_Floor_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Floor_Heat_Ceiling_Cool_Chilled_Ceiling_Equation_Source: Annotated[Literal['WaltonUnstableHorizontalOrTilt', 'AlamdariHammondUnstableHorizontal', 'KaradagChilledCeiling', 'UserCurve'], Field(default='KaradagChilledCeiling')]
    """Applies to zone with in-floor heating and/or in-ceiling cooling"""

    Floor_Heat_Ceiling_Cool_Chilled_Ceiling_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Floor_Heat_Ceiling_Cool_Stable_Tilted_Equation_Source: Annotated[Literal['WaltonStableHorizontalOrTilt', 'AlamdariHammondStableHorizontal', 'ISO15099Windows', 'UserCurve'], Field(default='WaltonStableHorizontalOrTilt')]
    """Applies to zone with in-floor heating and/or in-ceiling cooling"""

    Floor_Heat_Ceiling_Cool_Stable_Tilted_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Floor_Heat_Ceiling_Cool_Unstable_Tilted_Equation_Source: Annotated[Literal['WaltonUnstableHorizontalOrTilt', 'AlamdariHammondUnstableHorizontal', 'ISO15099Windows', 'UserCurve'], Field(default='WaltonUnstableHorizontalOrTilt')]
    """Applies to zone with in-floor heating and/or in-ceiling cooling"""

    Floor_Heat_Ceiling_Cool_Unstable_Tilted_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Floor_Heat_Ceiling_Cool_Window_Equation_Source: Annotated[Literal['ASHRAEVerticalWall', 'AlamdariHammondVerticalWall', 'ISO15099Windows', 'UserCurve'], Field(default='ISO15099Windows')]
    """Applies to zone with in-floor heating and/or in-ceiling cooling"""

    Floor_Heat_Ceiling_Cool_Window_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Wall_Panel_Heating_Vertical_Wall_Equation_Source: Annotated[Literal['ASHRAEVerticalWall', 'AlamdariHammondVerticalWall', 'KhalifaEq6NonHeatedWalls', 'FohannoPolidoriVerticalWall', 'ISO15099Windows', 'UserCurve'], Field(default='KhalifaEq6NonHeatedWalls')]
    """Applies to zone with in-wall panel heating"""

    Wall_Panel_Heating_Vertical_Wall_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Wall_Panel_Heating_Heated_Wall_Equation_Source: Annotated[Literal['ASHRAEVerticalWall', 'AlamdariHammondVerticalWall', 'KhalifaEq5WallNearHeat', 'AwbiHattonHeatedWall', 'FohannoPolidoriVerticalWall', 'ISO15099Windows', 'UserCurve'], Field(default='AwbiHattonHeatedWall')]
    """Applies to zone with in-wall panel heating"""

    Wall_Panel_Heating_Heated_Wall_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Wall_Panel_Heating_Stable_Horizontal_Equation_Source: Annotated[Literal['WaltonStableHorizontalOrTilt', 'AlamdariHammondStableHorizontal', 'UserCurve'], Field(default='AlamdariHammondStableHorizontal')]
    """Applies to zone with in-wall panel heating"""

    Wall_Panel_Heating_Stable_Horizontal_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Wall_Panel_Heating_Unstable_Horizontal_Equation_Source: Annotated[Literal['ASHRAEVerticalWall', 'WaltonUnstableHorizontalOrTilt', 'AlamdariHammondUnstableHorizontal', 'KhalifaEq7Ceiling', 'KaradagChilledCeiling', 'UserCurve'], Field(default='KhalifaEq7Ceiling')]
    """Applies to zone with in-wall panel heating"""

    Wall_Panel_Heating_Unstable_Horizontal_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Wall_Panel_Heating_Stable_Tilted_Equation_Source: Annotated[Literal['WaltonStableHorizontalOrTilt', 'AlamdariHammondStableHorizontal', 'ISO15099Windows', 'UserCurve'], Field(default='WaltonStableHorizontalOrTilt')]
    """Applies to zone with in-wall panel heating"""

    Wall_Panel_Heating_Stable_Tilted_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Wall_Panel_Heating_Unstable_Tilted_Equation_Source: Annotated[Literal['WaltonUnstableHorizontalOrTilt', 'AlamdariHammondUnstableHorizontal', 'ISO15099Windows', 'UserCurve'], Field(default='WaltonUnstableHorizontalOrTilt')]
    """Applies to zone with in-wall panel heating"""

    Wall_Panel_Heating_Unstable_Tilted_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Wall_Panel_Heating_Window_Equation_Source: Annotated[Literal['ASHRAEVerticalWall', 'AlamdariHammondVerticalWall', 'FohannoPolidoriVerticalWall', 'ISO15099Windows', 'UserCurve'], Field(default='ISO15099Windows')]
    """Applies to zone with in-wall panel heating"""

    Wall_Panel_Heating_Window_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Convective_Zone_Heater_Vertical_Wall_Equation_Source: Annotated[Literal['ASHRAEVerticalWall', 'AlamdariHammondVerticalWall', 'KhalifaEq3WallAwayFromHeat', 'KhalifaEq6NonHeatedWalls', 'FohannoPolidoriVerticalWall', 'ISO15099Windows', 'UserCurve'], Field(default='FohannoPolidoriVerticalWall')]
    """Applies to zone with convective heater"""

    Convective_Zone_Heater_Vertical_Wall_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Convective_Zone_Heater_Vertical_Walls_Near_Heater_Equation_Source: Annotated[Literal['ASHRAEVerticalWall', 'AlamdariHammondVerticalWall', 'KhalifaEq5WallNearHeat', 'AwbiHattonHeatedWall', 'FohannoPolidoriVerticalWall', 'ISO15099Windows', 'UserCurve'], Field(default='KhalifaEq5WallNearHeat')]
    """Applies to zone with convective heater"""

    Convective_Zone_Heater_Vertical_Walls_Near_Heater_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Convective_Zone_Heater_Stable_Horizontal_Equation_Source: Annotated[Literal['WaltonStableHorizontalOrTilt', 'AlamdariHammondStableHorizontal', 'UserCurve'], Field(default='AlamdariHammondStableHorizontal')]
    """Applies to zone with convective heater"""

    Convective_Zone_Heater_Stable_Horizontal_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Convective_Zone_Heater_Unstable_Horizontal_Equation_Source: Annotated[Literal['WaltonUnstableHorizontalOrTilt', 'AlamdariHammondUnstableHorizontal', 'KhalifaEq4CeilingAwayFromHeat', 'KhalifaEq7Ceiling', 'UserCurve'], Field(default='KhalifaEq7Ceiling')]
    """Applies to zone with convective heater"""

    Convective_Zone_Heater_Unstable_Horizontal_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Convective_Zone_Heater_Stable_Tilted_Equation_Source: Annotated[Literal['WaltonStableHorizontalOrTilt', 'AlamdariHammondStableHorizontal', 'UserCurve'], Field(default='WaltonStableHorizontalOrTilt')]
    """Applies to zone with convective heater"""

    Convective_Zone_Heater_Stable_Tilted_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Convective_Zone_Heater_Unstable_Tilted_Equation_Source: Annotated[Literal['WaltonUnstableHorizontalOrTilt', 'AlamdariHammondUnstableHorizontal', 'UserCurve'], Field(default='WaltonUnstableHorizontalOrTilt')]
    """Applies to zone with convective heater"""

    Convective_Zone_Heater_Unstable_Tilted_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Convective_Zone_Heater_Windows_Equation_Source: Annotated[Literal['ASHRAEVerticalWall', 'AlamdariHammondVerticalWall', 'KhalifaEq3WallAwayFromHeat', 'FohannoPolidoriVerticalWall', 'ISO15099Windows', 'UserCurve'], Field(default='ISO15099Windows')]
    """Applies to zone with convective heater"""

    Convective_Zone_Heater_Windows_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Central_Air_Diffuser_Wall_Equation_Source: Annotated[Literal['ASHRAEVerticalWall', 'FisherPedersenCeilingDiffuserWalls', 'AlamdariHammondVerticalWall', 'BeausoleilMorrisonMixedAssistedWall', 'BeausoleilMorrisonMixedOpposingWall', 'FohannoPolidoriVerticalWall', 'ISO15099Windows', 'GoldsteinNovoselacCeilingDiffuserWalls', 'UserCurve'], Field(default='GoldsteinNovoselacCeilingDiffuserWalls')]
    """Applies to zone with mechanical forced central air with diffusers"""

    Central_Air_Diffuser_Wall_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Central_Air_Diffuser_Ceiling_Equation_Source: Annotated[Literal['FisherPedersenCeilingDiffuserCeiling', 'BeausoleilMorrisonMixedStableCeiling', 'BeausoleilMorrisonMixedUnstableCeiling', 'UserCurve'], Field(default='FisherPedersenCeilingDiffuserCeiling')]
    """Applies to zone with mechanical forced central air with diffusers"""

    Central_Air_Diffuser_Ceiling_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Central_Air_Diffuser_Floor_Equation_Source: Annotated[Literal['FisherPedersenCeilingDiffuserFloor', 'BeausoleilMorrisonMixedStableFloor', 'BeausoleilMorrisonMixedUnstableFloor', 'GoldsteinNovoselacCeilingDiffuserFloor', 'UserCurve'], Field(default='GoldsteinNovoselacCeilingDiffuserFloor')]
    """Applies to zone with mechanical forced central air with diffusers"""

    Central_Air_Diffuser_Floor_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Central_Air_Diffuser_Window_Equation_Source: Annotated[Literal['ASHRAEVerticalWall', 'FisherPedersenCeilingDiffuserWalls', 'BeausoleilMorrisonMixedAssistedWall', 'BeausoleilMorrisonMixedOpposingWall', 'FohannoPolidoriVerticalWall', 'AlamdariHammondVerticalWall', 'ISO15099Windows', 'GoldsteinNovoselacCeilingDiffuserWindow', 'UserCurve'], Field(default='GoldsteinNovoselacCeilingDiffuserWindow')]
    """Applies to zone with mechanical forced central air with diffusers"""

    Central_Air_Diffuser_Window_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Mechanical_Zone_Fan_Circulation_Vertical_Wall_Equation_Source: Annotated[Literal['KhalifaEq3WallAwayFromHeat', 'ASHRAEVerticalWall', 'FisherPedersenCeilingDiffuserWalls', 'AlamdariHammondVerticalWall', 'BeausoleilMorrisonMixedAssistedWall', 'BeausoleilMorrisonMixedOpposingWall', 'FohannoPolidoriVerticalWall', 'ISO15099Windows', 'GoldsteinNovoselacCeilingDiffuserWalls', 'UserCurve'], Field(default='KhalifaEq3WallAwayFromHeat')]
    """reference choice fields"""

    Mechanical_Zone_Fan_Circulation_Vertical_Wall_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Mechanical_Zone_Fan_Circulation_Stable_Horizontal_Equation_Source: Annotated[Literal['WaltonStableHorizontalOrTilt', 'AlamdariHammondStableHorizontal', 'UserCurve'], Field(default='AlamdariHammondStableHorizontal')]
    """reference choice fields"""

    Mechanical_Zone_Fan_Circulation_Stable_Horizontal_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Mechanical_Zone_Fan_Circulation_Unstable_Horizontal_Equation_Source: Annotated[Literal['KhalifaEq4CeilingAwayFromHeat', 'WaltonUnstableHorizontalOrTilt', 'AlamdariHammondUnstableHorizontal', 'UserCurve'], Field(default='KhalifaEq4CeilingAwayFromHeat')]
    """reference choice fields"""

    Mechanical_Zone_Fan_Circulation_Unstable_Horizontal_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Mechanical_Zone_Fan_Circulation_Stable_Tilted_Equation_Source: Annotated[Literal['WaltonStableHorizontalOrTilt', 'UserCurve'], Field(default='WaltonStableHorizontalOrTilt')]
    """reference choice fields"""

    Mechanical_Zone_Fan_Circulation_Stable_Tilted_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Mechanical_Zone_Fan_Circulation_Unstable_Tilted_Equation_Source: Annotated[Literal['WaltonUnstableHorizontalOrTilt', 'AlamdariHammondUnstableHorizontal', 'UserCurve'], Field(default='WaltonUnstableHorizontalOrTilt')]
    """reference choice fields"""

    Mechanical_Zone_Fan_Circulation_Unstable_Tilted_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Mechanical_Zone_Fan_Circulation_Window_Equation_Source: Annotated[Literal['ASHRAEVerticalWall', 'AlamdariHammondVerticalWall', 'FohannoPolidoriVerticalWall', 'ISO15099Windows', 'GoldsteinNovoselacCeilingDiffuserWindow', 'UserCurve'], Field(default='ISO15099Windows')]
    """reference choice fields"""

    Mechanical_Zone_Fan_Circulation_Window_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Mixed_Regime_Buoyancy_Assisting_Flow_on_Walls_Equation_Source: Annotated[Literal['BeausoleilMorrisonMixedAssistedWall', 'AlamdariHammondVerticalWall', 'FohannoPolidoriVerticalWall', 'ASHRAEVerticalWall', 'FisherPedersenCeilingDiffuserWalls', 'GoldsteinNovoselacCeilingDiffuserWalls', 'UserCurve'], Field(default='BeausoleilMorrisonMixedAssistedWall')]
    """reference choice fields"""

    Mixed_Regime_Buoyancy_Assisting_Flow_on_Walls_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Mixed_Regime_Buoyancy_Opposing_Flow_on_Walls_Equation_Source: Annotated[Literal['BeausoleilMorrisonMixedOpposingWall', 'AlamdariHammondVerticalWall', 'FohannoPolidoriVerticalWall', 'ASHRAEVerticalWall', 'FisherPedersenCeilingDiffuserWalls', 'GoldsteinNovoselacCeilingDiffuserWalls', 'UserCurve'], Field(default='BeausoleilMorrisonMixedOpposingWall')]
    """reference choice fields"""

    Mixed_Regime_Buoyancy_Opposing_Flow_on_Walls_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Mixed_Regime_Stable_Floor_Equation_Source: Annotated[Literal['BeausoleilMorrisonMixedStableFloor', 'WaltonStableHorizontalOrTilt', 'AlamdariHammondStableHorizontal', 'UserCurve'], Field(default='BeausoleilMorrisonMixedStableFloor')]
    """reference choice fields"""

    Mixed_Regime_Stable_Floor_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Mixed_Regime_Unstable_Floor_Equation_Source: Annotated[Literal['BeausoleilMorrisonMixedUnstableFloor', 'WaltonUnstableHorizontalOrTilt', 'AlamdariHammondUnstableHorizontal', 'UserCurve'], Field(default='BeausoleilMorrisonMixedUnstableFloor')]
    """reference choice fields"""

    Mixed_Regime_Unstable_Floor_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Mixed_Regime_Stable_Ceiling_Equation_Source: Annotated[Literal['BeausoleilMorrisonMixedStableCeiling', 'WaltonStableHorizontalOrTilt', 'AlamdariHammondStableHorizontal', 'UserCurve'], Field(default='BeausoleilMorrisonMixedStableCeiling')]
    """reference choice fields"""

    Mixed_Regime_Stable_Ceiling_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Mixed_Regime_Unstable_Ceiling_Equation_Source: Annotated[Literal['BeausoleilMorrisonMixedUnstableCeiling', 'WaltonUnstableHorizontalOrTilt', 'AlamdariHammondUnstableHorizontal', 'UserCurve'], Field(default='BeausoleilMorrisonMixedUnstableCeiling')]
    """reference choice fields"""

    Mixed_Regime_Unstable_Ceiling_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""

    Mixed_Regime_Window_Equation_Source: Annotated[Literal['GoldsteinNovoselacCeilingDiffuserWindow', 'ISO15099Windows', 'UserCurve'], Field(default='GoldsteinNovoselacCeilingDiffuserWindow')]
    """reference choice fields"""

    Mixed_Regime_Window_Equation_User_Curve_Name: Annotated[str, Field()]
    """The SurfaceConvectionAlgorithm:Inside:UserCurve named in this field is used when the previous field is set to UserCurve"""