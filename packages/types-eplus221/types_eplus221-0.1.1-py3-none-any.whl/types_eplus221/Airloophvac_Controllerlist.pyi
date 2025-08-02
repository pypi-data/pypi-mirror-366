from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac_Controllerlist(EpBunch):
    """List controllers in order of control sequence"""

    Name: Annotated[str, Field(default=...)]

    Controller_1_Object_Type: Annotated[Literal['Controller:WaterCoil', 'Controller:OutdoorAir'], Field(default=...)]

    Controller_1_Name: Annotated[str, Field(default=...)]

    Controller_2_Object_Type: Annotated[Literal['Controller:WaterCoil', 'Controller:OutdoorAir'], Field()]

    Controller_2_Name: Annotated[str, Field()]

    Controller_3_Object_Type: Annotated[Literal['Controller:WaterCoil', 'Controller:OutdoorAir'], Field()]

    Controller_3_Name: Annotated[str, Field()]

    Controller_4_Object_Type: Annotated[Literal['Controller:WaterCoil', 'Controller:OutdoorAir'], Field()]

    Controller_4_Name: Annotated[str, Field()]

    Controller_5_Object_Type: Annotated[Literal['Controller:WaterCoil', 'Controller:OutdoorAir'], Field()]

    Controller_5_Name: Annotated[str, Field()]

    Controller_6_Object_Type: Annotated[Literal['Controller:WaterCoil', 'Controller:OutdoorAir'], Field()]

    Controller_6_Name: Annotated[str, Field()]

    Controller_7_Object_Type: Annotated[Literal['Controller:WaterCoil', 'Controller:OutdoorAir'], Field()]

    Controller_7_Name: Annotated[str, Field()]

    Controller_8_Object_Type: Annotated[Literal['Controller:WaterCoil', 'Controller:OutdoorAir'], Field()]

    Controller_8_Name: Annotated[str, Field()]