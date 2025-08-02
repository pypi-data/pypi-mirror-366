from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Heatpump_Watertowater_Parameterestimation_Heating(EpBunch):
    """OSU parameter estimation model"""

    Name: Annotated[str, Field(default=...)]

    Source_Side_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Source_Side_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Load_Side_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Load_Side_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Nominal_Cop: Annotated[str, Field()]

    Nominal_Capacity: Annotated[str, Field()]

    Minimum_Part_Load_Ratio: Annotated[str, Field()]

    Maximum_Part_Load_Ratio: Annotated[str, Field()]

    Optimum_Part_Load_Ratio: Annotated[str, Field()]

    Load_Side_Flow_Rate: Annotated[str, Field()]

    Source_Side_Flow_Rate: Annotated[str, Field()]

    Load_Side_Heat_Transfer_Coefficient: Annotated[str, Field()]

    Source_Side_Heat_Transfer_Coefficient: Annotated[str, Field()]

    Piston_Displacement: Annotated[str, Field()]

    Compressor_Clearance_Factor: Annotated[str, Field()]

    Compressor_Suction_And_Discharge_Pressure_Drop: Annotated[str, Field()]

    Superheating: Annotated[str, Field()]

    Constant_Part_Of_Electromechanical_Power_Losses: Annotated[str, Field()]

    Loss_Factor: Annotated[str, Field()]
    """Used to define electromechanical loss that is proportional"""

    High_Pressure_Cut_Off: Annotated[str, Field(default='500000000')]

    Low_Pressure_Cut_Off: Annotated[str, Field(default='0.0')]