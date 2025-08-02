from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Fuelfactors(EpBunch):
    """Provides Fuel Factors for Emissions as well as Source=>Site conversions."""

    Existing_Fuel_Resource_Name: Annotated[Literal['Electricity', 'NaturalGas', 'FuelOil#1', 'FuelOil#2', 'Coal', 'Gasoline', 'Propane', 'Diesel', 'OtherFuel1', 'OtherFuel2'], Field()]

    Units_of_Measure: Annotated[str, Field()]

    Energy_per_Unit_Factor: Annotated[str, Field()]

    Source_Energy_Factor: Annotated[str, Field()]

    Source_Energy_Schedule_Name: Annotated[str, Field()]

    CO2_Emission_Factor: Annotated[str, Field()]

    CO2_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    CO_Emission_Factor: Annotated[str, Field()]

    CO_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    CH4_Emission_Factor: Annotated[str, Field()]

    CH4_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    NOx_Emission_Factor: Annotated[str, Field()]

    NOx_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    N2O_Emission_Factor: Annotated[str, Field()]

    N2O_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    SO2_Emission_Factor: Annotated[str, Field()]

    SO2_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    PM_Emission_Factor: Annotated[str, Field()]

    PM_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    PM10_Emission_Factor: Annotated[str, Field()]

    PM10_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    PM25_Emission_Factor: Annotated[str, Field()]

    PM25_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    NH3_Emission_Factor: Annotated[str, Field()]

    NH3_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    NMVOC_Emission_Factor: Annotated[str, Field()]

    NMVOC_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    Hg_Emission_Factor: Annotated[str, Field()]

    Hg_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    Pb_Emission_Factor: Annotated[str, Field()]

    Pb_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    Water_Emission_Factor: Annotated[str, Field()]

    Water_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    Nuclear_High_Level_Emission_Factor: Annotated[str, Field()]

    Nuclear_High_Level_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    Nuclear_Low_Level_Emission_Factor: Annotated[str, Field()]

    Nuclear_Low_Level_Emission_Factor_Schedule_Name: Annotated[str, Field()]