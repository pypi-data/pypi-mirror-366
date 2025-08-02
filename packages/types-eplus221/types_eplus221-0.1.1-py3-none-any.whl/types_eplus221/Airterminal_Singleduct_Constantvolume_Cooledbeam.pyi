from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airterminal_Singleduct_Constantvolume_Cooledbeam(EpBunch):
    """Central air system terminal unit, single duct, constant volume, with cooled beam"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Cooled_Beam_Type: Annotated[Literal['Active', 'Passive'], Field(default=...)]

    Supply_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Supply_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Chilled_Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Chilled_Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Supply_Air_Volumetric_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]

    Maximum_Total_Chilled_Water_Volumetric_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]

    Number_Of_Beams: Annotated[int, Field(gt=0, default=autosize)]
    """Number of individual beam units in the zone"""

    Beam_Length: Annotated[float, Field(gt=0.0, default=autosize)]
    """Length of an individual beam unit"""

    Design_Inlet_Water_Temperature: Annotated[float, Field(ge=0.0, default=15.0)]

    Design_Outlet_Water_Temperature: Annotated[float, Field(ge=0.0, default=17.0)]

    Coil_Surface_Area_Per_Coil_Length: Annotated[float, Field(ge=0.0, default=5.422)]

    Model_Parameter_A: Annotated[float, Field(ge=0.0, default=15.3)]

    Model_Parameter_N1: Annotated[float, Field(ge=0.0, default=0.0)]

    Model_Parameter_N2: Annotated[float, Field(ge=0.0, default=0.84)]

    Model_Parameter_N3: Annotated[float, Field(ge=0.0, default=0.12)]

    Model_Parameter_A0: Annotated[float, Field(ge=0.0, default=0.171)]
    """Free area of the coil in plan view per unit beam length"""

    Model_Parameter_K1: Annotated[float, Field(ge=0.0, default=0.0057)]

    Model_Parameter_N: Annotated[float, Field(ge=0.0, default=0.4)]

    Coefficient_Of_Induction_Kin: Annotated[float, Field(ge=0.0, le=4.0, default=Autocalculate)]

    Leaving_Pipe_Inside_Diameter: Annotated[float, Field(gt=0.0, default=0.0145)]