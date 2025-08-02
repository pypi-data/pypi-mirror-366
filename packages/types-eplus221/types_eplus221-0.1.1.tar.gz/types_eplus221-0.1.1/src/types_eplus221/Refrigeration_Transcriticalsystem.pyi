from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Refrigeration_Transcriticalsystem(EpBunch):
    """Detailed transcritical carbon dioxide (CO2) booster refrigeration systems used in"""

    Name: Annotated[str, Field(default=...)]

    System_Type: Annotated[Literal['SingleStage', 'TwoStage'], Field(default=...)]

    Medium_Temperature_Refrigerated_Case_Or_Walkin_Or_Caseandwalkinlist_Name: Annotated[str, Field(default=...)]
    """Enter the name of a Refrigeration:Case or Refrigeration:WalkIn object."""

    Low_Temperature_Refrigerated_Case_Or_Walkin_Or_Caseandwalkinlist_Name: Annotated[str, Field()]
    """Enter the name of a Refrigeration:Case or Refrigeration:WalkIn object."""

    Refrigeration_Gas_Cooler_Name: Annotated[str, Field(default=...)]

    High_Pressure_Compressor_Or_Compressorlist_Name: Annotated[str, Field(default=...)]

    Low_Pressure_Compressor_Or_Compressorlist_Name: Annotated[str, Field()]

    Receiver_Pressure: Annotated[float, Field(default=4000000)]

    Subcooler_Effectiveness: Annotated[float, Field(default=0.4)]

    Refrigeration_System_Working_Fluid_Type: Annotated[str, Field(default=...)]
    """Fluid property data for the refrigerant must be entered."""

    Sum_Ua_Suction_Piping_For_Medium_Temperature_Loads: Annotated[float, Field(default=0.0)]
    """Use only if you want to include suction piping heat gain in refrigeration load"""

    Medium_Temperature_Suction_Piping_Zone_Name: Annotated[str, Field()]
    """This will be used to determine the temperature used for distribution piping heat"""

    Sum_Ua_Suction_Piping_For_Low_Temperature_Loads: Annotated[float, Field(default=0.0)]
    """Use only if you want to include suction piping heat gain in refrigeration load"""

    Low_Temperature_Suction_Piping_Zone_Name: Annotated[str, Field()]
    """This will be used to determine the temperature used for distribution piping heat"""

    End_Use_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""