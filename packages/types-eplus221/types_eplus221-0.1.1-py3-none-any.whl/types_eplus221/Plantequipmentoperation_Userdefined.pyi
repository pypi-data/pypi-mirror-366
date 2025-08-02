from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Plantequipmentoperation_Userdefined(EpBunch):
    """Defines a generic plant operation scheme for custom supervisory control"""

    Name: Annotated[str, Field(default=...)]
    """This is the name of the plant operation scheme"""

    Main_Model_Program_Calling_Manager_Name: Annotated[str, Field(default=...)]

    Initialization_Program_Calling_Manager_Name: Annotated[str, Field()]

    Equipment_1_Object_Type: Annotated[str, Field()]

    Equipment_1_Name: Annotated[str, Field()]

    Equipment_2_Object_Type: Annotated[str, Field()]

    Equipment_2_Name: Annotated[str, Field()]

    Equipment_3_Object_Type: Annotated[str, Field()]

    Equipment_3_Name: Annotated[str, Field()]

    Equipment_4_Object_Type: Annotated[str, Field()]

    Equipment_4_Name: Annotated[str, Field()]

    Equipment_5_Object_Type: Annotated[str, Field()]

    Equipment_5_Name: Annotated[str, Field()]

    Equipment_6_Object_Type: Annotated[str, Field()]

    Equipment_6_Name: Annotated[str, Field()]

    Equipment_7_Object_Type: Annotated[str, Field()]

    Equipment_7_Name: Annotated[str, Field()]

    Equipment_8_Object_Type: Annotated[str, Field()]

    Equipment_8_Name: Annotated[str, Field()]

    Equipment_9_Object_Type: Annotated[str, Field()]

    Equipment_9_Name: Annotated[str, Field()]

    Equipment_10_Object_Type: Annotated[str, Field()]

    Equipment_10_Name: Annotated[str, Field()]