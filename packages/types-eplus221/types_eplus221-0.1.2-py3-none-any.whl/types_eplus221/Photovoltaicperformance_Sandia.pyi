from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Photovoltaicperformance_Sandia(EpBunch):
    """Describes performance input data needed for specific makes and models of production"""

    Name: Annotated[str, Field()]

    Active_Area: Annotated[float, Field(ge=0.0, default=1.0)]
    """(m2, single module)"""

    Number_of_Cells_in_Series: Annotated[int, Field(ge=1, default=1)]

    Number_of_Cells_in_Parallel: Annotated[int, Field(ge=1, default=1)]

    Short_Circuit_Current: Annotated[float, Field()]
    """(Amps)"""

    Open_Circuit_Voltage: Annotated[float, Field()]
    """(Volts)"""

    Current_at_Maximum_Power_Point: Annotated[float, Field()]
    """(Amps)"""

    Voltage_at_Maximum_Power_Point: Annotated[float, Field()]
    """(Volts)"""

    Sandia_Database_Parameter_aIsc: Annotated[float, Field()]
    """(1/degC)"""

    Sandia_Database_Parameter_aImp: Annotated[float, Field()]
    """(1/degC)"""

    Sandia_Database_Parameter_c0: Annotated[float, Field()]

    Sandia_Database_Parameter_c1: Annotated[float, Field()]

    Sandia_Database_Parameter_BVoc0: Annotated[float, Field()]
    """(Volts/degC)"""

    Sandia_Database_Parameter_mBVoc: Annotated[float, Field()]
    """(Volts/degC)"""

    Sandia_Database_Parameter_BVmp0: Annotated[float, Field()]
    """(Volts/degC)"""

    Sandia_Database_Parameter_mBVmp: Annotated[float, Field()]
    """(Volts/degC)"""

    Diode_Factor: Annotated[float, Field()]

    Sandia_Database_Parameter_c2: Annotated[float, Field()]

    Sandia_Database_Parameter_c3: Annotated[float, Field()]

    Sandia_Database_Parameter_a0: Annotated[float, Field()]

    Sandia_Database_Parameter_a1: Annotated[float, Field()]

    Sandia_Database_Parameter_a2: Annotated[float, Field()]

    Sandia_Database_Parameter_a3: Annotated[float, Field()]

    Sandia_Database_Parameter_a4: Annotated[float, Field()]

    Sandia_Database_Parameter_b0: Annotated[float, Field()]

    Sandia_Database_Parameter_b1: Annotated[float, Field()]

    Sandia_Database_Parameter_b2: Annotated[float, Field()]

    Sandia_Database_Parameter_b3: Annotated[float, Field()]

    Sandia_Database_Parameter_b4: Annotated[float, Field()]

    Sandia_Database_Parameter_b5: Annotated[float, Field()]

    Sandia_Database_Parameter_DeltaTc: Annotated[float, Field()]
    """(deg C)"""

    Sandia_Database_Parameter_fd: Annotated[float, Field()]

    Sandia_Database_Parameter_a: Annotated[float, Field()]

    Sandia_Database_Parameter_b: Annotated[float, Field()]

    Sandia_Database_Parameter_c4: Annotated[float, Field()]

    Sandia_Database_Parameter_c5: Annotated[float, Field()]

    Sandia_Database_Parameter_Ix0: Annotated[float, Field()]
    """(Amps)"""

    Sandia_Database_Parameter_Ixx0: Annotated[float, Field()]
    """(Amps)"""

    Sandia_Database_Parameter_c6: Annotated[float, Field()]

    Sandia_Database_Parameter_c7: Annotated[float, Field()]
    """(non-dimensional)"""