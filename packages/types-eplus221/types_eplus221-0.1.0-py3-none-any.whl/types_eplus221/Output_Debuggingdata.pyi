from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Debuggingdata(EpBunch):
    """switch eplusout.dbg file on or off"""

    Report_Debugging_Data: Annotated[str, Field()]
    """value=1 then yes all others no"""

    Report_During_Warmup: Annotated[str, Field()]
    """value=1 then always even during warmup all others no"""