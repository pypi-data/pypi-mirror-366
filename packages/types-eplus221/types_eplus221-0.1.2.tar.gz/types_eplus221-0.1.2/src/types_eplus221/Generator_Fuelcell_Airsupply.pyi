from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Generator_Fuelcell_Airsupply(EpBunch):
    """Used to define details of the air supply subsystem for a fuel cell power generator."""

    Name: Annotated[str, Field(default=...)]

    Air_Inlet_Node_Name: Annotated[str, Field()]

    Blower_Power_Curve_Name: Annotated[str, Field()]

    Blower_Heat_Loss_Factor: Annotated[str, Field()]

    Air_Supply_Rate_Calculation_Mode: Annotated[Literal['AirRatiobyStoics', 'QuadraticFunctionofElectricPower', 'QuadraticFunctionofFuelRate'], Field(default=...)]

    Stoichiometric_Ratio: Annotated[str, Field()]
    """This is the excess air "stoics""""

    Air_Rate_Function_of_Electric_Power_Curve_Name: Annotated[str, Field()]

    Air_Rate_Air_Temperature_Coefficient: Annotated[str, Field()]

    Air_Rate_Function_of_Fuel_Rate_Curve_Name: Annotated[str, Field()]

    Air_Intake_Heat_Recovery_Mode: Annotated[Literal['NoRecovery', 'RecoverBurnerInverterStorage', 'RecoverAuxiliaryBurner', 'RecoverInverterandStorage', 'RecoverInverter', 'RecoverElectricalStorage'], Field(default=...)]

    Air_Supply_Constituent_Mode: Annotated[Literal['AmbientAir', 'UserDefinedConstituents'], Field(default=...)]

    Number_of_UserDefined_Constituents: Annotated[str, Field()]

    Constituent_1_Name: Annotated[Literal['CarbonDioxide', 'Nitrogen', 'Oxygen', 'Water', 'Argon'], Field()]

    Molar_Fraction_1: Annotated[str, Field()]

    Constituent_2_Name: Annotated[Literal['CarbonDioxide', 'Nitrogen', 'Oxygen', 'Water', 'Argon'], Field()]

    Molar_Fraction_2: Annotated[str, Field()]

    Constituent_3_Name: Annotated[Literal['CarbonDioxide', 'Nitrogen', 'Oxygen', 'Water', 'Argon'], Field()]

    Molar_Fraction_3: Annotated[str, Field()]

    Constituent_4_Name: Annotated[Literal['CarbonDioxide', 'Nitrogen', 'Oxygen', 'Water', 'Argon'], Field()]

    Molar_Fraction_4: Annotated[str, Field()]

    Constituent_5_Name: Annotated[Literal['CarbonDioxide', 'Nitrogen', 'Oxygen', 'Water', 'Argon'], Field()]

    Molar_Fraction_5: Annotated[str, Field()]