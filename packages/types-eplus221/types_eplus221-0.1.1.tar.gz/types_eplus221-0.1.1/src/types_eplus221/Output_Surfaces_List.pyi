from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Surfaces_List(EpBunch):
    """Produces a report summarizing the details of surfaces in the eio output file."""

    Report_Type: Annotated[Literal['Details', 'Vertices', 'DetailsWithVertices', 'ViewFactorInfo', 'Lines', 'CostInfo', 'DecayCurvesFromComponentLoadsSummary'], Field(default=...)]

    Report_Specifications: Annotated[Literal['IDF'], Field()]
    """(IDF, only for Output:Surfaces:List, Lines report --"""