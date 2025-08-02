from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Electricloadcenter_Distribution(EpBunch):
    """Describes a subpanel"""

    Name: Annotated[str, Field(default=...)]

    Generator_List_Name: Annotated[str, Field()]
    """Name of an ElectricLoadCenter:Generators object"""

    Generator_Operation_Scheme_Type: Annotated[Literal['Baseload', 'DemandLimit', 'TrackElectrical', 'TrackSchedule', 'TrackMeter', 'FollowThermal', 'FollowThermalLimitElectrical'], Field()]
    """Determines how generators are to be controlled"""

    Generator_Demand_Limit_Scheme_Purchased_Electric_Demand_Limit: Annotated[float, Field()]

    Generator_Track_Schedule_Name_Scheme_Schedule_Name: Annotated[str, Field()]
    """required when Generator Operation Scheme Type=TrackSchedule"""

    Generator_Track_Meter_Scheme_Meter_Name: Annotated[str, Field()]
    """required when Generator Operation Scheme Type=TrackMeter"""

    Electrical_Buss_Type: Annotated[Literal['AlternatingCurrent', 'AlternatingCurrentWithStorage', 'DirectCurrentWithInverter', 'DirectCurrentWithInverterDCStorage', 'DirectCurrentWithInverterACStorage'], Field(default='AlternatingCurrent')]

    Inverter_Name: Annotated[str, Field()]
    """required when Electrical Buss Type=DirectCurrentWithInverter, DirectCurrentWithInverterDCStorage,"""

    Electrical_Storage_Object_Name: Annotated[str, Field()]
    """required when Electrical Buss Type=AlternatingCurrentWithStorage, DirectCurrentWithInverterDCStorage,"""

    Transformer_Object_Name: Annotated[str, Field()]
    """required when power needs to be output from on-site generation or storage to the grid via transformer"""

    Storage_Operation_Scheme: Annotated[Literal['TrackFacilityElectricDemandStoreExcessOnSite', 'TrackMeterDemandStoreExcessOnSite', 'TrackChargeDischargeSchedules', 'FacilityDemandLeveling'], Field(default='TrackFacilityElectricDemandStoreExcessOnSite')]
    """Select method to govern how storage charge and discharge is controlled"""

    Storage_Control_Track_Meter_Name: Annotated[str, Field()]
    """required when Storage Operation Scheme is set to TrackMeterDemandStoreExcessOnSite."""

    Storage_Converter_Object_Name: Annotated[str, Field()]
    """Name of an ElectricLoadCenter:Storage:Converter used to convert AC to DC when charging DC storage from grid supply."""

    Maximum_Storage_State_of_Charge_Fraction: Annotated[float, Field(default=1.0)]
    """Fraction of storage capacity used as upper limit for controlling charging, for all storage operation schemes."""

    Minimum_Storage_State_of_Charge_Fraction: Annotated[float, Field(default=0.0)]
    """Fraction of storage capacity used as lower limit for controlling discharging, for all storage operation schemes."""

    Design_Storage_Control_Charge_Power: Annotated[float, Field()]
    """Maximum rate that electric power can be charged into storage."""

    Storage_Charge_Power_Fraction_Schedule_Name: Annotated[str, Field()]
    """Controls timing and magnitude of charging storage."""

    Design_Storage_Control_Discharge_Power: Annotated[float, Field()]
    """Maximum rate that electric power can be discharged from storage."""

    Storage_Discharge_Power_Fraction_Schedule_Name: Annotated[str, Field()]
    """Controls timing and magnitude of discharging storage"""

    Storage_Control_Utility_Demand_Target: Annotated[float, Field()]
    """Target utility service demand power for discharge control. Storage draws are adjusted upwards for conversion losses."""

    Storage_Control_Utility_Demand_Target_Fraction_Schedule_Name: Annotated[str, Field()]
    """Modifies the target utility service demand power over time."""