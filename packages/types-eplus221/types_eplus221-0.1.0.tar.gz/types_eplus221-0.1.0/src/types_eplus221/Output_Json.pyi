from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Json(EpBunch):
    """Output from EnergyPlus can be written to JSON format files."""

    Option_Type: Annotated[Literal['TimeSeries', 'TimeSeriesAndTabular'], Field(default=...)]

    Output_Json: Annotated[Literal['Yes', 'No'], Field(default='Yes')]

    Output_Cbor: Annotated[Literal['Yes', 'No'], Field(default='No')]

    Output_Messagepack: Annotated[Literal['Yes', 'No'], Field(default='No')]