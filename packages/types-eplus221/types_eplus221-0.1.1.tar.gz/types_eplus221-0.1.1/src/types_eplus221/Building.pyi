from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Building(EpBunch):
    """Describes parameters that are used during the simulation"""

    Name: Annotated[str, Field()]

    North_Axis: Annotated[float, Field(default=0.0)]
    """degrees from true North"""

    Terrain: Annotated[Literal['Country', 'Suburbs', 'City', 'Ocean', 'Urban'], Field(default='Suburbs')]
    """Country=FlatOpenCountry | Suburbs=CountryTownsSuburbs | City=CityCenter | Ocean=body of water (5km) | Urban=Urban-Industrial-Forest"""

    Loads_Convergence_Tolerance_Value: Annotated[float, Field(gt=0.0, le=.5, default=.04)]
    """Loads Convergence Tolerance Value is a fraction of load"""

    Temperature_Convergence_Tolerance_Value: Annotated[float, Field(gt=0.0, le=.5, default=.4)]

    Solar_Distribution: Annotated[Literal['MinimalShadowing', 'FullExterior', 'FullInteriorAndExterior', 'FullExteriorWithReflections', 'FullInteriorAndExteriorWithReflections'], Field(default='FullExterior')]
    """MinimalShadowing | FullExterior | FullInteriorAndExterior | FullExteriorWithReflections | FullInteriorAndExteriorWithReflections"""

    Maximum_Number_Of_Warmup_Days: Annotated[int, Field(gt=0, default=25)]
    """EnergyPlus will only use as many warmup days as needed to reach convergence tolerance."""

    Minimum_Number_Of_Warmup_Days: Annotated[int, Field(gt=0, default=6)]
    """The minimum number of warmup days that produce enough temperature and flux history"""