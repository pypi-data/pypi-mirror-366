from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roomair_Node_Airflownetwork(EpBunch):
    """define an air node for some types of nodal air models"""

    Name: Annotated[str, Field()]

    Zone_Name: Annotated[str, Field(default=...)]

    Fraction_Of_Zone_Air_Volume: Annotated[float, Field(ge=0.0, le=1.0)]

    Roomair_Node_Airflownetwork_Adjacentsurfacelist_Name: Annotated[str, Field()]

    Roomair_Node_Airflownetwork_Internalgains_Name: Annotated[str, Field()]

    Roomair_Node_Airflownetwork_Hvacequipment_Name: Annotated[str, Field()]