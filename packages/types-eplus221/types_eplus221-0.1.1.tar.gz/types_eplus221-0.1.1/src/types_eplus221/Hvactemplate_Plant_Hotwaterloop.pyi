from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_Plant_Hotwaterloop(EpBunch):
    """Plant loop to serve all HVACTemplate"""

    Name: Annotated[str, Field(default=...)]

    Pump_Schedule_Name: Annotated[str, Field()]
    """If blank, always available"""

    Pump_Control_Type: Annotated[Literal['Intermittent', 'Continuous'], Field(default='Intermittent')]

    Hot_Water_Plant_Operation_Scheme_Type: Annotated[Literal['Default', 'UserDefined'], Field(default='Default')]
    """Default operation type makes all equipment available"""

    Hot_Water_Plant_Equipment_Operation_Schemes_Name: Annotated[str, Field()]
    """Name of a PlantEquipmentOperationSchemes object"""

    Hot_Water_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank if constant setpoint"""

    Hot_Water_Design_Setpoint: Annotated[str, Field(default='82.0')]
    """Used for sizing and as constant setpoint if no Setpoint Schedule Name is specified."""

    Hot_Water_Pump_Configuration: Annotated[Literal['VariableFlow', 'ConstantFlow'], Field(default='ConstantFlow')]
    """VariableFlow - variable flow to boilers and coils, excess bypassed"""

    Hot_Water_Pump_Rated_Head: Annotated[str, Field(default='179352')]
    """Default head is 60 feet H2O"""

    Hot_Water_Setpoint_Reset_Type: Annotated[Literal['None', 'OutdoorAirTemperatureReset'], Field()]
    """Overrides Hot Water Setpoint Schedule Name"""

    Hot_Water_Setpoint_At_Outdoor_Dry_Bulb_Low: Annotated[str, Field(default='82.2')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Hot_Water_Reset_Outdoor_Dry_Bulb_Low: Annotated[str, Field(default='-6.7')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Hot_Water_Setpoint_At_Outdoor_Dry_Bulb_High: Annotated[str, Field(default='65.6')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Hot_Water_Reset_Outdoor_Dry_Bulb_High: Annotated[str, Field(default='10.0')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Hot_Water_Pump_Type: Annotated[Literal['SinglePump', 'PumpPerBoiler', 'TwoHeaderedPumps', 'ThreeHeaderedPumps', 'FourHeaderedPumps', 'FiveHeaderedPumps'], Field(default='SinglePump')]
    """Describes the type of pump configuration used for the hot water loop."""

    Supply_Side_Bypass_Pipe: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """Determines if a supply side bypass pipe is present in the hot water loop."""

    Demand_Side_Bypass_Pipe: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """Determines if a demand side bypass pipe is present in the hot water loop."""

    Fluid_Type: Annotated[Literal['Water', 'EthyleneGlycol30', 'EthyleneGlycol40', 'EthyleneGlycol50', 'EthyleneGlycol60', 'PropyleneGlycol30', 'PropyleneGlycol40', 'PropyleneGlycol50', 'PropyleneGlycol60'], Field(default='Water')]

    Loop_Design_Delta_Temperature: Annotated[str, Field(default='11.0')]
    """The temperature difference used in sizing the loop flow rate."""

    Maximum_Outdoor_Dry_Bulb_Temperature: Annotated[str, Field()]
    """The maximum outdoor dry-bulb temperature that the hot water loops operate."""

    Load_Distribution_Scheme: Annotated[Literal['Optimal', 'SequentialLoad', 'UniformLoad', 'UniformPLR', 'SequentialUniformPLR'], Field(default='SequentialLoad')]