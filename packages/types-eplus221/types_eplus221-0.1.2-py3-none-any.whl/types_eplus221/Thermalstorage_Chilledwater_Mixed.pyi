from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Thermalstorage_Chilledwater_Mixed(EpBunch):
    """Chilled water storage with a well-mixed, single-node tank. The chilled water is"""

    Name: Annotated[str, Field(default=...)]

    Tank_Volume: Annotated[float, Field(gt=0.0, default=0.1)]

    Setpoint_Temperature_Schedule_Name: Annotated[str, Field()]

    Deadband_Temperature_Difference: Annotated[float, Field(gt=0.0, default=0.5)]

    Minimum_Temperature_Limit: Annotated[float, Field()]

    Nominal_Cooling_Capacity: Annotated[float, Field()]

    Ambient_Temperature_Indicator: Annotated[Literal['Schedule', 'Zone', 'Outdoors'], Field(default=...)]

    Ambient_Temperature_Schedule_Name: Annotated[str, Field()]

    Ambient_Temperature_Zone_Name: Annotated[str, Field()]

    Ambient_Temperature_Outdoor_Air_Node_Name: Annotated[str, Field()]
    """required when field Ambient Temperature Indicator=Outdoors"""

    Heat_Gain_Coefficient_from_Ambient_Temperature: Annotated[float, Field(ge=0.0)]

    Use_Side_Inlet_Node_Name: Annotated[str, Field()]

    Use_Side_Outlet_Node_Name: Annotated[str, Field()]

    Use_Side_Heat_Transfer_Effectiveness: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Use_Side_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for use side. Schedule value > 0 means the system is available."""

    Use_Side_Design_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]

    Source_Side_Inlet_Node_Name: Annotated[str, Field()]

    Source_Side_Outlet_Node_Name: Annotated[str, Field()]

    Source_Side_Heat_Transfer_Effectiveness: Annotated[float, Field(gt=0.0, le=1.0, default=1.0)]

    Source_Side_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for source side. Schedule value > 0 means the system is available."""

    Source_Side_Design_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]

    Tank_Recovery_Time: Annotated[float, Field(gt=0.0, default=4.0)]
    """Parameter for autosizing design flow rates for indirectly cooled water tanks"""