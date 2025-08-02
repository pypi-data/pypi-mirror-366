from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Heating_Watertoairheatpump_Parameterestimation(EpBunch):
    """Direct expansion (DX) heating coil for water-to-air heat pump (includes electric"""

    Name: Annotated[str, Field(default=...)]

    Compressor_Type: Annotated[Literal['Reciprocating', 'Rotary', 'Scroll'], Field(default=...)]
    """Parameters 1-4 are as named below."""

    Refrigerant_Type: Annotated[str, Field(default='R22')]

    Design_Source_Side_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Gross_Rated_Heating_Capacity: Annotated[float, Field(default=..., gt=0.0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    High_Pressure_Cutoff: Annotated[float, Field(default=..., gt=0.0)]

    Low_Pressure_Cutoff: Annotated[float, Field(default=..., ge=0.0)]

    Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Load_Side_Total_Heat_Transfer_Coefficient: Annotated[float, Field(default=..., gt=0.0)]
    """Previously called Parameter 1"""

    Superheat_Temperature_at_the_Evaporator_Outlet: Annotated[float, Field(default=..., gt=0.0)]
    """Previously called Parameter 2"""

    Compressor_Power_Losses: Annotated[float, Field(default=..., gt=0.0)]
    """Accounts for the loss of work due to mechanical and electrical losses in the compressor."""

    Compressor_Efficiency: Annotated[float, Field(default=..., gt=0.0)]
    """Previously called Parameter 4"""

    Compressor_Piston_Displacement: Annotated[float, Field(gt=0.0)]
    """Use when Compressor Type is Reciprocating or Rotary"""

    Compressor_SuctionDischarge_Pressure_Drop: Annotated[float, Field(gt=0.0)]
    """Used when Compressor Type is Rotary or Reciprocating"""

    Compressor_Clearance_Factor: Annotated[float, Field(gt=0.0)]
    """Used when Compressor Type is Reciprocating."""

    Refrigerant_Volume_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Use when Compressor Type is Scroll"""

    Volume_Ratio: Annotated[float, Field(gt=0.0)]
    """Use when Compressor Type is Scroll."""

    Leak_Rate_Coefficient: Annotated[float, Field(ge=0.0)]
    """Use when Compressor Type is Scroll."""

    Source_Side_Heat_Transfer_Coefficient: Annotated[float, Field(ge=0.0)]
    """Use when Source Side Fluid Name is Water"""

    Source_Side_Heat_Transfer_Resistance1: Annotated[float, Field(ge=0.0)]
    """Use when Source Side Fluid Name is an antifreeze"""

    Source_Side_Heat_Transfer_Resistance2: Annotated[float, Field(ge=0.0)]
    """Use when Source Side Fluid Name is an antifreeze"""