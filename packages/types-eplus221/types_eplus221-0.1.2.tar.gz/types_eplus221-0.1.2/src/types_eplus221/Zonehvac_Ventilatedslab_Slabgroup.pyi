from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Ventilatedslab_Slabgroup(EpBunch):
    """This is used to allow the coordinate control of several ventilated slab system"""

    Name: Annotated[str, Field(default=...)]

    Zone_1_Name: Annotated[str, Field(default=...)]

    Surface_1_Name: Annotated[str, Field(default=...)]

    Core_Diameter_for_Surface_1: Annotated[float, Field(default=..., ge=0.0)]

    Core_Length_for_Surface_1: Annotated[float, Field(default=..., ge=0.0)]

    Core_Numbers_for_Surface_1: Annotated[str, Field(default=...)]

    Slab_Inlet_Node_Name_for_Surface_1: Annotated[str, Field(default=...)]

    Slab_Outlet_Node_Name_for_Surface_1: Annotated[str, Field(default=...)]

    Zone_2_Name: Annotated[str, Field()]

    Surface_2_Name: Annotated[str, Field()]

    Core_Diameter_for_Surface_2: Annotated[float, Field(ge=0.0)]

    Core_Length_for_Surface_2: Annotated[float, Field(ge=0.0)]

    Core_Numbers_for_Surface_2: Annotated[str, Field()]

    Slab_Inlet_Node_Name_for_Surface_2: Annotated[str, Field()]

    Slab_Outlet_Node_Name_for_Surface_2: Annotated[str, Field()]

    Zone_3_Name: Annotated[str, Field()]

    Surface_3_Name: Annotated[str, Field()]

    Core_Diameter_for_Surface_3: Annotated[float, Field(ge=0.0)]

    Core_Length_for_Surface_3: Annotated[float, Field(ge=0.0)]

    Core_Numbers_for_Surface_3: Annotated[str, Field()]

    Slab_Inlet_Node_Name_for_Surface_3: Annotated[str, Field()]

    Slab_Outlet_Node_Name_for_Surface_3: Annotated[str, Field()]

    Zone_4_Name: Annotated[str, Field()]

    Surface_4_Name: Annotated[str, Field()]

    Core_Diameter_for_Surface_4: Annotated[float, Field(ge=0.0)]

    Core_Length_for_Surface_4: Annotated[float, Field(ge=0.0)]

    Core_Numbers_for_Surface_4: Annotated[str, Field()]

    Slab_Inlet_Node_Name_for_Surface_4: Annotated[str, Field()]

    Slab_Outlet_Node_Name_for_Surface_4: Annotated[str, Field()]

    Zone_5_Name: Annotated[str, Field()]

    Surface_5_Name: Annotated[str, Field()]

    Core_Diameter_for_Surface_5: Annotated[float, Field(ge=0.0)]

    Core_Length_for_Surface_5: Annotated[float, Field(ge=0.0)]

    Core_Numbers_for_Surface_5: Annotated[str, Field()]

    Slab_Inlet_Node_Name_for_Surface_5: Annotated[str, Field()]

    Slab_Outlet_Node_Name_for_Surface_5: Annotated[str, Field()]

    Zone_6_Name: Annotated[str, Field()]

    Surface_6_Name: Annotated[str, Field()]

    Core_Diameter_for_Surface_6: Annotated[float, Field(ge=0.0)]

    Core_Length_for_Surface_6: Annotated[float, Field(ge=0.0)]

    Core_Numbers_for_Surface_6: Annotated[str, Field()]

    Slab_Inlet_Node_Name_for_Surface_6: Annotated[str, Field()]

    Slab_Outlet_Node_Name_for_Surface_6: Annotated[str, Field()]

    Zone_7_Name: Annotated[str, Field()]

    Surface_7_Name: Annotated[str, Field()]

    Core_Diameter_for_Surface_7: Annotated[float, Field(ge=0.0)]

    Core_Length_for_Surface_7: Annotated[float, Field(ge=0.0)]

    Core_Numbers_for_Surface_7: Annotated[str, Field()]

    Slab_Inlet_Node_Name_for_Surface_7: Annotated[str, Field()]

    Slab_Outlet_Node_Name_for_Surface_7: Annotated[str, Field()]

    Zone_8_Name: Annotated[str, Field()]

    Surface_8_Name: Annotated[str, Field()]

    Core_Diameter_for_Surface_8: Annotated[float, Field(ge=0.0)]

    Core_Length_for_Surface_8: Annotated[float, Field(ge=0.0)]

    Core_Numbers_for_Surface_8: Annotated[str, Field()]

    Slab_Inlet_Node_Name_for_Surface_8: Annotated[str, Field()]

    Slab_Outlet_Node_Name_for_Surface_8: Annotated[str, Field()]

    Zone_9_Name: Annotated[str, Field()]

    Surface_9_Name: Annotated[str, Field()]

    Core_Diameter_for_Surface_9: Annotated[float, Field(ge=0.0)]

    Core_Length_for_Surface_9: Annotated[float, Field(ge=0.0)]

    Core_Numbers_for_Surface_9: Annotated[str, Field()]

    Slab_Inlet_Node_Name_for_Surface_9: Annotated[str, Field()]

    Slab_Outlet_Node_Name_for_Surface_9: Annotated[str, Field()]

    Zone_10_Name: Annotated[str, Field()]

    Surface_10_Name: Annotated[str, Field()]

    Core_Diameter_for_Surface_10: Annotated[float, Field(ge=0.0)]

    Core_Length_for_Surface_10: Annotated[float, Field(ge=0.0)]

    Core_Numbers_for_Surface_10: Annotated[str, Field()]

    Slab_Inlet_Node_Name_for_Surface_10: Annotated[str, Field()]

    Slab_Outlet_Node_Name_for_Surface_10: Annotated[str, Field()]