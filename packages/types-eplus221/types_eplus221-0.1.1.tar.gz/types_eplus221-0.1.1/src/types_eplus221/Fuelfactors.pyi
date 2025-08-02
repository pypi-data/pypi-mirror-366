from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Fuelfactors(EpBunch):
    """Provides Fuel Factors for Emissions as well as Source=>Site conversions."""

    Existing_Fuel_Resource_Name: Annotated[Literal['Electricity', 'NaturalGas', 'FuelOil#1', 'FuelOil#2', 'Coal', 'Gasoline', 'Propane', 'Diesel', 'OtherFuel1', 'OtherFuel2'], Field()]

    Units_Of_Measure: Annotated[str, Field()]

    Energy_Per_Unit_Factor: Annotated[str, Field()]

    Source_Energy_Factor: Annotated[str, Field()]

    Source_Energy_Schedule_Name: Annotated[str, Field()]

    Co2_Emission_Factor: Annotated[str, Field()]

    Co2_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    Co_Emission_Factor: Annotated[str, Field()]

    Co_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    Ch4_Emission_Factor: Annotated[str, Field()]

    Ch4_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    Nox_Emission_Factor: Annotated[str, Field()]

    Nox_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    N2O_Emission_Factor: Annotated[str, Field()]

    N2O_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    So2_Emission_Factor: Annotated[str, Field()]

    So2_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    Pm_Emission_Factor: Annotated[str, Field()]

    Pm_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    Pm10_Emission_Factor: Annotated[str, Field()]

    Pm10_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    Pm2_5_Emission_Factor: Annotated[str, Field()]

    Pm2_5_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    Nh3_Emission_Factor: Annotated[str, Field()]

    Nh3_Emission_Factor_Schedule_Name: Annotated[str, Field()]

    Nmvoc_Emission_Factor: Annotated[str, Field()]

    Nmvoc_Emission_Factor_Schedule_Name: Annotated[str, Field()]

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