from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Componentcost_Lineitem(EpBunch):
    """Each instance of this object creates a cost line item and will contribute to the total"""

    Name: Annotated[str, Field()]

    Type: Annotated[str, Field()]

    Line_Item_Type: Annotated[Literal['General', 'Construction', 'Coil:DX', 'Coil:Cooling:DX:SingleSpeed', 'Coil:Heating:Fuel', 'Chiller:Electric', 'Daylighting:Controls', 'Shading:Zone:Detailed', 'Lights', 'Generator:Photovoltaic'], Field(default=...)]
    """extend choice-keys as Cases are added to code"""

    Item_Name: Annotated[str, Field(default=...)]
    """wildcard "*" is acceptable for some components"""

    Object_End_Use_Key: Annotated[str, Field()]
    """not yet used"""

    Cost_Per_Each: Annotated[float, Field()]

    Cost_Per_Area: Annotated[float, Field()]

    Cost_Per_Unit_Of_Output_Capacity: Annotated[float, Field()]

    Cost_Per_Unit_Of_Output_Capacity_Per_Cop: Annotated[float, Field()]
    """The value is per change in COP."""

    Cost_Per_Volume: Annotated[float, Field()]

    Cost_Per_Volume_Rate: Annotated[float, Field()]

    Cost_Per_Energy_Per_Temperature_Difference: Annotated[float, Field()]
    """as in for use with UA sizing of Coils"""

    Quantity: Annotated[float, Field()]
    """optional for use with Cost per Each and "General" object Type"""