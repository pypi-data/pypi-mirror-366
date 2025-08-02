from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Refrigeration_Walkin(EpBunch):
    """Works in conjunction with a compressor rack, a refrigeration system, or a"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Rated_Coil_Cooling_Capacity: Annotated[float, Field(default=...)]

    Operating_Temperature: Annotated[float, Field(default=..., lt=20.0)]

    Rated_Cooling_Source_Temperature: Annotated[float, Field(default=..., ge=-70.0, le=40.)]
    """If DXEvaporator, use evaporating temperature (saturated suction temperature)"""

    Rated_Total_Heating_Power: Annotated[float, Field(default=...)]
    """Include total for all anti-sweat, door, drip-pan, and floor heater power"""

    Heating_Power_Schedule_Name: Annotated[str, Field()]
    """Values will be used to multiply the total heating power"""

    Rated_Cooling_Coil_Fan_Power: Annotated[float, Field(ge=0., default=375.0)]

    Rated_Circulation_Fan_Power: Annotated[float, Field(ge=0.0, default=0.0)]

    Rated_Total_Lighting_Power: Annotated[float, Field(default=...)]
    """Enter the total (display + task) installed lighting power."""

    Lighting_Schedule_Name: Annotated[str, Field()]
    """The schedule should contain values between 0 and 1"""

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

    Restocking_Schedule_Name: Annotated[str, Field()]
    """Schedule values should be in units of Watts"""

    Average_Refrigerant_Charge_Inventory: Annotated[float, Field(default=0.0)]
    """This value is only used if the Cooling Source Type is DXEvaporator"""

    Insulated_Floor_Surface_Area: Annotated[float, Field(default=..., gt=0.0)]
    """floor area of walk-in cooler"""

    Insulated_Floor_UValue: Annotated[float, Field(gt=0.0, default=0.3154)]
    """The default value corresponds to R18 [ft2-F-hr/Btu]"""

    Zone_1_Name: Annotated[str, Field(default=...)]
    """This must be a controlled zone and appear in a ZoneHVAC:EquipmentConnections object."""

    Total_Insulated_Surface_Area_Facing_Zone_1: Annotated[float, Field(default=..., gt=0.0)]
    """Area should include walls and ceilings, but not doors"""

    Insulated_Surface_UValue_Facing_Zone_1: Annotated[float, Field(gt=0.0, default=0.3154)]
    """The default value corresponds to R18 [ft2-F-hr/Btu]"""

    Area_of_Glass_Reach_In_Doors_Facing_Zone_1: Annotated[float, Field(default=0.0)]

    Height_of_Glass_Reach_In_Doors_Facing_Zone_1: Annotated[float, Field(default=1.5)]

    Glass_Reach_In_Door_U_Value_Facing_Zone_1: Annotated[float, Field(gt=0.0, default=1.136)]
    """The default value corresponds to R5 [ft2-F-hr/Btu]"""

    Glass_Reach_In_Door_Opening_Schedule_Name_Facing_Zone_1: Annotated[str, Field()]
    """Schedule values should all be between 0.0 and 1.0."""

    Area_of_Stocking_Doors_Facing_Zone_1: Annotated[float, Field(default=0.0)]

    Height_of_Stocking_Doors_Facing_Zone_1: Annotated[float, Field(default=3.0)]

    Stocking_Door_U_Value_Facing_Zone_1: Annotated[float, Field(gt=0.0, default=0.3785)]
    """The default value corresponds to R15 [ft2-F-hr/Btu]"""

    Stocking_Door_Opening_Schedule_Name_Facing_Zone_1: Annotated[str, Field()]
    """Schedule values should all be between 0.0 and 1.0."""

    Stocking_Door_Opening_Protection_Type_Facing_Zone_1: Annotated[Literal['None', 'AirCurtain', 'StripCurtain'], Field(default='AirCurtain')]
    """Use StripCurtain for hanging strips or airlock vestibules"""

    Zone_2_Name: Annotated[str, Field()]
    """required if more than one zone"""

    Total_Insulated_Surface_Area_Facing_Zone_2: Annotated[float, Field(gt=0.0)]
    """Area should include walls and ceilings, but not doors"""

    Insulated_Surface_UValue_Facing_Zone_2: Annotated[float, Field(gt=0.0, default=0.3154)]
    """The default value corresponds to R18 [ft2-F-hr/Btu]"""

    Area_of_Glass_Reach_In_Doors_Facing_Zone_2: Annotated[float, Field(default=0.0)]

    Height_of_Glass_Reach_In_Doors_Facing_Zone_2: Annotated[float, Field(default=1.5)]

    Glass_Reach_In_Door_U_Value_Facing_Zone_2: Annotated[float, Field(gt=0.0, default=1.136)]
    """The default value corresponds to R5 [ft2-F-hr/Btu]"""

    Glass_Reach_In_Door_Opening_Schedule_Name_Facing_Zone_2: Annotated[str, Field()]
    """Schedule values should all be between 0.0 and 1.0."""

    Area_of_Stocking_Doors_Facing_Zone_2: Annotated[float, Field(default=0.0)]

    Height_of_Stocking_Doors_Facing_Zone_2: Annotated[float, Field(default=3.0)]

    Stocking_Door_U_Value_Facing_Zone_2: Annotated[float, Field(gt=0.0, default=0.3785)]
    """The default value corresponds to R15 [ft2-F-hr/Btu]"""

    Stocking_Door_Opening_Schedule_Name_Facing_Zone_2: Annotated[str, Field()]
    """Schedule values should all be between 0.0 and 1.0."""

    Stocking_Door_Opening_Protection_Type_Facing_Zone_2: Annotated[Literal['None', 'AirCurtain', 'StripCurtain'], Field(default='AirCurtain')]
    """Use StripCurtain for hanging strips or airlock vestibules"""

    Zone_3_Name: Annotated[str, Field()]
    """This must be a controlled zone and appear in a ZoneHVAC:EquipmentConnections object."""

    Total_Insulated_Surface_Area_Facing_Zone_3: Annotated[float, Field(gt=0.0)]
    """required if more than two zones"""

    Insulated_Surface_UValue_Facing_Zone_3: Annotated[float, Field(gt=0.0, default=0.3154)]
    """The default value corresponds to R18 [ft2-F-hr/Btu]"""

    Area_of_Glass_Reach_In_Doors_Facing_Zone_3: Annotated[float, Field(default=0.0)]

    Height_of_Glass_Reach_In_Doors_Facing_Zone_3: Annotated[float, Field(default=1.5)]

    Glass_Reach_In_Door_U_Value_Facing_Zone_3: Annotated[float, Field(gt=0.0, default=1.136)]
    """The default value corresponds to R5 [ft2-F-hr/Btu]"""

    Glass_Reach_In_Door_Opening_Schedule_Name_Facing_Zone_3: Annotated[str, Field()]
    """Schedule values should all be between 0.0 and 1.0."""

    Area_of_Stocking_Doors_Facing_Zone_3: Annotated[float, Field(default=0.0)]

    Height_of_Stocking_Doors_Facing_Zone_3: Annotated[float, Field(default=3.0)]

    Stocking_Door_U_Value_Facing_Zone_3: Annotated[float, Field(gt=0.0, default=0.3785)]
    """The default value corresponds to R15 [ft2-F-hr/Btu]"""

    Stocking_Door_Opening_Schedule_Name_Facing_Zone_3: Annotated[str, Field()]
    """Schedule values should all be between 0.0 and 1.0."""

    Stocking_Door_Opening_Protection_Type_Facing_Zone_3: Annotated[Literal['None', 'AirCurtain', 'StripCurtain'], Field(default='AirCurtain')]
    """Use StripCurtain for hanging strips or airlock vestibules"""