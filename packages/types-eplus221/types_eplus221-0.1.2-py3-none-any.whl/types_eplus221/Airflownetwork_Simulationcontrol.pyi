from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Simulationcontrol(EpBunch):
    """This object defines the global parameters used in an Airflow Network simulation."""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this object."""

    AirflowNetwork_Control: Annotated[Literal['MultizoneWithDistribution', 'MultizoneWithoutDistribution', 'MultizoneWithDistributionOnlyDuringFanOperation', 'NoMultizoneOrDistribution'], Field(default='NoMultizoneOrDistribution')]
    """NoMultizoneOrDistribution: Only perform Simple calculations (objects ZoneInfiltration:*,"""

    Wind_Pressure_Coefficient_Type: Annotated[Literal['Input', 'SurfaceAverageCalculation'], Field(default='SurfaceAverageCalculation')]
    """Input: User must enter AirflowNetwork:MultiZone:WindPressureCoefficientArray,"""

    Height_Selection_for_Local_Wind_Pressure_Calculation: Annotated[Literal['ExternalNode', 'OpeningHeight'], Field(default='OpeningHeight')]
    """If ExternalNode is selected, the height given in the"""

    Building_Type: Annotated[Literal['LowRise', 'HighRise'], Field(default='LowRise')]
    """Used only if Wind Pressure Coefficient Type = SurfaceAverageCalculation,"""

    Maximum_Number_of_Iterations: Annotated[int, Field(gt=10, le=30000, default=500)]
    """Determines the maximum number of iterations used to converge on a solution. If this limit"""

    Initialization_Type: Annotated[Literal['LinearInitializationMethod', 'ZeroNodePressures'], Field(default='ZeroNodePressures')]

    Relative_Airflow_Convergence_Tolerance: Annotated[float, Field(gt=0, default=1.E-4)]
    """This tolerance is defined as the absolute value of the sum of the mass Flow Rates"""

    Absolute_Airflow_Convergence_Tolerance: Annotated[float, Field(gt=0, default=1.E-6)]
    """This tolerance is defined as the absolute value of the sum of the mass flow rates. The mass"""

    Convergence_Acceleration_Limit: Annotated[float, Field(ge=-1, le=1, default=-0.5)]
    """Used only for AirflowNetwork:SimulationControl"""

    Azimuth_Angle_of_Long_Axis_of_Building: Annotated[float, Field(ge=0.0, le=180.0, default=0.0)]
    """Degrees clockwise from true North."""

    Ratio_of_Building_Width_Along_Short_Axis_to_Width_Along_Long_Axis: Annotated[float, Field(gt=0.0, le=1.0, default=1.0)]
    """Used only if Wind Pressure Coefficient Type = SurfaceAverageCalculation."""

    Height_Dependence_of_External_Node_Temperature: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """If Yes, external node temperature is height dependent."""

    Solver: Annotated[Literal['SkylineLU', 'ConjugateGradient'], Field(default='SkylineLU')]
    """Select the solver to use for the pressure network solution"""