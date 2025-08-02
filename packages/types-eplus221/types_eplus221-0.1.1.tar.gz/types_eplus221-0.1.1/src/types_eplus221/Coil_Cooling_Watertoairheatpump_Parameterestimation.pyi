from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Cooling_Watertoairheatpump_Parameterestimation(EpBunch):
    """Direct expansion (DX) cooling coil for water-to-air heat pump (includes electric"""

    Name: Annotated[str, Field(default=...)]

    Compressor_Type: Annotated[Literal['Reciprocating', 'Rotary', 'Scroll'], Field(default=...)]
    """Parameters 1-5 are as named below."""

    Refrigerant_Type: Annotated[str, Field(default='R22')]

    Design_Source_Side_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Nominal_Cooling_Coil_Capacity: Annotated[float, Field(default=..., gt=0.0)]

    Nominal_Time_For_Condensate_Removal_To_Begin: Annotated[float, Field(ge=0.0, le=3000.0, default=0.0)]
    """The nominal time for condensate to begin leaving the coil's condensate"""

    Ratio_Of_Initial_Moisture_Evaporation_Rate_And_Steady_State_Latent_Capacity: Annotated[float, Field(ge=0.0, le=5.0, default=0.0)]
    """Ratio of the initial moisture evaporation rate from the cooling coil (when"""

    High_Pressure_Cutoff: Annotated[str, Field(default=...)]

    Low_Pressure_Cutoff: Annotated[float, Field(default=..., ge=0.0)]

    Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Load_Side_Total_Heat_Transfer_Coefficient: Annotated[float, Field(default=..., gt=0.0)]
    """Previously called Parameter 1"""

    Load_Side_Outside_Surface_Heat_Transfer_Coefficient: Annotated[float, Field(default=..., gt=0.0)]
    """Previously called Parameter 2"""

    Superheat_Temperature_At_The_Evaporator_Outlet: Annotated[float, Field(default=..., gt=0.0)]
    """Previously called Parameter 3"""

    Compressor_Power_Losses: Annotated[float, Field(default=..., gt=0.0)]
    """Accounts for the loss of work due to mechanical and electrical losses in the compressor."""

    Compressor_Efficiency: Annotated[float, Field(default=..., gt=0.0)]
    """Previously called Parameter 5"""

    Compressor_Piston_Displacement: Annotated[float, Field(gt=0.0)]
    """Use when Compressor Type is Reciprocating or Rotary"""

    Compressor_Suction_Discharge_Pressure_Drop: Annotated[float, Field(gt=0.0)]
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