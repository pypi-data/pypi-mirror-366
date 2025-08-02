from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Photovoltaicperformance_Equivalentone_Diode(EpBunch):
    """Describes the performance characteristics of Photovoltaic (PV) modules to be modeled"""

    Name: Annotated[str, Field()]

    Cell_type: Annotated[Literal['CrystallineSilicon', 'AmorphousSilicon'], Field()]

    Number_of_Cells_in_Series: Annotated[int, Field(ge=0, default=36)]

    Active_Area: Annotated[float, Field(ge=0.1, default=0.89)]
    """The total power output of the array is determined by the"""

    Transmittance_Absorptance_Product: Annotated[float, Field(ge=0.0, le=1.0, default=0.95)]

    Semiconductor_Bandgap: Annotated[float, Field(ge=0.0, default=1.12)]

    Shunt_Resistance: Annotated[float, Field(ge=0.0, default=1000000.0)]

    Short_Circuit_Current: Annotated[float, Field(ge=0.0, default=6.5)]

    Open_Circuit_Voltage: Annotated[float, Field(ge=0.0, default=21.6)]

    Reference_Temperature: Annotated[float, Field(ge=0.0, default=25)]

    Reference_Insolation: Annotated[float, Field(ge=0.0, default=1000)]

    Module_Current_at_Maximum_Power: Annotated[float, Field(ge=0.0, default=5.9)]
    """Single module current at the maximum power point"""

    Module_Voltage_at_Maximum_Power: Annotated[float, Field(ge=0.0, default=17)]
    """Single module voltage at the maximum power point"""

    Temperature_Coefficient_of_Short_Circuit_Current: Annotated[float, Field(default=0.02)]

    Temperature_Coefficient_of_Open_Circuit_Voltage: Annotated[float, Field(default=-0.079)]

    Nominal_Operating_Cell_Temperature_Test_Ambient_Temperature: Annotated[float, Field(ge=0.0, default=20)]

    Nominal_Operating_Cell_Temperature_Test_Cell_Temperature: Annotated[float, Field(ge=0.0, default=40)]

    Nominal_Operating_Cell_Temperature_Test_Insolation: Annotated[float, Field(ge=0.0, default=800)]

    Module_Heat_Loss_Coefficient: Annotated[float, Field(ge=0.0, default=30)]

    Total_Heat_Capacity: Annotated[float, Field(ge=0.0, default=50000)]