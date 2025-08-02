from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Refrigeration_Secondarysystem(EpBunch):
    """Works in conjunction with refrigerated cases and walkins to simulate the performance"""

    Name: Annotated[str, Field(default=...)]

    Refrigerated_Case_or_Walkin_or_CaseAndWalkInList_Name: Annotated[str, Field(default=...)]
    """Enter the name of a Refrigeration:Case or Refrigeration:WalkIn object."""

    Circulating_Fluid_Type: Annotated[Literal['FluidAlwaysLiquid', 'FluidPhaseChange'], Field(default=...)]
    """If "FluidAlwaysLiquid" is selected, the fluid properties"""

    Circulating_Fluid_Name: Annotated[str, Field(default=...)]
    """This must correspond to a name in the FluidProperties:Name object."""

    Evaporator_Capacity: Annotated[float, Field(ge=0.0)]
    """For "FluidAlwaysLiquid", at least one of the two, Evaporator Capacity OR"""

    Evaporator_Flow_Rate_for_Secondary_Fluid: Annotated[float, Field(ge=0.0)]
    """For "FluidAlwaysLiquid", at least one of the two, Evaporator Capacity OR"""

    Evaporator_Evaporating_Temperature: Annotated[float, Field(default=...)]
    """This is the evaporating temperature in the heat exchanger"""

    Evaporator_Approach_Temperature_Difference: Annotated[float, Field(default=...)]
    """For "FluidAlwaysLiquid", this is the rated difference between the temperature of the"""

    Evaporator_Range_Temperature_Difference: Annotated[float, Field()]
    """For "FluidAlwaysLiquid", this is the rated difference between the temperature of the"""

    Number_of_Pumps_in_Loop: Annotated[int, Field(default=1)]

    Total_Pump_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """For "FluidAlwaysLiquid",if not input, Evaporator Flow Rate for Secondary Fluid"""

    Total_Pump_Power: Annotated[float, Field(ge=0.0)]
    """Either the Total Pump Power or the Total Pump Head is required."""

    Total_Pump_Head: Annotated[float, Field(ge=0.0)]
    """Either the Total Pump Power or the Total Pump Head is required."""

    PhaseChange_Circulating_Rate: Annotated[float, Field(ge=1.0, default=2.5)]
    """This is the total mass flow at the pump divided by the gaseous mass flow"""

    Pump_Drive_Type: Annotated[Literal['Constant', 'Variable'], Field(default='Constant')]

    Variable_Speed_Pump_Cubic_Curve_Name: Annotated[str, Field()]
    """Variable Speed Pump Curve Name is applicable to variable speed pumps"""

    Pump_Motor_Heat_to_Fluid: Annotated[float, Field(ge=0.5, le=1.0, default=0.85)]
    """This is the portion of the pump motor heat added to secondary circulating fluid"""

    Sum_UA_Distribution_Piping: Annotated[float, Field(default=0.0)]
    """Use only if you want to include distribution piping heat gain in refrigeration load."""

    Distribution_Piping_Zone_Name: Annotated[str, Field()]
    """This will be used to determine the temperature used for distribution piping heat gain."""

    Sum_UA_ReceiverSeparator_Shell: Annotated[float, Field(default=0.0)]
    """Use only if you want to include Receiver/Separator Shell heat gain in refrigeration load."""

    ReceiverSeparator_Zone_Name: Annotated[str, Field()]
    """This will be used to determine the temperature used for Receiver/Separator Shell heat gain."""

    Evaporator_Refrigerant_Inventory: Annotated[float, Field(default=0.0)]
    """This value refers to the refrigerant circulating within the primary system providing"""

    EndUse_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""