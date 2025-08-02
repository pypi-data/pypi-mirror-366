from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Json(EpBunch):
    """Output from EnergyPlus can be written to JSON format files."""

    Option_Type: Annotated[Literal['TimeSeries', 'TimeSeriesAndTabular'], Field(default=...)]

    Output_JSON: Annotated[Literal['Yes', 'No'], Field(default='Yes')]

    Output_CBOR: Annotated[Literal['Yes', 'No'], Field(default='No')]

    Output_MessagePack: Annotated[Literal['Yes', 'No'], Field(default='No')]