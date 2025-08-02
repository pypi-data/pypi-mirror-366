from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Thermalstorage_Ice_Detailed(EpBunch):
    """This input syntax is intended to describe a thermal storage system that"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Capacity: Annotated[str, Field(default=...)]
    """This includes only the latent storage capacity"""

    Inlet_Node_Name: Annotated[str, Field(default=...)]

    Outlet_Node_Name: Annotated[str, Field(default=...)]

    Discharging_Curve_Variable_Specifications: Annotated[Literal['FractionChargedLMTD', 'FractionDischargedLMTD', 'LMTDMassFlow', 'LMTDFractionCharged'], Field(default=...)]

    Discharging_Curve_Name: Annotated[str, Field(default=...)]

    Charging_Curve_Variable_Specifications: Annotated[Literal['FractionChargedLMTD', 'FractionDischargedLMTD', 'LMTDMassFlow', 'LMTDFractionCharged'], Field(default=...)]

    Charging_Curve_Name: Annotated[str, Field(default=...)]

    Timestep_Of_The_Curve_Data: Annotated[str, Field()]

    Parasitic_Electric_Load_During_Discharging: Annotated[str, Field()]

    Parasitic_Electric_Load_During_Charging: Annotated[str, Field()]

    Tank_Loss_Coefficient: Annotated[str, Field()]
    """This is the fraction the total storage capacity that is lost or melts"""

    Freezing_Temperature_Of_Storage_Medium: Annotated[str, Field(default='0.0')]
    """This temperature is typically 0C for water."""

    Thaw_Process_Indicator: Annotated[Literal['InsideMelt', 'OutsideMelt'], Field(default='OutsideMelt')]
    """This field determines whether the system uses internal or external melt"""