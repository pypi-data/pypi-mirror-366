from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hybridmodel_Zone(EpBunch):
    """Zones with measured air temperature data and a range of dates."""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Calculate_Zone_Internal_Thermal_Mass: Annotated[Literal['No', 'Yes'], Field(default='No')]
    """Use measured zone air temperature to calculate zone internal thermal mass."""

    Calculate_Zone_Air_Infiltration_Rate: Annotated[Literal['No', 'Yes'], Field(default='No')]
    """Use measured temperature data (temperature, humidity ratio, or CO2 concentration) to calculate zone air infiltration air flow rate."""

    Calculate_Zone_People_Count: Annotated[Literal['No', 'Yes'], Field(default='No')]
    """Use measured humidity ratio data (temperature, humidity ratio, or CO2 concentration) to calculate zone people count."""

    Zone_Measured_Air_Temperature_Schedule_Name: Annotated[str, Field()]
    """from Schedule:File"""

    Zone_Measured_Air_Humidity_Ratio_Schedule_Name: Annotated[str, Field()]
    """from Schedule:File"""

    Zone_Measured_Air_CO2_Concentration_Schedule_Name: Annotated[str, Field()]
    """from Schedule:File"""

    Zone_Input_People_Activity_Schedule_Name: Annotated[str, Field()]
    """When this field is provided and valid, the default people activity level (used to calculate people count) will be overwritten."""

    Zone_Input_People_Sensible_Heat_Fraction_Schedule_Name: Annotated[str, Field()]
    """When this field is provided and valid, the default sensible heat fraction from people (used to calculate people count) will be overwritten."""

    Zone_Input_People_Radiant_Heat_Fraction_Schedule_Name: Annotated[str, Field()]
    """When this field is provided and valid, the default radiant heat portion of the sensible heat from people (used to calculate people count) will be overwritten."""

    Zone_Input_People_CO2_Generation_Rate_Schedule_Name: Annotated[str, Field()]
    """When this field is provided and valid, the default people CO2 generation rate (used to calculate people count) will be overwritten."""

    Zone_Input_Supply_Air_Temperature_Schedule_Name: Annotated[str, Field()]
    """from Schedule:File"""

    Zone_Input_Supply_Air_Mass_Flow_Rate_Schedule_Name: Annotated[str, Field()]
    """from Schedule:File"""

    Zone_Input_Supply_Air_Humidity_Ratio_Schedule_Name: Annotated[str, Field()]
    """from Schedule:File"""

    Zone_Input_Supply_Air_CO2_Concentration_Schedule_Name: Annotated[str, Field()]
    """from Schedule:File"""

    Begin_Month: Annotated[int, Field(default=..., ge=1, le=12)]

    Begin_Day_of_Month: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_of_Month: Annotated[int, Field(default=..., ge=1, le=31)]