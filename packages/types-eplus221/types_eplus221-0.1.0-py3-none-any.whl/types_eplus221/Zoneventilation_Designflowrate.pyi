from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zoneventilation_Designflowrate(EpBunch):
    """Ventilation is specified as a design level which is modified by a schedule fraction, temperature difference and wind speed:"""

    Name: Annotated[str, Field(default=...)]

    Zone_Or_Zonelist_Name: Annotated[str, Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]

    Design_Flow_Rate_Calculation_Method: Annotated[Literal['Flow/Zone', 'Flow/Area', 'Flow/Person', 'AirChanges/Hour'], Field(default='Flow/Zone')]
    """The entered calculation method is used to create the maximum amount of ventilation"""

    Design_Flow_Rate: Annotated[float, Field(ge=0)]

    Flow_Rate_Per_Zone_Floor_Area: Annotated[float, Field(ge=0)]

    Flow_Rate_Per_Person: Annotated[float, Field(ge=0)]

    Air_Changes_Per_Hour: Annotated[float, Field(ge=0)]

    Ventilation_Type: Annotated[Literal['Natural', 'Intake', 'Exhaust', 'Balanced'], Field(default='Natural')]

    Fan_Pressure_Rise: Annotated[float, Field(ge=0, default=0)]
    """pressure rise across the fan"""

    Fan_Total_Efficiency: Annotated[float, Field(gt=0, default=1)]

    Constant_Term_Coefficient: Annotated[float, Field(default=1)]
    """"A" in Equation"""

    Temperature_Term_Coefficient: Annotated[float, Field(default=0)]
    """"B" in Equation"""

    Velocity_Term_Coefficient: Annotated[float, Field(default=0)]
    """"C" in Equation"""

    Velocity_Squared_Term_Coefficient: Annotated[float, Field(default=0)]
    """"D" in Equation"""

    Minimum_Indoor_Temperature: Annotated[float, Field(ge=-100, le=100, default=-100)]
    """this is the indoor temperature below which ventilation is shutoff"""

    Minimum_Indoor_Temperature_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the indoor temperature versus time below which"""

    Maximum_Indoor_Temperature: Annotated[float, Field(ge=-100, le=100, default=100)]
    """this is the indoor temperature above which ventilation is shutoff"""

    Maximum_Indoor_Temperature_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the indoor temperature versus time above which"""

    Delta_Temperature: Annotated[float, Field(ge=-100, default=-100)]
    """This is the temperature differential between indoor and outdoor below which ventilation is shutoff."""

    Delta_Temperature_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the temperature differential between indoor and outdoor"""

    Minimum_Outdoor_Temperature: Annotated[float, Field(ge=-100, le=100, default=-100)]
    """this is the outdoor temperature below which ventilation is shutoff"""

    Minimum_Outdoor_Temperature_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the outdoor temperature versus time below which"""

    Maximum_Outdoor_Temperature: Annotated[float, Field(ge=-100, le=100, default=100)]
    """this is the outdoor temperature above which ventilation is shutoff"""

    Maximum_Outdoor_Temperature_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the outdoor temperature versus time above which"""

    Maximum_Wind_Speed: Annotated[float, Field(ge=0, le=40, default=40)]
    """this is the outdoor wind speed above which ventilation is shutoff"""