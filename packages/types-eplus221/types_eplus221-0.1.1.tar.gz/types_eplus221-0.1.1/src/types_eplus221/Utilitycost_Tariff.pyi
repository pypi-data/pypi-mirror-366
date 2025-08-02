from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Utilitycost_Tariff(EpBunch):
    """Defines the name of a utility cost tariff, the type of tariff, and other details"""

    Name: Annotated[str, Field(default=...)]
    """The name of the tariff. Tariffs are sometimes called rates. The name is used in identifying"""

    Output_Meter_Name: Annotated[str, Field(default=...)]
    """The name of any standard meter or custom meter or but usually set to either Electricity:Facility or Gas:Facility"""

    Conversion_Factor_Choice: Annotated[Literal['UserDefined', 'kWh', 'Therm', 'MMBtu', 'MJ', 'kBtu', 'MCF', 'CCF', 'm3', 'gal', 'kgal'], Field()]
    """A choice that allows several different predefined conversion factors to be used; otherwise user"""

    Energy_Conversion_Factor: Annotated[float, Field()]
    """Is a multiplier used to convert energy into the units specified by the utility in their tariff. If"""

    Demand_Conversion_Factor: Annotated[float, Field()]
    """Is a multiplier used to convert demand into the units specified by the utility in their tariff. If"""

    Time_Of_Use_Period_Schedule_Name: Annotated[str, Field()]
    """The name of the schedule that defines the time-of-use periods that occur each day. The values for the"""

    Season_Schedule_Name: Annotated[str, Field()]
    """The name of a schedule that defines the seasons. The schedule values are: 1 for Winter. 2 for Spring."""

    Month_Schedule_Name: Annotated[str, Field()]
    """The name of the schedule that defines the billing periods of the year. Normally this entry is allowed"""

    Demand_Window_Length: Annotated[Literal['QuarterHour', 'HalfHour', 'FullHour', 'Day', 'Week'], Field()]
    """The determination of demand can vary by utility. Some utilities use the peak instantaneous demand"""

    Monthly_Charge_Or_Variable_Name: Annotated[str, Field()]
    """The fixed monthly service charge that many utilities have. The entry may be numeric and gets added to"""

    Minimum_Monthly_Charge_Or_Variable_Name: Annotated[str, Field()]
    """The minimum total charge for the tariff or if a variable name is entered here its"""

    Real_Time_Pricing_Charge_Schedule_Name: Annotated[str, Field()]
    """Used with real time pricing rates. The name of a schedule that contains the cost of"""

    Customer_Baseline_Load_Schedule_Name: Annotated[str, Field()]
    """Used with real time pricing rates. The name of a schedule that contains the baseline"""

    Group_Name: Annotated[str, Field()]
    """The group name of the tariff such as distribution transmission supplier etc. If more than one tariff"""

    Buy_Or_Sell: Annotated[Literal['BuyFromUtility', 'SellToUtility', 'NetMetering'], Field(default='BuyFromUtility')]
    """Sets whether the tariff is used for buying selling or both to the utility. This"""