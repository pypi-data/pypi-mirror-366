from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zoneearthtube(EpBunch):
    """Earth Tube is specified as a design level which is modified by a Schedule fraction, temperature difference and wind speed:"""

    Zone_Name: Annotated[str, Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]

    Design_Flow_Rate: Annotated[float, Field(default=..., ge=0)]
    """"Edesign" in Equation"""

    Minimum_Zone_Temperature_When_Cooling: Annotated[float, Field(default=..., ge=-100, le=100)]
    """this is the indoor temperature below which the earth tube is shut off"""

    Maximum_Zone_Temperature_When_Heating: Annotated[float, Field(default=..., ge=-100, le=100)]
    """this is the indoor temperature above which the earth tube is shut off"""

    Delta_Temperature: Annotated[float, Field(default=..., ge=0)]
    """This is the temperature difference between indoor and outdoor below which the earth tube is shut off"""

    Earthtube_Type: Annotated[Literal['Natural', 'Intake', 'Exhaust'], Field(default='Natural')]

    Fan_Pressure_Rise: Annotated[float, Field(ge=0, default=0)]
    """pressure rise across the fan"""

    Fan_Total_Efficiency: Annotated[float, Field(gt=0, default=1)]

    Pipe_Radius: Annotated[float, Field(gt=0, default=1)]

    Pipe_Thickness: Annotated[float, Field(gt=0, default=0.2)]

    Pipe_Length: Annotated[float, Field(gt=0, default=15)]

    Pipe_Thermal_Conductivity: Annotated[float, Field(gt=0, default=200)]

    Pipe_Depth_Under_Ground_Surface: Annotated[float, Field(gt=0, default=3)]

    Soil_Condition: Annotated[Literal['HeavyAndSaturated', 'HeavyAndDamp', 'HeavyAndDry', 'LightAndDry'], Field(default='HeavyAndDamp')]

    Average_Soil_Surface_Temperature: Annotated[float, Field(default=...)]

    Amplitude_Of_Soil_Surface_Temperature: Annotated[float, Field(default=..., ge=0)]

    Phase_Constant_Of_Soil_Surface_Temperature: Annotated[float, Field(default=..., ge=0)]

    Constant_Term_Flow_Coefficient: Annotated[float, Field(default=1)]
    """"A" in Equation"""

    Temperature_Term_Flow_Coefficient: Annotated[float, Field(default=0)]
    """"B" in Equation"""

    Velocity_Term_Flow_Coefficient: Annotated[float, Field(default=0)]
    """"C" in Equation"""

    Velocity_Squared_Term_Flow_Coefficient: Annotated[float, Field(default=0)]
    """"D" in Equation"""