from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Refrigeration_Transferloadlist(EpBunch):
    """A refrigeration system may provide cooling to other, secondary, systems through"""

    Name: Annotated[str, Field(default=...)]

    Cascade_Condenser_Name_or_Secondary_System_1_Name: Annotated[str, Field(default=...)]
    """Enter the name of a Refrigeration:Condenser:Cascade object OR"""

    Cascade_Condenser_Name_or_Secondary_System_2_Name: Annotated[str, Field()]
    """Enter the name of a Refrigeration:Condenser:Cascade object OR"""

    Cascade_Condenser_Name_or_Secondary_System_3_Name: Annotated[str, Field()]
    """Enter the name of a Refrigeration:Condenser:Cascade object OR"""

    Cascade_Condenser_Name_or_Secondary_System_4_Name: Annotated[str, Field()]
    """Enter the name of a Refrigeration:Condenser:Cascade object OR"""

    Cascade_Condenser_Name_or_Secondary_System_5_Name: Annotated[str, Field()]
    """Enter the name of a Refrigeration:Condenser:Cascade object OR"""

    Cascade_Condenser_Name_or_Secondary_System_6_Name: Annotated[str, Field()]
    """Enter the name of a Refrigeration:Condenser:Cascade object OR"""

    Cascade_Condenser_Name_or_Secondary_System_7_Name: Annotated[str, Field()]
    """Enter the name of a Refrigeration:Condenser:Cascade object OR"""

    Cascade_Condenser_Name_or_Secondary_System_8_Name: Annotated[str, Field()]
    """Enter the name of a Refrigeration:Condenser:Cascade object OR"""

    Cascade_Condenser_Name_or_Secondary_System_9_Name: Annotated[str, Field()]
    """Enter the name of a Refrigeration:Condenser:Cascade object OR"""