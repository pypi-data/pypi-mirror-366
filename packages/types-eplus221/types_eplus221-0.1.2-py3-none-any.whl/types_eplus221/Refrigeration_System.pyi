from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Refrigeration_System(EpBunch):
    """Simulates the performance of a supermarket refrigeration system when used along with"""

    Name: Annotated[str, Field(default=...)]

    Refrigerated_Case_or_Walkin_or_CaseAndWalkInList_Name: Annotated[str, Field()]
    """Enter the name of a Refrigeration:Case or Refrigeration:WalkIn object."""

    Refrigeration_Transfer_Load_or_TransferLoad_List_Name: Annotated[str, Field()]
    """Enter the name of a Refrigeration:SecondarySystem object OR"""

    Refrigeration_Condenser_Name: Annotated[str, Field(default=...)]

    Compressor_or_CompressorList_Name: Annotated[str, Field(default=...)]

    Minimum_Condensing_Temperature: Annotated[float, Field(default=...)]
    """related to the proper operation of the thermal expansion"""

    Refrigeration_System_Working_Fluid_Type: Annotated[str, Field(default=...)]
    """Fluid property data for the refrigerant must be entered."""

    Suction_Temperature_Control_Type: Annotated[Literal['FloatSuctionTemperature', 'ConstantSuctionTemperature'], Field(default='ConstantSuctionTemperature')]

    Mechanical_Subcooler_Name: Annotated[str, Field()]
    """Optional Field"""

    Liquid_Suction_Heat_Exchanger_Subcooler_Name: Annotated[str, Field()]
    """Optional Field"""

    Sum_UA_Suction_Piping: Annotated[float, Field(default=0.0)]
    """Use only if you want to include suction piping heat gain in refrigeration load"""

    Suction_Piping_Zone_Name: Annotated[str, Field()]
    """This will be used to determine the temperature used for distribution piping heat gain"""

    EndUse_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""

    Number_of_Compressor_Stages: Annotated[Literal['1', '2'], Field(default='1')]

    Intercooler_Type: Annotated[Literal['None', 'Flash Intercooler', 'Shell-and-Coil Intercooler'], Field()]

    ShellandCoil_Intercooler_Effectiveness: Annotated[float, Field(default=0.8)]

    HighStage_Compressor_or_CompressorList_Name: Annotated[str, Field()]