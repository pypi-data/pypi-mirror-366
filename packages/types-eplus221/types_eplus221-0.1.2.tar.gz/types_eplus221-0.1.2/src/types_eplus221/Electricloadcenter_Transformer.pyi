from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Electricloadcenter_Transformer(EpBunch):
    """a list of meters that can be reported are available after a run on"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Transformer_Usage: Annotated[Literal['PowerInFromGrid', 'PowerOutToGrid', 'LoadCenterPowerConditioning'], Field(default='PowerInFromGrid')]
    """A transformer can be used to transfer electric energy from utility grid to"""

    Zone_Name: Annotated[str, Field()]
    """Enter name of zone to receive transformer losses as heat"""

    Radiative_Fraction: Annotated[float, Field(ge=0, le=1.0, default=0)]

    Rated_Capacity: Annotated[float, Field(ge=0)]
    """the unit is VA, instead of kVA as usually shown on transformer nameplates."""

    Phase: Annotated[Literal['1', '3'], Field(default='3')]
    """Must be single or three phase transformer."""

    Conductor_Material: Annotated[Literal['Copper', 'Aluminum'], Field(default='Aluminum')]
    """Winding material used by the transformer."""

    Full_Load_Temperature_Rise: Annotated[float, Field(ge=50, le=180, default=150)]

    Fraction_of_Eddy_Current_Losses: Annotated[float, Field(ge=0, le=1.0, default=0.1)]

    Performance_Input_Method: Annotated[Literal['RatedLosses', 'NominalEfficiency'], Field(default='RatedLosses')]
    """User can define transformer performance by specifying"""

    Rated_No_Load_Loss: Annotated[float, Field(gt=0)]
    """Only required when RatedLosses is the performance input method"""

    Rated_Load_Loss: Annotated[float, Field(ge=0)]
    """Only required when RatedLosses is the performance input method"""

    Nameplate_Efficiency: Annotated[float, Field(gt=0, le=1.0, default=0.98)]
    """Only required when NominalEfficiency is the performance input method"""

    Per_Unit_Load_for_Nameplate_Efficiency: Annotated[float, Field(gt=0, le=1.0, default=0.35)]
    """Percentage of the rated capacity at which the nameplate efficiency is defined"""

    Reference_Temperature_for_Nameplate_Efficiency: Annotated[float, Field(ge=20, le=150, default=75)]
    """Conductor operating temperature at which the nameplate efficiency is defined"""

    Per_Unit_Load_for_Maximum_Efficiency: Annotated[float, Field(gt=0, le=1.0)]
    """Percentage of the rate capacity at which the maximum efficiency is obtained"""

    Consider_Transformer_Loss_for_Utility_Cost: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """Only required when the transformer is used for power in from the utility grid"""

    Meter_1_Name: Annotated[str, Field()]
    """Must be an electric meter (with electricity as the resource type)"""

    Meter_2_Name: Annotated[str, Field()]
    """Must be an electric meter (with electricity as the resource type)"""

    Meter_3_Name: Annotated[str, Field()]
    """Must be an electric meter (with electricity as the resource type)"""

    Meter_4_Name: Annotated[str, Field()]
    """Must be an electric meter (with electricity as the resource type)"""

    Meter_5_Name: Annotated[str, Field()]
    """Must be an electric meter (with electricity as the resource type)"""

    Meter_6_Name: Annotated[str, Field()]
    """Must be an electric meter (with electricity as the resource type)"""

    Meter_7_Name: Annotated[str, Field()]
    """Must be an electric meter (with electricity as the resource type)"""

    Meter_8_Name: Annotated[str, Field()]
    """Must be an electric meter (with electricity as the resource type)"""

    Meter_9_Name: Annotated[str, Field()]
    """Must be an electric meter (with electricity as the resource type)"""

    Meter_10_Name: Annotated[str, Field()]
    """Must be an electric meter (with electricity as the resource type)"""