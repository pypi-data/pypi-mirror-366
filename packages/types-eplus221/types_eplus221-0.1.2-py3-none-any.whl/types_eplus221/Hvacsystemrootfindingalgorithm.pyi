from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvacsystemrootfindingalgorithm(EpBunch):
    """Specifies a HVAC system solver algorithm to find a root"""

    Algorithm: Annotated[Literal['RegulaFalsi', 'Bisection', 'BisectionThenRegulaFalsi', 'RegulaFalsiThenBisection', 'Alternation'], Field(default='RegulaFalsi')]

    Number_of_Iterations_Before_Algorithm_Switch: Annotated[int, Field(default=5)]
    """This field is used when RegulaFalsiThenBisection or BisectionThenRegulaFalsi is"""