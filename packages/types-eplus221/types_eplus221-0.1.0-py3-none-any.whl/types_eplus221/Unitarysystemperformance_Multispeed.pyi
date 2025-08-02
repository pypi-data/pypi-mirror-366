from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Unitarysystemperformance_Multispeed(EpBunch):
    """The UnitarySystemPerformance object is used to specify the air flow ratio at each"""

    Name: Annotated[str, Field(default=...)]

    Number_Of_Speeds_For_Heating: Annotated[int, Field(default=..., ge=0, le=10)]
    """Used only for Multi speed coils"""

    Number_Of_Speeds_For_Cooling: Annotated[int, Field(default=..., ge=0, le=10)]
    """Used only for Multi speed coils"""

    Single_Mode_Operation: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Controls coil operation during each HVAC timestep."""

    No_Load_Supply_Air_Flow_Rate_Ratio: Annotated[float, Field(ge=0, le=1, default=1)]
    """Used to define the no load operating air flow rate when the system fan"""

    Heating_Speed_1_Supply_Air_Flow_Ratio: Annotated[float, Field(default=..., gt=0)]
    """Used only for Multi speed coils"""

    Cooling_Speed_1_Supply_Air_Flow_Ratio: Annotated[float, Field(default=..., gt=0)]
    """Used only for Multi speed coils"""

    Heating_Speed_2_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""

    Cooling_Speed_2_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""

    Heating_Speed_3_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""

    Cooling_Speed_3_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""

    Heating_Speed_4_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""

    Cooling_Speed_4_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""

    Heating_Speed_5_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""

    Cooling_Speed_5_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""

    Heating_Speed_6_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""

    Cooling_Speed_6_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""

    Heating_Speed_7_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""

    Cooling_Speed_7_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""

    Heating_Speed_8_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""

    Cooling_Speed_8_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""

    Heating_Speed_9_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""

    Cooling_Speed_9_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""

    Heating_Speed_10_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""

    Cooling_Speed_10_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0)]
    """Used only for Multi speed coils"""