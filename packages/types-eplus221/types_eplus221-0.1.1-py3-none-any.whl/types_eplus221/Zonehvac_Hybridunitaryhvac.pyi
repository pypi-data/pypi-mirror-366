from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Hybridunitaryhvac(EpBunch):
    """Hybrid Unitary HVAC. A black box model for multi-mode packaged forced air equipment. Independent variables include outdoor air conditions and indoor air conditions. Controlled inputs include operating mode, supply air flow rate, and outdoor air faction. Emperical lookup tables are required to map supply air temperature supply air humidity, electricity use, fuel uses, water use, fan electricity use, and external static pressure as a function of each indpednent varaible and each controlled input. In each timestep the model will choose one or more combinations of settings for mode, supply air flow rate, outdoor air faction, and part runtime fraction so as to satisfy zone requests for sensible cooling, heating, ventilation, and/or dehumidification with the least resource consumption. Equipment in this class may consume electricity, water, and up to two additional fuel types."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Enter the availability schedule name for this system. Schedule value > 0 means the system is available. If this field is blank, the system is always available."""

    Availability_Manager_List_Name: Annotated[str, Field()]
    """Enter the name of an AvailabilityManagerAssignmentList object."""

    Minimum_Supply_Air_Temperature_Schedule_Name: Annotated[str, Field()]
    """Values in this schedule are used as a constraint in choosing the feasible settings for supply air flow rate and ouside air fraction in each operating mode. If this field is blank, no minimum is imposed."""

    Maximum_Supply_Air_Temperature_Schedule_Name: Annotated[str, Field()]
    """Values in this schedule are used as a constraint in choosing the feasible settings for supply air flow rate and outdoor air fraction in each operating mode. If this field is blank, no maximum is imposed."""

    Minimum_Supply_Air_Humidity_Ratio_Schedule_Name: Annotated[str, Field()]
    """Values in this schedule are used as a constraint in choosing the feasible settings for supply air flow rate and outdoor air fraction in each operating mode. If this field is blank, no minimum is imposed."""

    Maximum_Supply_Air_Humidity_Ratio_Schedule_Name: Annotated[str, Field()]
    """Values in this schedule are used as a constraint in choosing the feasible settings for supply air flow rate and outdoor air fraction in each operating mode. If this field is blank, no maximum is imposed."""

    Method_To_Choose_Controlled_Inputs_And_Part_Runtime_Fraction: Annotated[Literal['Automatic', 'User Defined'], Field(default='Automatic')]
    """Select the method that will be used to choose operating mode(s), supply air flow rate(s), outdoor air fraction(s) and part runtime fraction(s) in each time step. "Automatic" = chooses controlled inputs and part runtime fraction(s) to minimize resource use within each time step while best satisfying requested sensible cooling, dehumidification and ventilation, and subject to constraints. "User Defined" = EMS will be used to choose controlled inputs and part runtime fraction(s) in each time step. If this field is blank, default to "Automatic"."""

    Return_Air_Node_Name: Annotated[str, Field(default=...)]
    """Return air node for the hybrid unit must be a zone exhaust node."""

    Outdoor_Air_Node_Name: Annotated[str, Field(default=...)]
    """Outdoor air node for the hybrid unit must be an outdoor air node."""

    Supply_Air_Node_Name: Annotated[str, Field(default=...)]
    """Supply air node for the hybrid unit must be a zone air inlet node."""

    Relief_Node_Name: Annotated[str, Field()]
    """Relief node for the hybrid unit must be a zone exhaust node, unless flow is being balanced elsewhere."""

    System_Maximum_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0)]
    """The value in this field represents the maximum supply air volume flow rate among all operating modes. Values of extensive variables in lookup tables are normalized by the system maximum supply air mass flow rate that was used to build performance curves. The value in this field is used to rescale the output from exenstive variables to a desired system size."""

    External_Static_Pressure_At_System_Maximum_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0)]
    """Input the external static pressure when the system operates at maximum supply air flow rate. Fan affinity laws are used to scale supply fan power from the values tabulated in lookup tables, to values that match the external static pressure input to this field. If this field is blank, the supply fan power is not scaled from the values tabulated in lookup tables."""

    Scaling_Factor: Annotated[float, Field(gt=0, default=1)]
    """The value in this field scales all extensive performance variables including: supply air mass flow rate, fuel uses, and water use. If this field is blank, the default scaling factor is 1."""

    Number_Of_Operating_Modes: Annotated[int, Field(ge=1, le=26, default=1)]
    """The value in this field defines the number of discrete operating modes for the unitary hybrid equipment. Supply air mass flow rate ratio and outdoor air fraction are treated as continuous controlled inputs within each discrete operating mode."""

    Minimum_Time_Between_Mode_Change: Annotated[float, Field(ge=1, default=10)]
    """Any mode selected will not operate for less time than the value input in this field. If the value in this field is larger than each timestep, the mode selected in one time step will persist in later time steps until the minimum time between mode change is satisfied. Supply air mass flow rate and outdoor air fraction within a mode are not subject to minimum runtime and may change in every time step. Mode 0 does not have a minimum time. If this field is blank, the default minimum time between mode change is 10 minutes."""

    First_Fuel_Type: Annotated[Literal['None', 'Electricity', 'NaturalGas', 'PropaneGas', 'FuelOil#1', 'FuelOil#2', 'Diesel', 'Gasoline', 'Coal', 'OtherFuel1', 'OtherFuel2', 'Steam', 'DistrictHeating', 'DistrictCooling'], Field(default='Electricity')]
    """Select the fuel type associated with field: "System Electric Power Lookup Table" in each mode."""

    Second_Fuel_Type: Annotated[Literal['None', 'Electricity', 'NaturalGas', 'PropaneGas', 'FuelOil#1', 'FuelOil#2', 'Diesel', 'Gasoline', 'Coal', 'OtherFuel1', 'OtherFuel2', 'Steam', 'DistrictHeating', 'DistrictCooling'], Field()]
    """Select the fuel type associated with field: "System Second Fuel Consumption Lookup Table" in each mode."""

    Third_Fuel_Type: Annotated[Literal['None', 'Electricity', 'NaturalGas', 'PropaneGas', 'FuelOil#1', 'FuelOil#2', 'Diesel', 'Gasoline', 'Coal', 'OtherFuel1', 'OtherFuel2', 'Steam', 'DistrictHeating', 'DistrictCooling'], Field()]
    """Select the fuel type associated with field: "System Third Fuel Consumption Lookup Table" in each mode."""

    Objective_Function_To_Minimize: Annotated[Literal['Electricity Use', 'Second Fuel Use', 'Third Fuel Use', 'Water Use'], Field(default='Electricity Use')]
    """In each time step, controlled variables will be chosen to minimize the selection in this field, subject to constraints."""

    Design_Specification_Outdoor_Air_Object_Name: Annotated[str, Field()]
    """Enter the name of a DesignSpecification:OutdoorAir object. Information in that object will be used to compute the minimum outdoor air flow rate in each time step."""

    Mode_0_Name: Annotated[str, Field()]
    """Enter a name for Mode 0."""

    Mode_0_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 0."""

    Mode_0_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 0."""

    Mode_0_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 0."""

    Mode_0_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 0."""

    Mode_0_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 0."""

    Mode_0_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 0."""

    Mode_0_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 0."""

    Mode_0_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 0."""

    Mode_0_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.00)]
    """Enter the outdoor air fraction for Mode 0."""

    Mode_0_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.00)]
    """Enter the supply air mass flow rate ratio for Mode 0. The value in this field will be used to determine the supply air mass flow rate in Mode 0."""

    Mode_1_Name: Annotated[str, Field()]
    """Enter a name for Mode 1."""

    Mode_1_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 1."""

    Mode_1_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 1."""

    Mode_1_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 1."""

    Mode_1_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 1."""

    Mode_1_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 1."""

    Mode_1_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 1."""

    Mode_1_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 1."""

    Mode_1_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 1."""

    Mode_1_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 1."""

    Mode_1_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 1."""

    Mode_1_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 1."""

    Mode_1_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 1."""

    Mode_1_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 1."""

    Mode_1_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 1."""

    Mode_1_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 1."""

    Mode_1_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 1."""

    Mode_1_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 1."""

    Mode_1_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 1."""

    Mode_1_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 1."""

    Mode_1_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 1."""

    Mode_1_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 1."""

    Mode_1_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 1."""

    Mode_1_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 1."""

    Mode_1_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 1."""

    Mode_2_Name: Annotated[str, Field()]
    """Enter a name for Mode 2."""

    Mode_2_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 2."""

    Mode_2_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 2."""

    Mode_2_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 2."""

    Mode_2_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 2."""

    Mode_2_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 2."""

    Mode_2_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 2."""

    Mode_2_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 2."""

    Mode_2_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 2."""

    Mode_2_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 2."""

    Mode_2_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 2."""

    Mode_2_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 2."""

    Mode_2_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 2."""

    Mode_2_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 2."""

    Mode_2_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 2."""

    Mode_2_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 2."""

    Mode_2_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 2."""

    Mode_2_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 2."""

    Mode_2_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 2."""

    Mode_2_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 2."""

    Mode_2_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 2."""

    Mode_2_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 2."""

    Mode_2_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 2."""

    Mode_2_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 2."""

    Mode_2_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 2."""

    Mode_3_Name: Annotated[str, Field()]
    """Enter a name for Mode 3."""

    Mode_3_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 3."""

    Mode_3_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 3."""

    Mode_3_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 3."""

    Mode_3_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 3."""

    Mode_3_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 3."""

    Mode_3_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 3."""

    Mode_3_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 3."""

    Mode_3_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 3."""

    Mode_3_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 3."""

    Mode_3_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 3."""

    Mode_3_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 3."""

    Mode_3_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 3."""

    Mode_3_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 3."""

    Mode_3_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 3."""

    Mode_3_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 3."""

    Mode_3_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 3."""

    Mode_3_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 3."""

    Mode_3_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 3."""

    Mode_3_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 3."""

    Mode_3_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 3."""

    Mode_3_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 3."""

    Mode_3_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 3."""

    Mode_3_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 3."""

    Mode_3_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 3."""

    Mode_4_Name: Annotated[str, Field()]
    """Enter a name for Mode 4."""

    Mode_4_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 4."""

    Mode_4_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 4."""

    Mode_4_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 4."""

    Mode_4_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 4."""

    Mode_4_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 4."""

    Mode_4_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 4."""

    Mode_4_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 4."""

    Mode_4_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 4."""

    Mode_4_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 4."""

    Mode_4_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 4."""

    Mode_4_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 4."""

    Mode_4_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 4."""

    Mode_4_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 4."""

    Mode_4_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 4."""

    Mode_4_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 4."""

    Mode_4_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 4."""

    Mode_4_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 4."""

    Mode_4_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 4."""

    Mode_4_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 4."""

    Mode_4_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 4."""

    Mode_4_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 4."""

    Mode_4_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 4."""

    Mode_4_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 4."""

    Mode_4_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 4."""

    Mode_5_Name: Annotated[str, Field()]
    """Enter a name for Mode 5."""

    Mode_5_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 5."""

    Mode_5_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 5."""

    Mode_5_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 5."""

    Mode_5_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 5."""

    Mode_5_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 5."""

    Mode_5_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 5."""

    Mode_5_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 5."""

    Mode_5_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 5."""

    Mode_5_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 5."""

    Mode_5_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 5."""

    Mode_5_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 5."""

    Mode_5_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 5."""

    Mode_5_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 5."""

    Mode_5_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 5."""

    Mode_5_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 5."""

    Mode_5_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 5."""

    Mode_5_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 5."""

    Mode_5_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 5."""

    Mode_5_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 5."""

    Mode_5_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 5."""

    Mode_5_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 5."""

    Mode_5_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 5."""

    Mode_5_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 5."""

    Mode_5_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 5."""

    Mode_6_Name: Annotated[str, Field()]
    """Enter a name for Mode 6."""

    Mode_6_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 6."""

    Mode_6_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 6."""

    Mode_6_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 6."""

    Mode_6_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 6."""

    Mode_6_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 6."""

    Mode_6_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 6."""

    Mode_6_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 6."""

    Mode_6_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 6."""

    Mode_6_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 6."""

    Mode_6_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 6."""

    Mode_6_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 6."""

    Mode_6_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 6."""

    Mode_6_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 6."""

    Mode_6_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 6."""

    Mode_6_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 6."""

    Mode_6_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 6."""

    Mode_6_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 6."""

    Mode_6_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 6."""

    Mode_6_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 6."""

    Mode_6_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 6."""

    Mode_6_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 6."""

    Mode_6_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 6."""

    Mode_6_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 6."""

    Mode_6_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 6."""

    Mode_7_Name: Annotated[str, Field()]
    """Enter a name for Mode 7."""

    Mode_7_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 7."""

    Mode_7_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 7."""

    Mode_7_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 7."""

    Mode_7_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 7."""

    Mode_7_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 7."""

    Mode_7_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 7."""

    Mode_7_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 7."""

    Mode_7_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 7."""

    Mode_7_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 7."""

    Mode_7_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 7."""

    Mode_7_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 7."""

    Mode_7_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 7."""

    Mode_7_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 7."""

    Mode_7_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 7."""

    Mode_7_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 7."""

    Mode_7_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 7."""

    Mode_7_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 7."""

    Mode_7_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 7."""

    Mode_7_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 7."""

    Mode_7_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 7."""

    Mode_7_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 7."""

    Mode_7_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 7."""

    Mode_7_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 7."""

    Mode_7_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 7."""

    Mode_8_Name: Annotated[str, Field()]
    """Enter a name for Mode 8."""

    Mode_8_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 8."""

    Mode_8_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 8."""

    Mode_8_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 8."""

    Mode_8_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 8."""

    Mode_8_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 8."""

    Mode_8_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 8."""

    Mode_8_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 8."""

    Mode_8_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 8."""

    Mode_8_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 8."""

    Mode_8_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 8."""

    Mode_8_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 8."""

    Mode_8_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 8."""

    Mode_8_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 8."""

    Mode_8_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 8."""

    Mode_8_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 8."""

    Mode_8_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 8."""

    Mode_8_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 8."""

    Mode_8_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 8."""

    Mode_8_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 8."""

    Mode_8_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 8."""

    Mode_8_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 8."""

    Mode_8_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 8."""

    Mode_8_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 8."""

    Mode_8_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 8."""

    Mode_9_Name: Annotated[str, Field()]
    """Enter a name for Mode 9."""

    Mode_9_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 9."""

    Mode_9_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 9."""

    Mode_9_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 9."""

    Mode_9_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 9."""

    Mode_9_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 9."""

    Mode_9_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 9."""

    Mode_9_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 9."""

    Mode_9_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 9."""

    Mode_9_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 9."""

    Mode_9_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 9."""

    Mode_9_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 9."""

    Mode_9_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 9."""

    Mode_9_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 9."""

    Mode_9_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 9."""

    Mode_9_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 9."""

    Mode_9_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 9."""

    Mode_9_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 9."""

    Mode_9_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 9."""

    Mode_9_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 9."""

    Mode_9_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 9."""

    Mode_9_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 9."""

    Mode_9_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 9."""

    Mode_9_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 9."""

    Mode_9_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 9."""

    Mode_10_Name: Annotated[str, Field()]
    """Enter a name for Mode 10."""

    Mode_10_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 10."""

    Mode_10_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 10."""

    Mode_10_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 10."""

    Mode_10_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 10."""

    Mode_10_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 10."""

    Mode_10_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 10."""

    Mode_10_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 10."""

    Mode_10_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 10."""

    Mode_10_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 10."""

    Mode_10_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 10."""

    Mode_10_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 10."""

    Mode_10_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 10."""

    Mode_10_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 10."""

    Mode_10_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 10."""

    Mode_10_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 10."""

    Mode_10_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 10."""

    Mode_10_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 10."""

    Mode_10_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 10."""

    Mode_10_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 10."""

    Mode_10_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 10."""

    Mode_10_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 10."""

    Mode_10_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 10."""

    Mode_10_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 10."""

    Mode_11_Name: Annotated[str, Field()]
    """Enter a name for Mode 11."""

    Mode_11_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 11."""

    Mode_11_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 11."""

    Mode_11_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 11."""

    Mode_11_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 11."""

    Mode_11_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 11."""

    Mode_11_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 11."""

    Mode_11_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 11."""

    Mode_11_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 11."""

    Mode_11_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 11."""

    Mode_11_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 11."""

    Mode_11_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 11."""

    Mode_11_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 11."""

    Mode_11_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 11."""

    Mode_11_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 11."""

    Mode_11_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 11."""

    Mode_11_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 11."""

    Mode_11_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 11."""

    Mode_11_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 11."""

    Mode_11_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 11."""

    Mode_11_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 11."""

    Mode_11_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 11."""

    Mode_11_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 11."""

    Mode_11_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 11."""

    Mode_11_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 11."""

    Mode_12_Name: Annotated[str, Field()]
    """Enter a name for Mode 12."""

    Mode_12_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 12."""

    Mode_12_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 12."""

    Mode_12_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 12."""

    Mode_12_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 12."""

    Mode_12_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 12."""

    Mode_12_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 12."""

    Mode_12_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 12."""

    Mode_12_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 12."""

    Mode_12_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 12."""

    Mode_12_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 12."""

    Mode_12_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 12."""

    Mode_12_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 12."""

    Mode_12_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 12."""

    Mode_12_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 12."""

    Mode_12_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 12."""

    Mode_12_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 12."""

    Mode_12_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 12."""

    Mode_12_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 12."""

    Mode_12_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 12."""

    Mode_12_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 12."""

    Mode_12_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 12."""

    Mode_12_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 12."""

    Mode_12_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 12."""

    Mode_12_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 12."""

    Mode_13_Name: Annotated[str, Field()]
    """Enter a name for Mode 13."""

    Mode_13_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 13."""

    Mode_13_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 13."""

    Mode_13_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 13."""

    Mode_13_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 13."""

    Mode_13_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 13."""

    Mode_13_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 13."""

    Mode_13_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 13."""

    Mode_13_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 13."""

    Mode_13_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 13."""

    Mode_13_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 13."""

    Mode_13_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 13."""

    Mode_13_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 13."""

    Mode_13_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 13."""

    Mode_13_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 13."""

    Mode_13_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 13."""

    Mode_13_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 13."""

    Mode_13_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 13."""

    Mode_13_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 13."""

    Mode_13_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 13."""

    Mode_13_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 13."""

    Mode_13_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 13."""

    Mode_13_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 13."""

    Mode_13_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 13."""

    Mode_13_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 13."""

    Mode_14_Name: Annotated[str, Field()]
    """Enter a name for Mode 14."""

    Mode_14_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 14."""

    Mode_14_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 14."""

    Mode_14_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 14."""

    Mode_14_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 14."""

    Mode_14_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 14."""

    Mode_14_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 14."""

    Mode_14_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 14."""

    Mode_14_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 14."""

    Mode_14_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 14."""

    Mode_14_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 14."""

    Mode_14_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 14."""

    Mode_14_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 14."""

    Mode_14_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 14."""

    Mode_14_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 14."""

    Mode_14_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 14."""

    Mode_14_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 14."""

    Mode_14_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 14."""

    Mode_14_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 14."""

    Mode_14_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 14."""

    Mode_14_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 14."""

    Mode_14_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 14."""

    Mode_14_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 14."""

    Mode_14_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 14."""

    Mode_14_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 14."""

    Mode_15_Name: Annotated[str, Field()]
    """Enter a name for Mode 15."""

    Mode_15_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 15."""

    Mode_15_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 15."""

    Mode_15_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 15."""

    Mode_15_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 15."""

    Mode_15_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 15."""

    Mode_15_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 15."""

    Mode_15_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 15."""

    Mode_15_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 15."""

    Mode_15_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 15."""

    Mode_15_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 15."""

    Mode_15_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 15."""

    Mode_15_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 15."""

    Mode_15_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 15."""

    Mode_15_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 15."""

    Mode_15_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 15."""

    Mode_15_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 15."""

    Mode_15_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 15."""

    Mode_15_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 15."""

    Mode_15_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 15."""

    Mode_15_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 15."""

    Mode_15_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 15."""

    Mode_15_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 15."""

    Mode_15_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 15."""

    Mode_15_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 15."""

    Mode_16_Name: Annotated[str, Field()]
    """Enter a name for Mode 16."""

    Mode_16_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 16."""

    Mode_16_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 16."""

    Mode_16_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 16."""

    Mode_16_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 16."""

    Mode_16_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 16."""

    Mode_16_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 16."""

    Mode_16_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 16."""

    Mode_16_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 16."""

    Mode_16_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 16."""

    Mode_16_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 16."""

    Mode_16_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 16."""

    Mode_16_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 16."""

    Mode_16_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 16."""

    Mode_16_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 16."""

    Mode_16_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 16."""

    Mode_16_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 16."""

    Mode_16_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 16."""

    Mode_16_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 16."""

    Mode_16_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 16."""

    Mode_16_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 16."""

    Mode_16_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 16."""

    Mode_16_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 16."""

    Mode_16_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 16."""

    Mode_16_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 16."""

    Mode_17_Name: Annotated[str, Field()]
    """Enter a name for Mode 17."""

    Mode_17_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 17."""

    Mode_17_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 17."""

    Mode_17_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 17."""

    Mode_17_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 17."""

    Mode_17_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 17."""

    Mode_17_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 17."""

    Mode_17_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 17."""

    Mode_17_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 17."""

    Mode_17_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 17."""

    Mode_17_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 17."""

    Mode_17_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 17."""

    Mode_17_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 17."""

    Mode_17_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 17."""

    Mode_17_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 17."""

    Mode_17_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 17."""

    Mode_17_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 17."""

    Mode_17_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 17."""

    Mode_17_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 17."""

    Mode_17_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 17."""

    Mode_17_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 17."""

    Mode_17_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 17."""

    Mode_17_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 17."""

    Mode_17_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 17."""

    Mode_17_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 17."""

    Mode_18_Name: Annotated[str, Field()]
    """Enter a name for Mode 18."""

    Mode_18_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 18."""

    Mode_18_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 18."""

    Mode_18_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 18."""

    Mode_18_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 18."""

    Mode_18_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 18."""

    Mode_18_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 18."""

    Mode_18_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 18."""

    Mode_18_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 18."""

    Mode_18_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 18."""

    Mode_18_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 18."""

    Mode_18_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 18."""

    Mode_18_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 18."""

    Mode_18_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 18."""

    Mode_18_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 18."""

    Mode_18_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 18."""

    Mode_18_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 18."""

    Mode_18_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 18."""

    Mode_18_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 18."""

    Mode_18_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 18."""

    Mode_18_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 18."""

    Mode_18_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 18."""

    Mode_18_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 18."""

    Mode_18_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 18."""

    Mode_18_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 18."""

    Mode_19_Name: Annotated[str, Field()]
    """Enter a name for Mode 19."""

    Mode_19_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 19."""

    Mode_19_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 19."""

    Mode_19_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 19."""

    Mode_19_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 19."""

    Mode_19_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 19."""

    Mode_19_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 19."""

    Mode_19_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 19."""

    Mode_19_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 19."""

    Mode_19_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 19."""

    Mode_19_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 19."""

    Mode_19_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 19."""

    Mode_19_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 19."""

    Mode_19_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 19."""

    Mode_19_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 19."""

    Mode_19_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 19."""

    Mode_19_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 19."""

    Mode_19_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 19."""

    Mode_19_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 19."""

    Mode_19_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 19."""

    Mode_19_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 19."""

    Mode_19_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 19."""

    Mode_19_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 19."""

    Mode_19_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 19."""

    Mode_19_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 19."""

    Mode_20_Name: Annotated[str, Field()]
    """Enter a name for Mode 20."""

    Mode_20_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 20."""

    Mode_20_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 20."""

    Mode_20_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 20."""

    Mode_20_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 20."""

    Mode_20_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 20."""

    Mode_20_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 20."""

    Mode_20_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 20."""

    Mode_20_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 20."""

    Mode_20_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 20."""

    Mode_20_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 20."""

    Mode_20_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 20."""

    Mode_20_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 20."""

    Mode_20_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 20."""

    Mode_20_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 20."""

    Mode_20_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 20."""

    Mode_20_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 20."""

    Mode_20_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 20."""

    Mode_20_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 20."""

    Mode_20_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 20."""

    Mode_20_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 20."""

    Mode_20_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 20."""

    Mode_20_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 20."""

    Mode_20_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 20."""

    Mode_20_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 20."""

    Mode_21_Name: Annotated[str, Field()]
    """Enter a name for Mode 21."""

    Mode_21_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 21."""

    Mode_21_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 21."""

    Mode_21_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 21."""

    Mode_21_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 21."""

    Mode_21_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 21."""

    Mode_21_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 21."""

    Mode_21_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 21."""

    Mode_21_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 21."""

    Mode_21_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 21."""

    Mode_21_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 21."""

    Mode_21_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 21."""

    Mode_21_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 21."""

    Mode_21_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 21."""

    Mode_21_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 21."""

    Mode_21_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 21."""

    Mode_21_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 21."""

    Mode_21_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 21."""

    Mode_21_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 21."""

    Mode_21_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 21."""

    Mode_21_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 21."""

    Mode_21_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 21."""

    Mode_21_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 21."""

    Mode_21_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 21."""

    Mode_21_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 21."""

    Mode_22_Name: Annotated[str, Field()]
    """Enter a name for Mode 22."""

    Mode_22_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 22."""

    Mode_22_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 22."""

    Mode_22_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 22."""

    Mode_22_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 22."""

    Mode_22_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 22."""

    Mode_22_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 22."""

    Mode_22_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 22."""

    Mode_22_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 22."""

    Mode_22_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 22."""

    Mode_22_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 22."""

    Mode_22_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 22."""

    Mode_22_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 22."""

    Mode_22_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 22."""

    Mode_22_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 22."""

    Mode_22_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 22."""

    Mode_22_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 22."""

    Mode_22_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 22."""

    Mode_22_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 22."""

    Mode_22_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 22."""

    Mode_22_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 22."""

    Mode_22_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 22."""

    Mode_22_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 22."""

    Mode_22_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 22."""

    Mode_22_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 22."""

    Mode_23_Name: Annotated[str, Field()]
    """Enter a name for Mode 23."""

    Mode_23_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 23."""

    Mode_23_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 23."""

    Mode_23_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 23."""

    Mode_23_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 23."""

    Mode_23_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 23."""

    Mode_23_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 23."""

    Mode_23_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 23."""

    Mode_23_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 23."""

    Mode_23_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 23."""

    Mode_23_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 23."""

    Mode_23_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 23."""

    Mode_23_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 23."""

    Mode_23_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 23."""

    Mode_23_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 23."""

    Mode_23_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 23."""

    Mode_23_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 23."""

    Mode_23_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 23."""

    Mode_23_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 23."""

    Mode_23_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 23."""

    Mode_23_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 23."""

    Mode_23_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 23."""

    Mode_23_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 23."""

    Mode_23_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 23."""

    Mode_23_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 23."""

    Mode_24_Name: Annotated[str, Field()]
    """Enter a name for Mode 24."""

    Mode_24_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 24."""

    Mode_24_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 24."""

    Mode_24_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 24."""

    Mode_24_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 24."""

    Mode_24_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 24."""

    Mode_24_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 24."""

    Mode_24_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 24."""

    Mode_24_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 24."""

    Mode_24_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 24."""

    Mode_24_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 24."""

    Mode_24_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 24."""

    Mode_24_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 24."""

    Mode_24_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 24."""

    Mode_24_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 24."""

    Mode_24_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 24."""

    Mode_24_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 24."""

    Mode_24_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 24."""

    Mode_24_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 24."""

    Mode_24_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 24."""

    Mode_24_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 24."""

    Mode_24_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 24."""

    Mode_24_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 24."""

    Mode_24_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 24."""

    Mode_24_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 24."""

    Mode_25_Name: Annotated[str, Field()]
    """Enter a name for Mode 25."""

    Mode_25_Supply_Air_Temperature_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Temperature Lookup Table for Mode 25."""

    Mode_25_Supply_Air_Humidity_Ratio_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Air Humidity Ratio Lookup Table for Mode 25."""

    Mode_25_System_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Electric Power Lookup Table for Mode 25."""

    Mode_25_Supply_Fan_Electric_Power_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the Supply Fan Electric Power Lookup Table for Mode 25."""

    Mode_25_External_Static_Pressure_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the External Static Pressure Lookup Table for Mode 25."""

    Mode_25_System_Second_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Second Fuel Consumption Lookup Table for Mode 25."""

    Mode_25_System_Third_Fuel_Consumption_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Third Fuel Consumption Lookup Table for Mode 25."""

    Mode_25_System_Water_Use_Lookup_Table_Name: Annotated[str, Field()]
    """Enter the name of the System Water Use Lookup Table for Mode 25."""

    Mode_25_Minimum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor air temperature allowed for Mode 25."""

    Mode_25_Maximum_Outdoor_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor air temperature allowed for Mode 25."""

    Mode_25_Minimum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum outdoor humidity ratio allowed for Mode 25."""

    Mode_25_Maximum_Outdoor_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum outdoor air humidity ratio allowed for Mode 25."""

    Mode_25_Minimum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum outdoor relative humidity allowed for Mode 25."""

    Mode_25_Maximum_Outdoor_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum outdoor air relative humidity allowed for Mode 25."""

    Mode_25_Minimum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the minimum return air temperature allowed for Mode 25."""

    Mode_25_Maximum_Return_Air_Temperature: Annotated[float, Field()]
    """Enter the maximum return air temperature allowed for Mode 25."""

    Mode_25_Minimum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.00)]
    """Enter the minimum return air humidity ratio allowed for Mode 25."""

    Mode_25_Maximum_Return_Air_Humidity_Ratio: Annotated[float, Field(ge=0.00, le=0.10, default=0.10)]
    """Enter the maximum return air humidity ratio allowed for Mode 25."""

    Mode_25_Minimum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=0.00)]
    """Enter the minimum return air relative humidity allowed for Mode 25."""

    Mode_25_Maximum_Return_Air_Relative_Humidity: Annotated[float, Field(ge=0.00, le=100.00, default=100.00)]
    """Enter the maximum return air relative humdity allowed for Mode 25."""

    Mode_25_Minimum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum outdoor air fraction allowed for Mode 25."""

    Mode_25_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum outdoor air fraction allowed for Mode 25."""

    Mode_25_Minimum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=0.10)]
    """Enter the minimum supply air mass flow rate ratio allowed for Mode 25."""

    Mode_25_Maximum_Supply_Air_Mass_Flow_Rate_Ratio: Annotated[float, Field(ge=0.00, le=1.00, default=1.00)]
    """Enter the maximum supply air mass flow rate ratio allowed for Mode 25."""