from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceproperty_Surroundingsurfaces(EpBunch):
    """This object defines a list of surrounding surfaces for an exterior surface."""

    Name: Annotated[str, Field(default=...)]

    Sky_View_Factor: Annotated[str, Field(default='0.5')]
    """optional"""

    Sky_Temperature_Schedule_Name: Annotated[str, Field()]
    """Schedule values are real numbers, -100.0 to 100.0, units C"""

    Ground_View_Factor: Annotated[str, Field(default='0.5')]
    """optional"""

    Ground_Temperature_Schedule_Name: Annotated[str, Field()]
    """Schedule values are real numbers, -100.0 to 100.0, units C"""

    Surrounding_Surface_1_Name: Annotated[str, Field(default=...)]

    Surrounding_Surface_1_View_Factor: Annotated[str, Field(default='0.0')]

    Surrounding_Surface_1_Temperature_Schedule_Name: Annotated[str, Field(default=...)]
    """Schedule values are real numbers, -100.0 to 100.0, units C"""

    Surrounding_Surface_2_Name: Annotated[str, Field()]

    Surrounding_Surface_2_View_Factor: Annotated[str, Field(default='0.0')]

    Surrounding_Surface_2_Temperature_Schedule_Name: Annotated[str, Field()]
    """Schedule values are real numbers, -100.0 to 100.0, units C"""

    Surrounding_Surface_3_Name: Annotated[str, Field()]

    Surrounding_Surface_3_View_Factor: Annotated[str, Field(default='0.0')]

    Surrounding_Surface_3_Temperature_Schedule_Name: Annotated[str, Field()]
    """Schedule values are real numbers, -100.0 to 100.0, units C"""

    Surrounding_Surface_4_Name: Annotated[str, Field()]

    Surrounding_Surface_4_View_Factor: Annotated[str, Field(default='0.0')]

    Surrounding_Surface_4_Temperature_Schedule_Name: Annotated[str, Field()]
    """Schedule values are real numbers, -100.0 to 100.0, units C"""

    Surrounding_Surface_5_Name: Annotated[str, Field()]

    Surrounding_Surface_5_View_Factor: Annotated[str, Field(default='0.0')]

    Surrounding_Surface_5_Temperature_Schedule_Name: Annotated[str, Field()]
    """Schedule values are real numbers, -100.0 to 100.0, units C"""

    Surrounding_Surface_6_Name: Annotated[str, Field()]

    Surrounding_Surface_6_View_Factor: Annotated[str, Field(default='0.0')]

    Surrounding_Surface_6_Temperature_Schedule_Name: Annotated[str, Field()]
    """Schedule values are real numbers, -100.0 to 100.0, units C"""

    Surrounding_Surface_7_Name: Annotated[str, Field()]

    Surrounding_Surface_7_View_Factor: Annotated[str, Field(default='0.0')]

    Surrounding_Surface_7_Temperature_Schedule_Name: Annotated[str, Field()]
    """Schedule values are real numbers, -100.0 to 100.0, units C"""

    Surrounding_Surface_8_Name: Annotated[str, Field()]

    Surrounding_Surface_8_View_Factor: Annotated[str, Field(default='0.0')]

    Surrounding_Surface_8_Temperature_Schedule_Name: Annotated[str, Field()]
    """Schedule values are real numbers, -100.0 to 100.0, units C"""

    Surrounding_Surface_9_Name: Annotated[str, Field()]

    Surrounding_Surface_9_View_Factor: Annotated[str, Field(default='0.0')]

    Surrounding_Surface_9_Temperature_Schedule_Name: Annotated[str, Field()]
    """Schedule values are real numbers, -100.0 to 100.0, units C"""

    Surrounding_Surface_10_Name: Annotated[str, Field()]

    Surrounding_Surface_10_View_Factor: Annotated[str, Field(default='0.0')]

    Surrounding_Surface_10_Temperature_Schedule_Name: Annotated[str, Field()]
    """Schedule values are real numbers, -100.0 to 100.0, units C"""