from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Solarcollector_Unglazedtranspired(EpBunch):
    """Unglazed transpired solar collector (UTSC) used to condition outdoor air. This type of"""

    Name: Annotated[str, Field(default=...)]

    Boundary_Conditions_Model_Name: Annotated[str, Field(default=...)]
    """Enter the name of a SurfaceProperty:OtherSideConditionsModel object"""

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this collector. Schedule value > 0 means it is available."""

    Inlet_Node_Name: Annotated[str, Field()]
    """required field if no SolarCollector:UnglazedTranspired:Multisystem"""

    Outlet_Node_Name: Annotated[str, Field()]
    """required field if no SolarCollector:UnglazedTranspired:Multisystem"""

    Setpoint_Node_Name: Annotated[str, Field()]
    """This node is where the mixed air setpoint is determined."""

    Zone_Node_Name: Annotated[str, Field()]
    """This node is used to identify the affected zone"""

    Free_Heating_Setpoint_Schedule_Name: Annotated[str, Field()]

    Diameter_Of_Perforations_In_Collector: Annotated[float, Field(default=..., gt=0)]

    Distance_Between_Perforations_In_Collector: Annotated[float, Field(default=..., gt=0)]

    Thermal_Emissivity_Of_Collector_Surface: Annotated[float, Field(default=..., ge=0, le=1)]

    Solar_Absorbtivity_Of_Collector_Surface: Annotated[float, Field(default=..., ge=0, le=1)]

    Effective_Overall_Height_Of_Collector: Annotated[float, Field(default=..., gt=0.0)]

    Effective_Gap_Thickness_Of_Plenum_Behind_Collector: Annotated[float, Field(default=..., gt=0.)]
    """if corrugated, use average depth"""

    Effective_Cross_Section_Area_Of_Plenum_Behind_Collector: Annotated[float, Field(default=..., gt=0)]
    """if corrugated, use average depth"""

    Hole_Layout_Pattern_For_Pitch: Annotated[Literal['Triangle', 'Square'], Field(default='Square')]

    Heat_Exchange_Effectiveness_Correlation: Annotated[Literal['Kutscher1994', 'VanDeckerHollandsBrunger2001'], Field(default='Kutscher1994')]

    Ratio_Of_Actual_Collector_Surface_Area_To_Projected_Surface_Area: Annotated[float, Field(ge=1.0, le=2.0, default=1.0)]
    """This parameter is used to help account for corrugations in the collector"""

    Roughness_Of_Collector: Annotated[Literal['VeryRough', 'Rough', 'MediumRough', 'MediumSmooth', 'Smooth', 'VerySmooth'], Field(default=...)]

    Collector_Thickness: Annotated[float, Field(ge=0.0005, le=0.007)]
    """Collector thickness is not required for Kutscher correlation"""

    Effectiveness_For_Perforations_With_Respect_To_Wind: Annotated[float, Field(gt=0, le=1.5, default=0.25)]
    """Cv"""

    Discharge_Coefficient_For_Openings_With_Respect_To_Buoyancy_Driven_Flow: Annotated[float, Field(gt=0.0, le=1.5, default=0.65)]
    """Cd"""

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