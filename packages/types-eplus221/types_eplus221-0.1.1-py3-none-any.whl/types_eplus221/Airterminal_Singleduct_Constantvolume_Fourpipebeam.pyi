from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airterminal_Singleduct_Constantvolume_Fourpipebeam(EpBunch):
    """Central air system terminal unit, single duct, constant volume,"""

    Name: Annotated[str, Field(default=...)]

    Primary_Air_Availability_Schedule_Name: Annotated[str, Field()]
    """Primary air is supplied by central air handling unit and must be on for heating or cooling."""

    Cooling_Availability_Schedule_Name: Annotated[str, Field()]
    """Cooling operation can be controlled separately using this availability schedule."""

    Heating_Availability_Schedule_Name: Annotated[str, Field()]
    """Heating operation can be controlled separately using this availability schedule."""

    Primary_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Name of the air system node for primary supply air entering the air distribution unit."""

    Primary_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """Name of the air system node for primary supply air leaving the air distribution unit and entering the zone."""

    Chilled_Water_Inlet_Node_Name: Annotated[str, Field()]
    """Name of the plant system node for chilled water entering the beam."""

    Chilled_Water_Outlet_Node_Name: Annotated[str, Field()]
    """Name of the plant system node for chilled water leaving the beam."""

    Hot_Water_Inlet_Node_Name: Annotated[str, Field()]
    """Name of the plant system node for hot water entering the beam."""

    Hot_Water_Outlet_Node_Name: Annotated[str, Field()]
    """Name of the plant system node for hot water leaving the beam."""

    Design_Primary_Air_Volume_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]

    Design_Chilled_Water_Volume_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]

    Design_Hot_Water_Volume_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]

    Zone_Total_Beam_Length: Annotated[float, Field(gt=0.0, default=autosize)]
    """Sum of the length of all the beam units in the zone represented by this terminal unit."""

    Rated_Primary_Air_Flow_Rate_Per_Beam_Length: Annotated[float, Field(gt=0.0, default=0.035)]
    """Primary air supply flow rate normalized by beam length."""

    Beam_Rated_Cooling_Capacity_Per_Beam_Length: Annotated[float, Field(gt=0.0, default=600.0)]
    """Sensible cooling capacity per meter of beam length at the rating point."""

    Beam_Rated_Cooling_Room_Air_Chilled_Water_Temperature_Difference: Annotated[float, Field(gt=0.0, default=10.0)]
    """Difference in temperature between the zone air and the entering chilled water at the rating point."""

    Beam_Rated_Chilled_Water_Volume_Flow_Rate_Per_Beam_Length: Annotated[float, Field(gt=0.0, default=0.00005)]
    """The volume flow rate of chilled water per meter of beam length at the rating point."""

    Beam_Cooling_Capacity_Temperature_Difference_Modification_Factor_Curve_Name: Annotated[str, Field()]
    """Adjusts beam cooling capacity when the temperature difference between entering water and zone air"""

    Beam_Cooling_Capacity_Air_Flow_Modification_Factor_Curve_Name: Annotated[str, Field()]
    """Adjusts beam cooling capacity when the primary air supply flow rate is different"""

    Beam_Cooling_Capacity_Chilled_Water_Flow_Modification_Factor_Curve_Name: Annotated[str, Field()]
    """Adjusts beam cooling capacity when the normalized chilled water flow rate is different"""

    Beam_Rated_Heating_Capacity_Per_Beam_Length: Annotated[float, Field(gt=0.0, default=1500.0)]
    """Sensible heating capacity per meter of beam length at the rating point."""

    Beam_Rated_Heating_Room_Air_Hot_Water_Temperature_Difference: Annotated[float, Field(gt=0.0, default=27.8)]
    """Difference in temperature between the zone air and the entering hot water at the rating point."""

    Beam_Rated_Hot_Water_Volume_Flow_Rate_Per_Beam_Length: Annotated[float, Field(gt=0.0, default=0.00005)]
    """The volume flow rate of hoy water per meter of beam length at the rating point."""

    Beam_Heating_Capacity_Temperature_Difference_Modification_Factor_Curve_Name: Annotated[str, Field()]
    """Adjusts beam heating capacity when the temperature difference between entering water and zone air"""

    Beam_Heating_Capacity_Air_Flow_Modification_Factor_Curve_Name: Annotated[str, Field()]
    """Adjusts beam heating capacity when the primary air supply flow rate is different"""

    Beam_Heating_Capacity_Hot_Water_Flow_Modification_Factor_Curve_Name: Annotated[str, Field()]
    """Adjusts beam heating capacity when the normalized hot water flow rate is different"""