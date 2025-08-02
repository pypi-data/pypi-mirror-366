from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Lifecyclecost_Parameters(EpBunch):
    """Provides inputs related to the overall life-cycle analysis. It establishes many of"""

    Name: Annotated[str, Field(default=...)]

    Discounting_Convention: Annotated[Literal['EndOfYear', 'MidYear', 'BeginningOfYear'], Field(default='EndOfYear')]
    """The field specifies if the discounting of future costs should be computed as occurring at the end"""

    Inflation_Approach: Annotated[Literal['ConstantDollar', 'CurrentDollar'], Field(default='ConstantDollar')]
    """This field is used to determine if the analysis should use constant dollars or current dollars"""

    Real_Discount_Rate: Annotated[float, Field()]
    """Enter the real discount rate as a decimal. For a 3% rate enter the value 0.03. This input is"""

    Nominal_Discount_Rate: Annotated[float, Field()]
    """Enter the nominal discount rate as a decimal. For a 5% rate enter the value 0.05. This input"""

    Inflation: Annotated[float, Field()]
    """Enter the rate of inflation for general goods and services as a decimal. For a 2% rate enter"""

    Base_Date_Month: Annotated[Literal['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], Field(default='January')]
    """Enter the month that is the beginning of study period also known as the beginning of the base period."""

    Base_Date_Year: Annotated[int, Field(ge=1900, le=2100)]
    """Enter the four digit year that is the beginning of study period such as 2010. The study period is"""

    Service_Date_Month: Annotated[Literal['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], Field(default='January')]
    """Enter the month that is the beginning of building occupancy. Energy costs computed by EnergyPlus"""

    Service_Date_Year: Annotated[int, Field(ge=1900, le=2100)]
    """Enter the four digit year that is the beginning of occupancy such as 2010."""

    Length_of_Study_Period_in_Years: Annotated[int, Field(ge=1, le=100)]
    """Enter the number of years of the study period. It is the number of years that the study continues"""

    Tax_rate: Annotated[float, Field(ge=0.0)]
    """Enter the overall marginal tax rate for the project costs. This does not include energy or water"""

    Depreciation_Method: Annotated[Literal['ModifiedAcceleratedCostRecoverySystem-3year', 'ModifiedAcceleratedCostRecoverySystem-5year', 'ModifiedAcceleratedCostRecoverySystem-7year', 'ModifiedAcceleratedCostRecoverySystem-10year', 'ModifiedAcceleratedCostRecoverySystem-15year', 'ModifiedAcceleratedCostRecoverySystem-20year', 'StraightLine-27year', 'StraightLine-31year', 'StraightLine-39year', 'StraightLine-40year', 'None'], Field()]
    """For an analysis that includes income tax impacts this entry describes how capital costs are"""