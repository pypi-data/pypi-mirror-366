from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_Zone_Baseboardheat(EpBunch):
    """Zone baseboard heating system."""

    Zone_Name: Annotated[str, Field(default=...)]
    """Zone name must match a building zone name"""

    Template_Thermostat_Name: Annotated[str, Field()]
    """Enter the name of a HVACTemplate:Thermostat object."""

    Zone_Heating_Sizing_Factor: Annotated[str, Field()]
    """If blank, value from Sizing:Parameters will be used."""

    Baseboard_Heating_Type: Annotated[Literal['HotWater', 'Electric'], Field(default='HotWater')]

    Baseboard_Heating_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Baseboard_Heating_Capacity: Annotated[str, Field(default='autosize')]

    Dedicated_Outdoor_Air_System_Name: Annotated[str, Field()]
    """Enter the name of an HVACTemplate:System:DedicatedOutdoorAir object if this"""

    Outdoor_Air_Method: Annotated[Literal['Flow/Person', 'Flow/Zone', 'Flow/Area', 'Sum', 'Maximum', 'DetailedSpecification'], Field(default='Flow/Person')]
    """Flow/Person, Flow/Zone, Flow/Area, Sum, and Maximum use the values in the next three"""

    Outdoor_Air_Flow_Rate_Per_Person: Annotated[str, Field(default='0.00944')]
    """Default 0.00944 is 20 cfm per person"""

    Outdoor_Air_Flow_Rate_Per_Zone_Floor_Area: Annotated[str, Field(default='0.0')]
    """This input is used if the field Outdoor Air Method is"""

    Outdoor_Air_Flow_Rate_Per_Zone: Annotated[float, Field(default=0.0)]
    """This input is used if the field Outdoor Air Method is"""

    Design_Specification_Outdoor_Air_Object_Name: Annotated[str, Field()]
    """This field is used only when Outdoor Air Method=DetailedSpecification."""

    Design_Specification_Zone_Air_Distribution_Object_Name: Annotated[str, Field()]
    """This field is used only when Outdoor Air Method=DetailedSpecification."""