from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceproperty_Exteriornaturalventedcavity(EpBunch):
    """Used to describe the decoupled layer, or baffle, and the characteristics of the cavity"""

    Name: Annotated[str, Field(default=...)]

    Boundary_Conditions_Model_Name: Annotated[str, Field(default=...)]
    """Enter the name of a SurfaceProperty:OtherSideConditionsModel object"""

    Area_Fraction_of_Openings: Annotated[float, Field(gt=0, le=1.0)]

    Thermal_Emissivity_of_Exterior_Baffle_Material: Annotated[float, Field(ge=0, le=1)]

    Solar_Absorbtivity_of_Exterior_Baffle: Annotated[float, Field(ge=0, le=1)]

    Height_Scale_for_BuoyancyDriven_Ventilation: Annotated[float, Field(gt=0.0)]

    Effective_Thickness_of_Cavity_Behind_Exterior_Baffle: Annotated[float, Field(gt=0.)]
    """if corrugated, use average depth"""

    Ratio_of_Actual_Surface_Area_to_Projected_Surface_Area: Annotated[float, Field(ge=0.8, le=2.0, default=1.0)]
    """this parameter is used to help account for corrugations in the collector"""

    Roughness_of_Exterior_Surface: Annotated[Literal['VeryRough', 'Rough', 'MediumRough', 'MediumSmooth', 'Smooth', 'VerySmooth'], Field(default=...)]

    Effectiveness_for_Perforations_with_Respect_to_Wind: Annotated[float, Field(gt=0, le=1.5, default=0.25)]

    Discharge_Coefficient_for_Openings_with_Respect_to_Buoyancy_Driven_Flow: Annotated[float, Field(gt=0.0, le=1.5, default=0.65)]

    Surface_1_Name: Annotated[str, Field(default=...)]

    Surface_2_Name: Annotated[str, Field()]

    Surface_3_Name: Annotated[str, Field()]

    Surface_4_Name: Annotated[str, Field()]

    Surface_5_Name: Annotated[str, Field()]

    Surface_6_Name: Annotated[str, Field()]

    Surface_7_Name: Annotated[str, Field()]

    Surface_8_Name: Annotated[str, Field()]

    Surface_9_Name: Annotated[str, Field()]

    Surface_10_Name: Annotated[str, Field()]