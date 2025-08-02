from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Energymanagementsystem_Programcallingmanager(EpBunch):
    """Input EMS program. a program needs a name"""

    Name: Annotated[str, Field(default=...)]
    """no spaces allowed in name"""

    Energyplus_Model_Calling_Point: Annotated[Literal['BeginNewEnvironment', 'AfterNewEnvironmentWarmUpIsComplete', 'BeginZoneTimestepBeforeInitHeatBalance', 'BeginZoneTimestepAfterInitHeatBalance', 'BeginTimestepBeforePredictor', 'AfterPredictorBeforeHVACManagers', 'AfterPredictorAfterHVACManagers', 'InsideHVACSystemIterationLoop', 'EndOfZoneTimestepBeforeZoneReporting', 'EndOfZoneTimestepAfterZoneReporting', 'EndOfSystemTimestepBeforeHVACReporting', 'EndOfSystemTimestepAfterHVACReporting', 'EndOfZoneSizing', 'EndOfSystemSizing', 'AfterComponentInputReadIn', 'UserDefinedComponentModel', 'UnitarySystemSizing'], Field()]

    Program_Name_1: Annotated[str, Field(default=...)]
    """no spaces allowed in name"""

    Program_Name_2: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_3: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_4: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_5: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_6: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_7: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_8: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_9: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_10: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_11: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_12: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_13: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_14: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_15: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_16: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_17: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_18: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_19: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_20: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_21: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_22: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_23: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_24: Annotated[str, Field()]
    """no spaces allowed in name"""

    Program_Name_25: Annotated[str, Field()]
    """no spaces allowed in name"""