from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Heatexchanger_Desiccant_Balancedflow_Performancedatatype1(EpBunch):
    """RTO = B1 + B2*RWI + B3*RTI + B4*(RWI/RTI) + B5*PWI + B6*PTI + B7*(PWI/PTI)"""

    Name: Annotated[str, Field(default=...)]

    Nominal_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Air flow rate at nominal conditions (assumed to be the same for both sides"""

    Nominal_Air_Face_Velocity: Annotated[float, Field(default=..., gt=0.0, le=6.0)]

    Nominal_Electric_Power: Annotated[float, Field(ge=0.0, default=0.0)]
    """Parasitic electric power (e.g., desiccant wheel motor)"""

    Temperature_Equation_Coefficient_1: Annotated[float, Field(default=...)]

    Temperature_Equation_Coefficient_2: Annotated[float, Field(default=...)]

    Temperature_Equation_Coefficient_3: Annotated[float, Field(default=...)]

    Temperature_Equation_Coefficient_4: Annotated[float, Field(default=...)]

    Temperature_Equation_Coefficient_5: Annotated[float, Field(default=...)]

    Temperature_Equation_Coefficient_6: Annotated[float, Field(default=...)]

    Temperature_Equation_Coefficient_7: Annotated[float, Field(default=...)]

    Temperature_Equation_Coefficient_8: Annotated[float, Field(default=...)]

    Minimum_Regeneration_Inlet_Air_Humidity_Ratio_For_Temperature_Equation: Annotated[float, Field(default=..., ge=0.0, le=1.0)]

    Maximum_Regeneration_Inlet_Air_Humidity_Ratio_For_Temperature_Equation: Annotated[float, Field(default=..., ge=0.0, le=1.0)]

    Minimum_Regeneration_Inlet_Air_Temperature_For_Temperature_Equation: Annotated[float, Field(default=...)]

    Maximum_Regeneration_Inlet_Air_Temperature_For_Temperature_Equation: Annotated[float, Field(default=...)]

    Minimum_Process_Inlet_Air_Humidity_Ratio_For_Temperature_Equation: Annotated[float, Field(default=..., ge=0.0, le=1.0)]

    Maximum_Process_Inlet_Air_Humidity_Ratio_For_Temperature_Equation: Annotated[float, Field(default=..., ge=0.0, le=1.0)]

    Minimum_Process_Inlet_Air_Temperature_For_Temperature_Equation: Annotated[float, Field(default=...)]

    Maximum_Process_Inlet_Air_Temperature_For_Temperature_Equation: Annotated[float, Field(default=...)]

    Minimum_Regeneration_Air_Velocity_For_Temperature_Equation: Annotated[float, Field(default=..., gt=0.0)]

    Maximum_Regeneration_Air_Velocity_For_Temperature_Equation: Annotated[float, Field(default=..., gt=0.0)]

    Minimum_Regeneration_Outlet_Air_Temperature_For_Temperature_Equation: Annotated[float, Field(default=...)]

    Maximum_Regeneration_Outlet_Air_Temperature_For_Temperature_Equation: Annotated[float, Field(default=...)]

    Minimum_Regeneration_Inlet_Air_Relative_Humidity_For_Temperature_Equation: Annotated[float, Field(default=..., ge=0.0, le=100.0)]

    Maximum_Regeneration_Inlet_Air_Relative_Humidity_For_Temperature_Equation: Annotated[float, Field(default=..., ge=0.0, le=100.0)]

    Minimum_Process_Inlet_Air_Relative_Humidity_For_Temperature_Equation: Annotated[float, Field(default=..., ge=0.0, le=100.0)]

    Maximum_Process_Inlet_Air_Relative_Humidity_For_Temperature_Equation: Annotated[float, Field(default=..., ge=0.0, le=100.0)]

    Humidity_Ratio_Equation_Coefficient_1: Annotated[float, Field(default=...)]

    Humidity_Ratio_Equation_Coefficient_2: Annotated[float, Field(default=...)]

    Humidity_Ratio_Equation_Coefficient_3: Annotated[float, Field(default=...)]

    Humidity_Ratio_Equation_Coefficient_4: Annotated[float, Field(default=...)]

    Humidity_Ratio_Equation_Coefficient_5: Annotated[float, Field(default=...)]

    Humidity_Ratio_Equation_Coefficient_6: Annotated[float, Field(default=...)]

    Humidity_Ratio_Equation_Coefficient_7: Annotated[float, Field(default=...)]

    Humidity_Ratio_Equation_Coefficient_8: Annotated[float, Field(default=...)]

    Minimum_Regeneration_Inlet_Air_Humidity_Ratio_For_Humidity_Ratio_Equation: Annotated[float, Field(default=..., ge=0.0, le=1.0)]

    Maximum_Regeneration_Inlet_Air_Humidity_Ratio_For_Humidity_Ratio_Equation: Annotated[float, Field(default=..., ge=0.0, le=1.0)]

    Minimum_Regeneration_Inlet_Air_Temperature_For_Humidity_Ratio_Equation: Annotated[float, Field(default=...)]

    Maximum_Regeneration_Inlet_Air_Temperature_For_Humidity_Ratio_Equation: Annotated[float, Field(default=...)]

    Minimum_Process_Inlet_Air_Humidity_Ratio_For_Humidity_Ratio_Equation: Annotated[float, Field(default=..., ge=0.0, le=1.0)]

    Maximum_Process_Inlet_Air_Humidity_Ratio_For_Humidity_Ratio_Equation: Annotated[float, Field(default=..., ge=0.0, le=1.0)]

    Minimum_Process_Inlet_Air_Temperature_For_Humidity_Ratio_Equation: Annotated[float, Field(default=...)]

    Maximum_Process_Inlet_Air_Temperature_For_Humidity_Ratio_Equation: Annotated[float, Field(default=...)]

    Minimum_Regeneration_Air_Velocity_For_Humidity_Ratio_Equation: Annotated[float, Field(default=..., gt=0.0)]

    Maximum_Regeneration_Air_Velocity_For_Humidity_Ratio_Equation: Annotated[float, Field(default=..., gt=0.0)]

    Minimum_Regeneration_Outlet_Air_Humidity_Ratio_For_Humidity_Ratio_Equation: Annotated[float, Field(default=..., ge=0.0, le=1.0)]

    Maximum_Regeneration_Outlet_Air_Humidity_Ratio_For_Humidity_Ratio_Equation: Annotated[float, Field(default=..., ge=0.0, le=1.0)]

    Minimum_Regeneration_Inlet_Air_Relative_Humidity_For_Humidity_Ratio_Equation: Annotated[float, Field(default=..., ge=0.0, le=100.0)]

    Maximum_Regeneration_Inlet_Air_Relative_Humidity_For_Humidity_Ratio_Equation: Annotated[float, Field(default=..., ge=0.0, le=100.0)]

    Minimum_Process_Inlet_Air_Relative_Humidity_For_Humidity_Ratio_Equation: Annotated[float, Field(default=..., ge=0.0, le=100.0)]

    Maximum_Process_Inlet_Air_Relative_Humidity_For_Humidity_Ratio_Equation: Annotated[float, Field(default=..., ge=0.0, le=100.0)]