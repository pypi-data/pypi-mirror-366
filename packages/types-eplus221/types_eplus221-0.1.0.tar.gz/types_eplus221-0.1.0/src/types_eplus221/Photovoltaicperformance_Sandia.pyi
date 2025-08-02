from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Photovoltaicperformance_Sandia(EpBunch):
    """Describes performance input data needed for specific makes and models of production"""

    Name: Annotated[str, Field()]

    Active_Area: Annotated[float, Field(ge=0.0, default=1.0)]
    """(m2, single module)"""

    Number_Of_Cells_In_Series: Annotated[int, Field(ge=1, default=1)]

    Number_Of_Cells_In_Parallel: Annotated[int, Field(ge=1, default=1)]

    Short_Circuit_Current: Annotated[float, Field()]
    """(Amps)"""

    Open_Circuit_Voltage: Annotated[float, Field()]
    """(Volts)"""

    Current_At_Maximum_Power_Point: Annotated[float, Field()]
    """(Amps)"""

    Voltage_At_Maximum_Power_Point: Annotated[float, Field()]
    """(Volts)"""

    Sandia_Database_Parameter_Aisc: Annotated[float, Field()]
    """(1/degC)"""

    Sandia_Database_Parameter_Aimp: Annotated[float, Field()]
    """(1/degC)"""

    Sandia_Database_Parameter_C0: Annotated[float, Field()]

    Sandia_Database_Parameter_C1: Annotated[float, Field()]

    Sandia_Database_Parameter_Bvoc0: Annotated[float, Field()]
    """(Volts/degC)"""

    Sandia_Database_Parameter_Mbvoc: Annotated[float, Field()]
    """(Volts/degC)"""

    Sandia_Database_Parameter_Bvmp0: Annotated[float, Field()]
    """(Volts/degC)"""

    Sandia_Database_Parameter_Mbvmp: Annotated[float, Field()]
    """(Volts/degC)"""

    Diode_Factor: Annotated[float, Field()]

    Sandia_Database_Parameter_C2: Annotated[float, Field()]

    Sandia_Database_Parameter_C3: Annotated[float, Field()]

    Sandia_Database_Parameter_A0: Annotated[float, Field()]

    Sandia_Database_Parameter_A1: Annotated[float, Field()]

    Sandia_Database_Parameter_A2: Annotated[float, Field()]

    Sandia_Database_Parameter_A3: Annotated[float, Field()]

    Sandia_Database_Parameter_A4: Annotated[float, Field()]

    Sandia_Database_Parameter_B0: Annotated[float, Field()]

    Sandia_Database_Parameter_B1: Annotated[float, Field()]

    Sandia_Database_Parameter_B2: Annotated[float, Field()]

    Sandia_Database_Parameter_B3: Annotated[float, Field()]

    Sandia_Database_Parameter_B4: Annotated[float, Field()]

    Sandia_Database_Parameter_B5: Annotated[float, Field()]

    Sandia_Database_Parameter_Delta_Tc_: Annotated[float, Field()]
    """(deg C)"""

    Sandia_Database_Parameter_Fd: Annotated[float, Field()]

    Sandia_Database_Parameter_A: Annotated[float, Field()]

    Sandia_Database_Parameter_B: Annotated[float, Field()]

    Sandia_Database_Parameter_C4: Annotated[float, Field()]

    Sandia_Database_Parameter_C5: Annotated[float, Field()]

    Sandia_Database_Parameter_Ix0: Annotated[float, Field()]
    """(Amps)"""

    Sandia_Database_Parameter_Ixx0: Annotated[float, Field()]
    """(Amps)"""

    Sandia_Database_Parameter_C6: Annotated[float, Field()]

    Sandia_Database_Parameter_C7: Annotated[float, Field()]
    """(non-dimensional)"""