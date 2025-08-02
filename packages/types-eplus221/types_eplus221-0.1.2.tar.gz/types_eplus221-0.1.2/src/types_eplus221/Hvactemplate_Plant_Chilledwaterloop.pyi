from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_Plant_Chilledwaterloop(EpBunch):
    """Plant and condenser loops to serve all HVACTemplate"""

    Name: Annotated[str, Field(default=...)]

    Pump_Schedule_Name: Annotated[str, Field()]
    """If blank, always available"""

    Pump_Control_Type: Annotated[Literal['Intermittent', 'Continuous'], Field(default='Intermittent')]
    """Applies to both chilled water and condenser loop pumps"""

    Chiller_Plant_Operation_Scheme_Type: Annotated[Literal['Default', 'UserDefined'], Field(default='Default')]
    """Default operation type makes all equipment available"""

    Chiller_Plant_Equipment_Operation_Schemes_Name: Annotated[str, Field()]
    """Name of a PlantEquipmentOperationSchemes object"""

    Chilled_Water_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank if constant setpoint"""

    Chilled_Water_Design_Setpoint: Annotated[str, Field(default='7.22')]
    """Used for sizing and as constant setpoint if no Chilled Water Setpoint Schedule Name is specified."""

    Chilled_Water_Pump_Configuration: Annotated[Literal['ConstantPrimaryNoSecondary', 'VariablePrimaryNoSecondary', 'ConstantPrimaryVariableSecondary'], Field(default='ConstantPrimaryNoSecondary')]
    """VariablePrimaryNoSecondary - variable flow to chillers and coils"""

    Primary_Chilled_Water_Pump_Rated_Head: Annotated[str, Field(default='179352')]
    """default head is 60 feet H2O"""

    Secondary_Chilled_Water_Pump_Rated_Head: Annotated[str, Field(default='179352')]
    """default head is 60 feet H2O"""

    Condenser_Plant_Operation_Scheme_Type: Annotated[Literal['Default', 'UserDefined'], Field(default='Default')]
    """Default operation type makes all equipment available"""

    Condenser_Equipment_Operation_Schemes_Name: Annotated[str, Field()]
    """Name of a CondenserEquipmentOperationSchemes object"""

    Condenser_Water_Temperature_Control_Type: Annotated[Literal['OutdoorWetBulbTemperature', 'SpecifiedSetpoint'], Field()]
    """May be left blank if not serving any water cooled chillers"""

    Condenser_Water_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank if constant setpoint"""

    Condenser_Water_Design_Setpoint: Annotated[str, Field(default='29.4')]
    """Used for sizing and as constant setpoint if no Condenser Water Setpoint Schedule Name is specified."""

    Condenser_Water_Pump_Rated_Head: Annotated[str, Field(default='179352')]
    """May be left blank if not serving any water cooled chillers"""

    Chilled_Water_Setpoint_Reset_Type: Annotated[Literal['None', 'OutdoorAirTemperatureReset'], Field()]
    """Overrides Chilled Water Setpoint Schedule Name"""

    Chilled_Water_Setpoint_at_Outdoor_DryBulb_Low: Annotated[str, Field(default='12.2')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Chilled_Water_Reset_Outdoor_DryBulb_Low: Annotated[str, Field(default='15.6')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Chilled_Water_Setpoint_at_Outdoor_DryBulb_High: Annotated[str, Field(default='6.7')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Chilled_Water_Reset_Outdoor_DryBulb_High: Annotated[str, Field(default='26.7')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Chilled_Water_Primary_Pump_Type: Annotated[Literal['SinglePump', 'PumpPerChiller', 'TwoHeaderedPumps', 'ThreeHeaderedPumps', 'FourHeaderedPumps', 'FiveHeaderedPumps'], Field(default='SinglePump')]
    """Describes the type of pump configuration used for the primary portion of the chilled water loop."""

    Chilled_Water_Secondary_Pump_Type: Annotated[Literal['SinglePump', 'TwoHeaderedPumps', 'ThreeHeaderedPumps', 'FourHeaderedPumps', 'FiveHeaderedPumps'], Field(default='SinglePump')]
    """Describes the type of pump configuration used for the secondary portion of the chilled water loop."""

    Condenser_Water_Pump_Type: Annotated[Literal['SinglePump', 'PumpPerTower', 'TwoHeaderedPumps', 'ThreeHeaderedPumps', 'FourHeaderedPumps', 'FiveHeaderedPumps'], Field(default='SinglePump')]
    """Describes the type of pump configuration used for the condenser water loop."""

    Chilled_Water_Supply_Side_Bypass_Pipe: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """Determines if a supply side bypass pipe is present in the chilled water loop."""

    Chilled_Water_Demand_Side_Bypass_Pipe: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """Determines if a demand side bypass pipe is present in the chilled water loop."""

    Condenser_Water_Supply_Side_Bypass_Pipe: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """Determines if a supply side bypass pipe is present in the condenser water loop."""

    Condenser_Water_Demand_Side_Bypass_Pipe: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """Determines if a demand side bypass pipe is present in the condenser water loop."""

    Fluid_Type: Annotated[Literal['Water', 'EthyleneGlycol30', 'EthyleneGlycol40', 'EthyleneGlycol50', 'EthyleneGlycol60', 'PropyleneGlycol30', 'PropyleneGlycol40', 'PropyleneGlycol50', 'PropyleneGlycol60'], Field(default='Water')]

    Loop_Design_Delta_Temperature: Annotated[str, Field(default='6.67')]
    """The temperature difference used in sizing the loop flow rate."""

    Minimum_Outdoor_Dry_Bulb_Temperature: Annotated[str, Field()]
    """The minimum outdoor dry-bulb temperature that the chilled water loops operate."""

    Chilled_Water_Load_Distribution_Scheme: Annotated[Literal['Optimal', 'SequentialLoad', 'UniformLoad', 'UniformPLR', 'SequentialUniformPLR'], Field(default='SequentialLoad')]

    Condenser_Water_Load_Distribution_Scheme: Annotated[Literal['Optimal', 'SequentialLoad', 'UniformLoad', 'UniformPLR', 'SequentialUniformPLR'], Field(default='SequentialLoad')]