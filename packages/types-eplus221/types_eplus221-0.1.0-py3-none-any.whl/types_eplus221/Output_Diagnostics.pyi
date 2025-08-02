from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Diagnostics(EpBunch):
    """Special keys to produce certain warning messages or effect certain simulation characteristics."""

    Key_1: Annotated[Literal['DisplayAllWarnings', 'DisplayExtraWarnings', 'DisplayUnusedSchedules', 'DisplayUnusedObjects', 'DisplayAdvancedReportVariables', 'DisplayZoneAirHeatBalanceOffBalance', 'DoNotMirrorDetachedShading', 'DoNotMirrorAttachedShading', 'DisplayWeatherMissingDataWarnings', 'ReportDuringWarmup', 'ReportDetailedWarmupConvergence', 'ReportDuringHVACSizingSimulation'], Field()]

    Key_2: Annotated[Literal['DisplayAllWarnings', 'DisplayExtraWarnings', 'DisplayUnusedSchedules', 'DisplayUnusedObjects', 'DisplayAdvancedReportVariables', 'DisplayZoneAirHeatBalanceOffBalance', 'DoNotMirrorDetachedShading', 'DoNotMirrorAttachedShading', 'DisplayWeatherMissingDataWarnings', 'ReportDuringWarmup', 'ReportDetailedWarmupConvergence', 'ReportDuringHVACSizingSimulation'], Field()]