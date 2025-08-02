from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Externalinterface_Functionalmockupunitimport(EpBunch):
    """This object declares an FMU"""

    FMU_File_Name: Annotated[str, Field(default=...)]

    FMU_Timeout: Annotated[float, Field(default=0.0)]
    """in milli-seconds"""

    FMU_LoggingOn: Annotated[int, Field(default=0)]