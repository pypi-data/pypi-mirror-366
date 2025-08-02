from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Refrigeration_Case(EpBunch):
    """The Refrigeration Case object works in conjunction with a compressor rack, a"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Zone_Name: Annotated[str, Field(default=...)]
    """This must be a controlled zone and appear in a ZoneHVAC:EquipmentConnections object."""

    Rated_Ambient_Temperature: Annotated[float, Field(gt=0.0, default=23.9)]

    Rated_Ambient_Relative_Humidity: Annotated[float, Field(gt=0.0, lt=100.0, default=55.0)]

    Rated_Total_Cooling_Capacity_per_Unit_Length: Annotated[float, Field(gt=0.0, default=1900)]

    Rated_Latent_Heat_Ratio: Annotated[float, Field(ge=0.0, le=1.0, default=0.3)]

    Rated_Runtime_Fraction: Annotated[float, Field(gt=0.0, le=1.0, default=0.85)]

    Case_Length: Annotated[float, Field(gt=0.0, default=3.0)]

    Case_Operating_Temperature: Annotated[float, Field(lt=20.0, default=1.1)]

    Latent_Case_Credit_Curve_Type: Annotated[Literal['CaseTemperatureMethod', 'RelativeHumidityMethod', 'DewpointMethod'], Field(default='CaseTemperatureMethod')]

    Latent_Case_Credit_Curve_Name: Annotated[str, Field(default=...)]

    Standard_Case_Fan_Power_per_Unit_Length: Annotated[float, Field(ge=0.0, default=75.0)]

    Operating_Case_Fan_Power_per_Unit_Length: Annotated[float, Field(ge=0.0, default=75.0)]

    Standard_Case_Lighting_Power_per_Unit_Length: Annotated[float, Field(default=90.0)]

    Installed_Case_Lighting_Power_per_Unit_Length: Annotated[float, Field()]
    """default set equal to Standard Case Lighting Power per Unit Length"""

    Case_Lighting_Schedule_Name: Annotated[str, Field()]

    Fraction_of_Lighting_Energy_to_Case: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Case_AntiSweat_Heater_Power_per_Unit_Length: Annotated[float, Field(ge=0, default=0)]

    Minimum_AntiSweat_Heater_Power_per_Unit_Length: Annotated[float, Field(ge=0, default=0)]
    """This field is only applicable to the Linear, Dewpoint Method, and"""

    AntiSweat_Heater_Control_Type: Annotated[Literal['None', 'Constant', 'Linear', 'DewpointMethod', 'HeatBalanceMethod'], Field()]

    Humidity_at_Zero_AntiSweat_Heater_Energy: Annotated[float, Field(default=-10.0)]
    """This field is only applicable to Linear AS heater control type"""

    Case_Height: Annotated[float, Field(ge=0, default=1.5)]
    """This field only applicable to Heat Balance Method AS heater control type"""

    Fraction_of_AntiSweat_Heater_Energy_to_Case: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Case_Defrost_Power_per_Unit_Length: Annotated[float, Field(ge=0.0, default=0.0)]
    """Used to evaluate load on case as well as power or heat consumption"""

    Case_Defrost_Type: Annotated[Literal['None', 'OffCycle', 'HotGas', 'Electric', 'HotFluid', 'HotGasWithTemperatureTermination', 'ElectricWithTemperatureTermination', 'HotFluidWithTemperatureTermination'], Field(default='OffCycle')]

    Case_Defrost_Schedule_Name: Annotated[str, Field()]
    """A case defrost schedule name is required unless case defrost type = None"""

    Case_Defrost_DripDown_Schedule_Name: Annotated[str, Field()]
    """If left blank, the defrost schedule will be used"""

    Defrost_Energy_Correction_Curve_Type: Annotated[Literal['None', 'CaseTemperatureMethod', 'RelativeHumidityMethod', 'DewpointMethod'], Field()]
    """Case Temperature, Relative Humidity, and Dewpoint Method are applicable to case defrost"""

    Defrost_Energy_Correction_Curve_Name: Annotated[str, Field()]
    """Defrost Energy Correction Curve Name is applicable to case defrost types"""

    Under_Case_HVAC_Return_Air_Fraction: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Refrigerated_Case_Restocking_Schedule_Name: Annotated[str, Field()]
    """Schedule values should be in units of Watts per unit case length (W/m)"""

    Case_Credit_Fraction_Schedule_Name: Annotated[str, Field()]
    """Schedule values should be from 0 to 1"""

    Design_Evaporator_Temperature_or_Brine_Inlet_Temperature: Annotated[float, Field(ge=-70.0, le=40.0)]
    """Required for detailed refrigeration system, not for compressor rack"""

    Average_Refrigerant_Charge_Inventory: Annotated[float, Field(default=0.0)]

    Under_Case_HVAC_Return_Air_Node_Name: Annotated[str, Field()]
    """Name of the return air node for this case."""