from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceproperty_Exteriornaturalventedcavity(EpBunch):
    """Used to describe the decoupled layer, or baffle, and the characteristics of the cavity"""

    Name: Annotated[str, Field(default=...)]

    Boundary_Conditions_Model_Name: Annotated[str, Field(default=...)]
    """Enter the name of a SurfaceProperty:OtherSideConditionsModel object"""

    Area_Fraction_Of_Openings: Annotated[float, Field(gt=0, le=1.0)]

    Thermal_Emissivity_Of_Exterior_Baffle_Material: Annotated[float, Field(ge=0, le=1)]

    Solar_Absorbtivity_Of_Exterior_Baffle: Annotated[float, Field(ge=0, le=1)]

    Height_Scale_For_Buoyancy_Driven_Ventilation: Annotated[float, Field(gt=0.0)]

    Effective_Thickness_Of_Cavity_Behind_Exterior_Baffle: Annotated[float, Field(gt=0.)]
    """if corrugated, use average depth"""

    Ratio_Of_Actual_Surface_Area_To_Projected_Surface_Area: Annotated[float, Field(ge=0.8, le=2.0, default=1.0)]
    """this parameter is used to help account for corrugations in the collector"""

    Roughness_Of_Exterior_Surface: Annotated[Literal['VeryRough', 'Rough', 'MediumRough', 'MediumSmooth', 'Smooth', 'VerySmooth'], Field(default=...)]

    Effectiveness_For_Perforations_With_Respect_To_Wind: Annotated[float, Field(gt=0, le=1.5, default=0.25)]

    Discharge_Coefficient_For_Openings_With_Respect_To_Buoyancy_Driven_Flow: Annotated[float, Field(gt=0.0, le=1.5, default=0.65)]

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