from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Branch(EpBunch):
    """List components on the branch in simulation and connection order"""

    Name: Annotated[str, Field(default=...)]

    Pressure_Drop_Curve_Name: Annotated[str, Field()]
    """Optional field to include this branch in plant pressure drop calculations"""

    Component_1_Object_Type: Annotated[str, Field(default=...)]

    Component_1_Name: Annotated[str, Field(default=...)]

    Component_1_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Component_1_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Component_2_Object_Type: Annotated[str, Field()]

    Component_2_Name: Annotated[str, Field()]

    Component_2_Inlet_Node_Name: Annotated[str, Field()]

    Component_2_Outlet_Node_Name: Annotated[str, Field()]

    Component_3_Object_Type: Annotated[str, Field()]

    Component_3_Name: Annotated[str, Field()]

    Component_3_Inlet_Node_Name: Annotated[str, Field()]

    Component_3_Outlet_Node_Name: Annotated[str, Field()]

    Component_4_Object_Type: Annotated[str, Field()]

    Component_4_Name: Annotated[str, Field()]

    Component_4_Inlet_Node_Name: Annotated[str, Field()]

    Component_4_Outlet_Node_Name: Annotated[str, Field()]

    Component_5_Object_Type: Annotated[str, Field()]

    Component_5_Name: Annotated[str, Field()]

    Component_5_Inlet_Node_Name: Annotated[str, Field()]

    Component_5_Outlet_Node_Name: Annotated[str, Field()]

    Component_6_Object_Type: Annotated[str, Field()]

    Component_6_Name: Annotated[str, Field()]

    Component_6_Inlet_Node_Name: Annotated[str, Field()]

    Component_6_Outlet_Node_Name: Annotated[str, Field()]

    Component_7_Object_Type: Annotated[str, Field()]

    Component_7_Name: Annotated[str, Field()]

    Component_7_Inlet_Node_Name: Annotated[str, Field()]

    Component_7_Outlet_Node_Name: Annotated[str, Field()]

    Component_8_Object_Type: Annotated[str, Field()]

    Component_8_Name: Annotated[str, Field()]

    Component_8_Inlet_Node_Name: Annotated[str, Field()]

    Component_8_Outlet_Node_Name: Annotated[str, Field()]

    Component_9_Object_Type: Annotated[str, Field()]

    Component_9_Name: Annotated[str, Field()]

    Component_9_Inlet_Node_Name: Annotated[str, Field()]

    Component_9_Outlet_Node_Name: Annotated[str, Field()]

    Component_10_Object_Type: Annotated[str, Field()]

    Component_10_Name: Annotated[str, Field()]

    Component_10_Inlet_Node_Name: Annotated[str, Field()]

    Component_10_Outlet_Node_Name: Annotated[str, Field()]

    Component_11_Object_Type: Annotated[str, Field()]

    Component_11_Name: Annotated[str, Field()]

    Component_11_Inlet_Node_Name: Annotated[str, Field()]

    Component_11_Outlet_Node_Name: Annotated[str, Field()]