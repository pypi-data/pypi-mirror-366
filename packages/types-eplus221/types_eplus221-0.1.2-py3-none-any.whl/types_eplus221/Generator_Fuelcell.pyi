from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Generator_Fuelcell(EpBunch):
    """This generator model is the FC model from IEA Annex 42"""

    Name: Annotated[str, Field(default=...)]

    Power_Module_Name: Annotated[str, Field(default=...)]
    """Enter the name of a Generator:FuelCell:PowerModule object."""

    Air_Supply_Name: Annotated[str, Field(default=...)]
    """Enter the name of a Generator:FuelCell:AirSupply object."""

    Fuel_Supply_Name: Annotated[str, Field(default=...)]
    """Enter the name of a Generator:FuelSupply object."""

    Water_Supply_Name: Annotated[str, Field(default=...)]
    """Enter the name of a Generator:FuelCell:WaterSupply object."""

    Auxiliary_Heater_Name: Annotated[str, Field(default=...)]
    """Enter the name of a Generator:FuelCell:AuxiliaryHeater object."""

    Heat_Exchanger_Name: Annotated[str, Field(default=...)]
    """Enter the name of a Generator:FuelCell:ExhaustGasToWaterHeatExchanger object."""

    Electrical_Storage_Name: Annotated[str, Field(default=...)]
    """Enter the name of a Generator:FuelCell:ElectricalStorage object."""

    Inverter_Name: Annotated[str, Field(default=...)]
    """Enter the name of a Generator:FuelCell:Inverter object."""

    Stack_Cooler_Name: Annotated[str, Field()]
    """Enter the name of a Generator:FuelCell:StackCooler object."""