from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_Plant_Mixedwaterloop(EpBunch):
    """Central plant loop portion of a water source heat pump system."""

    Name: Annotated[str, Field(default=...)]

    Pump_Schedule_Name: Annotated[str, Field()]
    """If blank, always available"""

    Pump_Control_Type: Annotated[Literal['Intermittent', 'Continuous'], Field(default='Intermittent')]
    """Applies to both chilled water and condenser loop pumps"""

    Operation_Scheme_Type: Annotated[Literal['Default', 'UserDefined'], Field(default='Default')]
    """Default operation type makes all equipment available"""

    Equipment_Operation_Schemes_Name: Annotated[str, Field()]
    """Name of a PlantEquipmentOperationSchemes object"""

    High_Temperature_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank if constant setpoint"""

    High_Temperature_Design_Setpoint: Annotated[str, Field(default='33.0')]
    """Used for sizing and as constant setpoint if no Setpoint Schedule Name is specified."""

    Low_Temperature_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank if constant setpoint"""

    Low_Temperature_Design_Setpoint: Annotated[str, Field(default='20.0')]
    """Used for sizing and as constant setpoint if no Condenser Water Setpoint Schedule Name is specified."""

    Water_Pump_Configuration: Annotated[Literal['VariableFlow', 'ConstantFlow'], Field(default='ConstantFlow')]
    """VariableFlow - variable flow to boilers and coils, excess bypassed"""

    Water_Pump_Rated_Head: Annotated[str, Field(default='179352')]
    """May be left blank if not serving any water cooled chillers"""

    Water_Pump_Type: Annotated[Literal['SinglePump', 'PumpPerTowerOrBoiler', 'TwoHeaderedPumps', 'ThreeHeaderedPumps', 'FourHeaderedPumps', 'FiveHeaderedPumps'], Field(default='SinglePump')]
    """Describes the type of pump configuration used for the mixed water loop."""

    Supply_Side_Bypass_Pipe: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """Determines if a supply side bypass pipe is present in the hot water loop."""

    Demand_Side_Bypass_Pipe: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """Determines if a demand side bypass pipe is present in the hot water loop."""

    Fluid_Type: Annotated[Literal['Water', 'EthyleneGlycol30', 'EthyleneGlycol40', 'EthyleneGlycol50', 'EthyleneGlycol60', 'PropyleneGlycol30', 'PropyleneGlycol40', 'PropyleneGlycol50', 'PropyleneGlycol60'], Field(default='Water')]

    Loop_Design_Delta_Temperature: Annotated[str, Field(default='5.6')]
    """The temperature difference used in sizing the loop flow rate."""

    Load_Distribution_Scheme: Annotated[Literal['Optimal', 'SequentialLoad', 'UniformLoad', 'UniformPLR', 'SequentialUniformPLR'], Field(default='SequentialLoad')]