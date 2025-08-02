from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Generator_Microchp_Nonnormalizedparameters(EpBunch):
    """This object is referenced by a Generator:MicroCHP object and provides the"""

    Name: Annotated[str, Field()]

    Maximum_Electric_Power: Annotated[str, Field()]

    Minimum_Electric_Power: Annotated[str, Field()]

    Minimum_Cooling_Water_Flow_Rate: Annotated[str, Field()]

    Maximum_Cooling_Water_Temperature: Annotated[str, Field()]

    Electrical_Efficiency_Curve_Name: Annotated[str, Field()]
    """TriQuadratic"""

    Thermal_Efficiency_Curve_Name: Annotated[str, Field()]
    """TriQuadratic"""

    Cooling_Water_Flow_Rate_Mode: Annotated[Literal['PlantControl', 'InternalControl'], Field()]

    Cooling_Water_Flow_Rate_Curve_Name: Annotated[str, Field()]

    Air_Flow_Rate_Curve_Name: Annotated[str, Field()]

    Maximum_Net_Electrical_Power_Rate_Of_Change: Annotated[str, Field()]

    Maximum_Fuel_Flow_Rate_Of_Change: Annotated[str, Field()]

    Heat_Exchanger_U_Factor_Times_Area_Value: Annotated[str, Field()]

    Skin_Loss_U_Factor_Times_Area_Value: Annotated[str, Field()]

    Skin_Loss_Radiative_Fraction: Annotated[float, Field()]

    Aggregated_Thermal_Mass_Of_Energy_Conversion_Portion_Of_Generator: Annotated[str, Field()]

    Aggregated_Thermal_Mass_Of_Heat_Recovery_Portion_Of_Generator: Annotated[str, Field()]

    Standby_Power: Annotated[str, Field()]

    Warm_Up_Mode: Annotated[Literal['NominalEngineTemperature', 'TimeDelay'], Field()]
    """Stirling engines use Nominal Engine Temperature"""

    Warm_Up_Fuel_Flow_Rate_Coefficient: Annotated[str, Field()]

    Nominal_Engine_Operating_Temperature: Annotated[str, Field()]

    Warm_Up_Power_Coefficient: Annotated[str, Field()]

    Warm_Up_Fuel_Flow_Rate_Limit_Ratio: Annotated[str, Field()]

    Warm_Up_Delay_Time: Annotated[str, Field()]

    Cool_Down_Power: Annotated[str, Field()]

    Cool_Down_Delay_Time: Annotated[str, Field()]

    Restart_Mode: Annotated[Literal['MandatoryCoolDown', 'OptionalCoolDown'], Field()]