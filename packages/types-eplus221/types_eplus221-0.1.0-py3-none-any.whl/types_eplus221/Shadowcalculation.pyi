from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Shadowcalculation(EpBunch):
    """This object is used to control details of the solar, shading, and daylighting models"""

    Calculation_Method: Annotated[Literal['AverageOverDaysInFrequency', 'TimestepFrequency'], Field(default='AverageOverDaysInFrequency')]
    """choose calculation method. note that TimestepFrequency is only needed for certain cases"""

    Calculation_Frequency: Annotated[int, Field(ge=1, default=20)]
    """enter number of days"""

    Maximum_Figures_In_Shadow_Overlap_Calculations: Annotated[int, Field(ge=200, default=15000)]
    """Number of allowable figures in shadow overlap calculations"""

    Polygon_Clipping_Algorithm: Annotated[Literal['ConvexWeilerAtherton', 'SutherlandHodgman'], Field(default='SutherlandHodgman')]
    """Advanced Feature. Internal default is SutherlandHodgman"""

    Sky_Diffuse_Modeling_Algorithm: Annotated[Literal['SimpleSkyDiffuseModeling', 'DetailedSkyDiffuseModeling'], Field(default='SimpleSkyDiffuseModeling')]
    """Advanced Feature. Internal default is SimpleSkyDiffuseModeling"""

    External_Shading_Calculation_Method: Annotated[Literal['ScheduledShading', 'InternalCalculation', 'ImportedShading'], Field(default='InternalCalculation')]
    """If ScheduledShading is chosen, the External Shading Fraction Schedule Name is required"""

    Output_External_Shading_Calculation_Results: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """If Yes is chosen, the calculated external shading fraction results will be saved to an external CSV file with surface names as the column headers."""

    Disable_Self_Shading_Within_Shading_Zone_Groups: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """If Yes, self-shading will be disabled from all exterior surfaces in a given Shading Zone Group to surfaces within"""

    Disable_Self_Shading_From_Shading_Zone_Groups_To_Other_Zones: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """If Yes, self-shading will be disabled from all exterior surfaces in a given Shading Zone Group to all other zones in the model."""

    Shading_Zone_Group_1_Zonelist_Name: Annotated[str, Field()]
    """Specifies a group of zones which are controlled by the Disable Self-Shading fields."""

    Shading_Zone_Group_2_Zonelist_Name: Annotated[str, Field()]

    Shading_Zone_Group_3_Zonelist_Name: Annotated[str, Field()]

    Shading_Zone_Group_4_Zonelist_Name: Annotated[str, Field()]

    Shading_Zone_Group_5_Zonelist_Name: Annotated[str, Field()]

    Shading_Zone_Group_6_Zonelist_Name: Annotated[str, Field()]