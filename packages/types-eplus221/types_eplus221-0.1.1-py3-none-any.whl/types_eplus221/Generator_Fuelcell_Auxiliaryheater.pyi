from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Generator_Fuelcell_Auxiliaryheater(EpBunch):
    """Intended for modeling an auxiliary heater for a fuel cell power generator, however this"""

    Name: Annotated[str, Field(default=...)]

    Excess_Air_Ratio: Annotated[str, Field()]

    Ancillary_Power_Constant_Term: Annotated[str, Field()]

    Ancillary_Power_Linear_Term: Annotated[str, Field()]

    Skin_Loss_U_Factor_Times_Area_Value: Annotated[str, Field()]

    Skin_Loss_Destination: Annotated[Literal['SurroundingZone', 'AirInletForFuelCell'], Field()]

    Zone_Name_To_Receive_Skin_Losses: Annotated[str, Field()]

    Heating_Capacity_Units: Annotated[Literal['Watts', 'kmol/s'], Field()]

    Maximum_Heating_Capacity_In_Watts: Annotated[str, Field()]

    Minimum_Heating_Capacity_In_Watts: Annotated[str, Field()]

    Maximum_Heating_Capacity_In_Kmol_Per_Second: Annotated[str, Field()]

    Minimum_Heating_Capacity_In_Kmol_Per_Second: Annotated[str, Field()]