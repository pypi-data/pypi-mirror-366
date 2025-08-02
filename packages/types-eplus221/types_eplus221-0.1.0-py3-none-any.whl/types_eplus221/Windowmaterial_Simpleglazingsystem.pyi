from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowmaterial_Simpleglazingsystem(EpBunch):
    """Alternate method of describing windows"""

    Name: Annotated[str, Field(default=...)]

    U_Factor: Annotated[str, Field(default=...)]
    """Enter U-Factor including film coefficients"""

    Solar_Heat_Gain_Coefficient: Annotated[str, Field(default=...)]
    """SHGC at Normal Incidence"""

    Visible_Transmittance: Annotated[str, Field()]
    """VT at Normal Incidence"""