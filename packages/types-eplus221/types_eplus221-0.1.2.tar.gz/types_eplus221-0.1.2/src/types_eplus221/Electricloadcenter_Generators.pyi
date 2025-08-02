from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Electricloadcenter_Generators(EpBunch):
    """List of electric power generators to include in the simulation including the name and"""

    Name: Annotated[str, Field(default=...)]

    Generator_1_Name: Annotated[str, Field(default=...)]

    Generator_1_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field(default=...)]

    Generator_1_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_1_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_1_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_2_Name: Annotated[str, Field()]

    Generator_2_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_2_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_2_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_2_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_3_Name: Annotated[str, Field()]

    Generator_3_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_3_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_3_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_3_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_4_Name: Annotated[str, Field()]

    Generator_4_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_4_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_4_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_4_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_5_Name: Annotated[str, Field()]

    Generator_5_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_5_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_5_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_5_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_6_Name: Annotated[str, Field()]

    Generator_6_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_6_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_6_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_6_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_7_Name: Annotated[str, Field()]

    Generator_7_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_7_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_7_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_7_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_8_Name: Annotated[str, Field()]

    Generator_8_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_8_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_8_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_8_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_9_Name: Annotated[str, Field()]

    Generator_9_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_9_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_9_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_9_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_10_Name: Annotated[str, Field()]

    Generator_10_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_10_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_10_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_10_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_11_Name: Annotated[str, Field()]

    Generator_11_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_11_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_11_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_11_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_12_Name: Annotated[str, Field()]

    Generator_12_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_12_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_12_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_12_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_13_Name: Annotated[str, Field()]

    Generator_13_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_13_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_13_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_13_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_14_Name: Annotated[str, Field()]

    Generator_14_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_14_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_14_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_14_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_15_Name: Annotated[str, Field()]

    Generator_15_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_15_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_15_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_15_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_16_Name: Annotated[str, Field()]

    Generator_16_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_16_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_16_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_16_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_17_Name: Annotated[str, Field()]

    Generator_17_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_17_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_17_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_17_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_18_Name: Annotated[str, Field()]

    Generator_18_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_18_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_18_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_18_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_19_Name: Annotated[str, Field()]

    Generator_19_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_19_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_19_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_19_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_20_Name: Annotated[str, Field()]

    Generator_20_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_20_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_20_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_20_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_21_Name: Annotated[str, Field()]

    Generator_21_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_21_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_21_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_21_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_22_Name: Annotated[str, Field()]

    Generator_22_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_22_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_22_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_22_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_23_Name: Annotated[str, Field()]

    Generator_23_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_23_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_23_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_23_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_24_Name: Annotated[str, Field()]

    Generator_24_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_24_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_24_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_24_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_25_Name: Annotated[str, Field()]

    Generator_25_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_25_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_25_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_25_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_26_Name: Annotated[str, Field()]

    Generator_26_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_26_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_26_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_26_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_27_Name: Annotated[str, Field()]

    Generator_27_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_27_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_27_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_27_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_28_Name: Annotated[str, Field()]

    Generator_28_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_28_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_28_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_28_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_29_Name: Annotated[str, Field()]

    Generator_29_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_29_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_29_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_29_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""

    Generator_30_Name: Annotated[str, Field()]

    Generator_30_Object_Type: Annotated[Literal['Generator:InternalCombustionEngine', 'Generator:CombustionTurbine', 'Generator:Photovoltaic', 'Generator:PVWatts', 'Generator:FuelCell', 'Generator:MicroCHP', 'Generator:MicroTurbine', 'Generator:WindTurbine'], Field()]

    Generator_30_Rated_Electric_Power_Output: Annotated[float, Field()]

    Generator_30_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this generator. Schedule value > 0 means the generator is available."""

    Generator_30_Rated_Thermal_to_Electrical_Power_Ratio: Annotated[float, Field()]
    """Required field when generator is used by an ElectricLoadCenter:Distribution object with Generator Operation Scheme set to FollowThermal or FollowThermalLimitElectrical"""