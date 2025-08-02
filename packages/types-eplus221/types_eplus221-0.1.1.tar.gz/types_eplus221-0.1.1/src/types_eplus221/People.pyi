from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class People(EpBunch):
    """Sets internal gains and contaminant rates for occupants in the zone."""

    Name: Annotated[str, Field(default=...)]

    Zone_Or_Zonelist_Name: Annotated[str, Field(default=...)]

    Number_Of_People_Schedule_Name: Annotated[str, Field(default=...)]
    """units in schedule should be fraction applied to number of people (0.0 - 1.0)"""

    Number_Of_People_Calculation_Method: Annotated[Literal['People', 'People/Area', 'Area/Person'], Field(default='People')]
    """The entered calculation method is used to create the maximum number of people"""

    Number_Of_People: Annotated[float, Field(ge=0)]

    People_Per_Zone_Floor_Area: Annotated[float, Field(ge=0)]

    Zone_Floor_Area_Per_Person: Annotated[float, Field(ge=0)]

    Fraction_Radiant: Annotated[float, Field(ge=0.0, le=1.0, default=0.3)]
    """This is radiant fraction of the sensible heat released by people in a zone. This value will be"""

    Sensible_Heat_Fraction: Annotated[str, Field(default='autocalculate')]
    """if input, overrides program calculated sensible/latent split"""

    Activity_Level_Schedule_Name: Annotated[str, Field(default=...)]
    """Note that W has to be converted to mets in TC routine"""

    Carbon_Dioxide_Generation_Rate: Annotated[float, Field(ge=0.0, le=3.82E-7, default=3.82E-8)]
    """CO2 generation rate per unit of activity level."""

    Enable_Ashrae_55_Comfort_Warnings: Annotated[Literal['Yes', 'No'], Field(default='No')]

    Mean_Radiant_Temperature_Calculation_Type: Annotated[Literal['ZoneAveraged', 'SurfaceWeighted', 'AngleFactor'], Field(default='ZoneAveraged')]
    """optional (only required for thermal comfort runs)"""

    Surface_Name_Angle_Factor_List_Name: Annotated[str, Field()]
    """optional (only required for runs of thermal comfort models: Fanger, Pierce and KSU)"""

    Work_Efficiency_Schedule_Name: Annotated[str, Field()]
    """units in schedule are 0.0 to 1.0"""

    Clothing_Insulation_Calculation_Method: Annotated[Literal['ClothingInsulationSchedule', 'DynamicClothingModelASHRAE55', 'CalculationMethodSchedule'], Field(default='ClothingInsulationSchedule')]

    Clothing_Insulation_Calculation_Method_Schedule_Name: Annotated[str, Field()]
    """a schedule value of 1 for the Scheduled method, and 2 for the DynamicClothingModelASHRAE55 method"""

    Clothing_Insulation_Schedule_Name: Annotated[str, Field()]
    """use "Clo" from ASHRAE or Thermal Comfort guides"""

    Air_Velocity_Schedule_Name: Annotated[str, Field()]
    """units in the schedule are m/s"""

    Thermal_Comfort_Model_1_Type: Annotated[Literal['Fanger', 'Pierce', 'KSU', 'AdaptiveASH55', 'AdaptiveCEN15251'], Field()]
    """optional (only needed for people thermal comfort results reporting)"""

    Thermal_Comfort_Model_2_Type: Annotated[Literal['Fanger', 'Pierce', 'KSU', 'AdaptiveASH55', 'AdaptiveCEN15251'], Field()]
    """optional (second type of thermal comfort model and results reporting)"""

    Thermal_Comfort_Model_3_Type: Annotated[Literal['Fanger', 'Pierce', 'KSU', 'AdaptiveASH55', 'AdaptiveCEN15251'], Field()]
    """optional (third thermal comfort model and report type)"""

    Thermal_Comfort_Model_4_Type: Annotated[Literal['Fanger', 'Pierce', 'KSU', 'AdaptiveASH55', 'AdaptiveCEN15251'], Field()]
    """optional (fourth thermal comfort model and report type)"""

    Thermal_Comfort_Model_5_Type: Annotated[Literal['Fanger', 'Pierce', 'KSU', 'AdaptiveASH55', 'AdaptiveCEN15251'], Field()]
    """optional (fifth thermal comfort model and report type)"""