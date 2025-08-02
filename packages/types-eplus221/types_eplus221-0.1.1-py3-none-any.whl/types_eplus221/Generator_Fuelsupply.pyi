from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Generator_Fuelsupply(EpBunch):
    """Used only with Generator:FuelCell and Generator:MicroCHP"""

    Name: Annotated[str, Field(default=...)]

    Fuel_Temperature_Modeling_Mode: Annotated[Literal['TemperatureFromAirNode', 'Scheduled'], Field()]

    Fuel_Temperature_Reference_Node_Name: Annotated[str, Field()]

    Fuel_Temperature_Schedule_Name: Annotated[str, Field()]

    Compressor_Power_Multiplier_Function_Of_Fuel_Rate_Curve_Name: Annotated[str, Field()]

    Compressor_Heat_Loss_Factor: Annotated[str, Field()]

    Fuel_Type: Annotated[Literal['GaseousConstituents', 'LiquidGeneric'], Field()]

    Liquid_Generic_Fuel_Lower_Heating_Value: Annotated[str, Field()]

    Liquid_Generic_Fuel_Higher_Heating_Value: Annotated[str, Field()]

    Liquid_Generic_Fuel_Molecular_Weight: Annotated[str, Field()]

    Liquid_Generic_Fuel_Co2_Emission_Factor: Annotated[str, Field()]

    Number_Of_Constituents_In_Gaseous_Constituent_Fuel_Supply: Annotated[str, Field()]

    Constituent_1_Name: Annotated[Literal['CarbonDioxide', 'Nitrogen', 'Oxygen', 'Water', 'Argon', 'Hydrogen', 'Methane', 'Ethane', 'Propane', 'Butane', 'Pentane', 'Hexane', 'Methanol', 'Ethanol'], Field()]

    Constituent_1_Molar_Fraction: Annotated[str, Field()]

    Constituent_2_Name: Annotated[Literal['CarbonDioxide', 'Nitrogen', 'Oxygen', 'Water', 'Argon', 'Hydrogen', 'Methane', 'Ethane', 'Propane', 'Butane', 'Pentane', 'Hexane', 'Methanol', 'Ethanol'], Field()]

    Constituent_2_Molar_Fraction: Annotated[str, Field()]

    Constituent_3_Name: Annotated[Literal['CarbonDioxide', 'Nitrogen', 'Oxygen', 'Water', 'Argon', 'Hydrogen', 'Methane', 'Ethane', 'Propane', 'Butane', 'Pentane', 'Hexane', 'Methanol', 'Ethanol'], Field()]

    Constituent_3_Molar_Fraction: Annotated[str, Field()]

    Constituent_4_Name: Annotated[Literal['CarbonDioxide', 'Nitrogen', 'Oxygen', 'Water', 'Argon', 'Hydrogen', 'Methane', 'Ethane', 'Propane', 'Butane', 'Pentane', 'Hexane', 'Methanol', 'Ethanol'], Field()]

    Constituent_4_Molar_Fraction: Annotated[str, Field()]

    Constituent_5_Name: Annotated[Literal['CarbonDioxide', 'Nitrogen', 'Oxygen', 'Water', 'Argon', 'Hydrogen', 'Methane', 'Ethane', 'Propane', 'Butane', 'Pentane', 'Hexane', 'Methanol', 'Ethanol'], Field()]

    Constituent_5_Molar_Fraction: Annotated[str, Field()]

    Constituent_6_Name: Annotated[Literal['CarbonDioxide', 'Nitrogen', 'Oxygen', 'Water', 'Argon', 'Hydrogen', 'Methane', 'Ethane', 'Propane', 'Butane', 'Pentane', 'Hexane', 'Methanol', 'Ethanol'], Field()]

    Constituent_6_Molar_Fraction: Annotated[str, Field()]

    Constituent_7_Name: Annotated[Literal['Hydrogen', 'Methane', 'Ethane', 'Propane', 'Butane', 'Pentane', 'Hexane', 'Methanol', 'Ethanol'], Field()]

    Constituent_7_Molar_Fraction: Annotated[str, Field()]

    Constituent_8_Name: Annotated[Literal['CarbonDioxide', 'Nitrogen', 'Oxygen', 'Water', 'Argon', 'Hydrogen', 'Methane', 'Ethane', 'Propane', 'Butane', 'Pentane', 'Hexane', 'Methanol', 'Ethanol'], Field()]

    Constituent_8_Molar_Fraction: Annotated[str, Field()]

    Constituent_9_Name: Annotated[Literal['CarbonDioxide', 'Nitrogen', 'Oxygen', 'Water', 'Argon', 'Hydrogen', 'Methane', 'Ethane', 'Propane', 'Butane', 'Pentane', 'Hexane', 'Methanol', 'Ethanol'], Field()]

    Constituent_9_Molar_Fraction: Annotated[str, Field()]

    Constituent_10_Name: Annotated[Literal['CarbonDioxide', 'Nitrogen', 'Oxygen', 'Water', 'Argon', 'Hydrogen', 'Methane', 'Ethane', 'Propane', 'Butane', 'Pentane', 'Hexane', 'Methanol', 'Ethanol'], Field()]

    Constituent_10_Molar_Fraction: Annotated[str, Field()]

    Constituent_11_Name: Annotated[Literal['CarbonDioxide', 'Nitrogen', 'Oxygen', 'Water', 'Argon', 'Hydrogen', 'Methane', 'Ethane', 'Propane', 'Butane', 'Pentane', 'Hexane', 'Methanol', 'Ethanol'], Field()]

    Constituent_11_Molar_Fraction: Annotated[str, Field()]

    Constituent_12_Name: Annotated[Literal['CarbonDioxide', 'Nitrogen', 'Oxygen', 'Water', 'Argon', 'Hydrogen', 'Methane', 'Ethane', 'Propane', 'Butane', 'Pentane', 'Hexane', 'Methanol', 'Ethanol'], Field()]

    Constituent_12_Molar_Fraction: Annotated[str, Field()]