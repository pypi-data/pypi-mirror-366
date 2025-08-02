from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Sizingperiod_Designday(EpBunch):
    """The design day object creates the parameters for the program to create"""

    Name: Annotated[str, Field(default=...)]

    Month: Annotated[int, Field(default=..., ge=1, le=12)]

    Day_of_Month: Annotated[int, Field(default=..., ge=1, le=31)]
    """must be valid for Month field"""

    Day_Type: Annotated[Literal['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Holiday', 'SummerDesignDay', 'WinterDesignDay', 'CustomDay1', 'CustomDay2'], Field(default=...)]
    """Day Type selects the schedules appropriate for this design day"""

    Maximum_DryBulb_Temperature: Annotated[float, Field(ge=-90, le=70)]
    """This field is required when field "Dry-Bulb Temperature Range Modifier Type""""

    Daily_DryBulb_Temperature_Range: Annotated[float, Field(ge=0, default=0)]
    """Must still produce appropriate maximum dry-bulb (within range)"""

    DryBulb_Temperature_Range_Modifier_Type: Annotated[Literal['MultiplierSchedule', 'DifferenceSchedule', 'TemperatureProfileSchedule', 'DefaultMultipliers'], Field(default='DefaultMultipliers')]
    """Type of modifier to the dry-bulb temperature calculated for the timestep"""

    DryBulb_Temperature_Range_Modifier_Day_Schedule_Name: Annotated[str, Field()]
    """Only used when previous field is "MultiplierSchedule", "DifferenceSchedule" or"""

    Humidity_Condition_Type: Annotated[Literal['WetBulb', 'DewPoint', 'HumidityRatio', 'Enthalpy', 'RelativeHumiditySchedule', 'WetBulbProfileMultiplierSchedule', 'WetBulbProfileDifferenceSchedule', 'WetBulbProfileDefaultMultipliers'], Field(default='WetBulb')]
    """values/schedules indicated here and in subsequent fields create the humidity"""

    Wetbulb_or_DewPoint_at_Maximum_DryBulb: Annotated[float, Field()]
    """Wetbulb or dewpoint temperature coincident with the maximum temperature."""

    Humidity_Condition_Day_Schedule_Name: Annotated[str, Field()]
    """Only used when Humidity Condition Type is "RelativeHumiditySchedule","""

    Humidity_Ratio_at_Maximum_DryBulb: Annotated[float, Field()]
    """Humidity ratio coincident with the maximum temperature (constant humidity ratio throughout day)."""

    Enthalpy_at_Maximum_DryBulb: Annotated[float, Field()]
    """Enthalpy coincident with the maximum temperature."""

    Daily_WetBulb_Temperature_Range: Annotated[str, Field()]
    """Required only if Humidity Condition Type = "WetbulbProfileMultiplierSchedule" or"""

    Barometric_Pressure: Annotated[float, Field(ge=31000, le=120000)]
    """This field's value is also checked against the calculated "standard barometric pressure""""

    Wind_Speed: Annotated[float, Field(default=..., ge=0, le=40)]

    Wind_Direction: Annotated[float, Field(default=..., ge=0, le=360)]
    """North=0.0 East=90.0"""

    Rain_Indicator: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Yes is raining (all day), No is not raining"""

    Snow_Indicator: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Yes is Snow on Ground, No is no Snow on Ground"""

    Daylight_Saving_Time_Indicator: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Yes -- use schedules modified for Daylight Saving Time Schedules."""

    Solar_Model_Indicator: Annotated[Literal['ASHRAEClearSky', 'ZhangHuang', 'Schedule', 'ASHRAETau', 'ASHRAETau2017'], Field(default='ASHRAEClearSky')]

    Beam_Solar_Day_Schedule_Name: Annotated[str, Field()]
    """if Solar Model Indicator = Schedule, then beam schedule name (for day)"""

    Diffuse_Solar_Day_Schedule_Name: Annotated[str, Field()]
    """if Solar Model Indicator = Schedule, then diffuse schedule name (for day)"""

    ASHRAE_Clear_Sky_Optical_Depth_for_Beam_Irradiance_taub: Annotated[str, Field(default='0')]
    """Required if Solar Model Indicator = ASHRAETau or ASHRAETau2017"""

    ASHRAE_Clear_Sky_Optical_Depth_for_Diffuse_Irradiance_taud: Annotated[str, Field(default='0')]
    """Required if Solar Model Indicator = ASHRAETau or ASHRAETau2017"""

    Sky_Clearness: Annotated[float, Field(ge=0.0, le=1.2, default=0.0)]
    """Used if Sky Model Indicator = ASHRAEClearSky or ZhangHuang"""