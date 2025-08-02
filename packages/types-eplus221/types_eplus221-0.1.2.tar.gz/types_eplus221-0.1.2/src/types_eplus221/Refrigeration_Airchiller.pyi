from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Refrigeration_Airchiller(EpBunch):
    """Works in conjunction with a refrigeration chiller set, compressor rack, a"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Capacity_Rating_Type: Annotated[Literal['UnitLoadFactorSensibleOnly', 'CapacityTotalSpecificConditions', 'EuropeanSC1Standard', 'EuropeanSC1NominalWet', 'EuropeanSC2Standard', 'EuropeanSC2NominalWet', 'EuropeanSC3Standard', 'FixedLinear', 'EuropeanSC3NominalWet', 'EuropeanSC4Standard', 'EuropeanSC4NominalWet', 'EuropeanSC5Standard', 'EuropeanSC5NominalWet'], Field(default=...)]
    """In each case, select the rating option that corresponds to the expected service conditions."""

    Rated_Unit_Load_Factor: Annotated[float, Field()]
    """The sensible cooling capacity in watts (W/C) at rated conditions."""

    Rated_Capacity: Annotated[float, Field()]
    """This value is only used if the Capacity Rating Type is NOT UnitLoadFactorSensibleOnly."""

    Rated_Relative_Humidity: Annotated[float, Field(le=100, default=85)]
    """This field is ONLY used if the Capacity Rating Type is CapacityTotalSpecificConditions and"""

    Rated_Cooling_Source_Temperature: Annotated[float, Field(default=..., ge=-70.0, le=40.)]
    """If DXEvaporator, use evaporating temperature (saturated suction temperature)"""

    Rated_Temperature_Difference_DT1: Annotated[float, Field(default=..., ge=0.0, le=20.)]
    """The rated difference between the air entering the refrigeration chiller and the"""

    Maximum_Temperature_Difference_Between_Inlet_Air_and_Evaporating_Temperature: Annotated[float, Field(ge=0.0, le=25.)]
    """The maximum difference between the air entering the refrigeration chiller and the"""

    Coil_Material_Correction_Factor: Annotated[float, Field(default=1.0)]
    """This is the manufacturer's correction factor for coil material corresponding to rating"""

    Refrigerant_Correction_Factor: Annotated[float, Field(default=1.0)]
    """This is the manufacturer's correction factor for refrigerant corresponding to rating"""

    Capacity_Correction_Curve_Type: Annotated[Literal['LinearSHR60', 'QuadraticSHR', 'European', 'TabularRHxDT1xTRoom'], Field()]
    """In each case, select the correction curve type that corresponds to the rating type."""

    Capacity_Correction_Curve_Name: Annotated[str, Field()]
    """Should be blank for LinearSHR60 correction curve type"""

    SHR60_Correction_Factor: Annotated[float, Field(le=1.67, default=1.48)]
    """only used when the capacity correction curve type is LinearSHR60"""

    Rated_Total_Heating_Power: Annotated[float, Field(default=...)]
    """Include total for all heater power"""

    Heating_Power_Schedule_Name: Annotated[str, Field()]
    """Values will be used to multiply the total heating power"""

    Fan_Speed_Control_Type: Annotated[Literal['Fixed', 'FixedLinear', 'VariableSpeed', 'TwoSpeed'], Field(default='Fixed')]

    Rated_Fan_Power: Annotated[float, Field(ge=0., default=375.0)]

    Rated_Air_Flow: Annotated[float, Field(default=...)]

    Minimum_Fan_Air_Flow_Ratio: Annotated[float, Field(ge=0.0, default=0.2)]
    """Minimum air flow fraction through fan"""

    Defrost_Type: Annotated[Literal['HotFluid', 'Electric', 'None', 'OffCycle'], Field(default='Electric')]
    """HotFluid includes either hot gas defrost for a DX system or"""

    Defrost_Control_Type: Annotated[Literal['TimeSchedule', 'TemperatureTermination'], Field(default='TimeSchedule')]

    Defrost_Schedule_Name: Annotated[str, Field(default=...)]
    """The schedule values should be 0 (off) or 1 (on)"""

    Defrost_DripDown_Schedule_Name: Annotated[str, Field()]
    """The schedule values should be 0 (off) or 1 (on)"""

    Defrost_Power: Annotated[float, Field(ge=0.0)]
    """needed for all defrost types except none and offcycle"""

    Temperature_Termination_Defrost_Fraction_to_Ice: Annotated[float, Field(gt=0.0, le=1.0)]
    """This is the portion of the defrost energy that is available to melt frost"""

    Vertical_Location: Annotated[Literal['Ceiling', 'Middle', 'Floor'], Field(default='Middle')]

    Average_Refrigerant_Charge_Inventory: Annotated[float, Field(default=0.0)]
    """This value is only used if the Cooling Source Type is DXEvaporator"""