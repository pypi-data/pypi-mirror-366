from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Generator_Internalcombustionengine(EpBunch):
    """This generator model is the empirical model from the Building Loads"""

    Name: Annotated[str, Field(default=...)]

    Rated_Power_Output: Annotated[str, Field()]

    Electric_Circuit_Node_Name: Annotated[str, Field()]

    Minimum_Part_Load_Ratio: Annotated[str, Field()]

    Maximum_Part_Load_Ratio: Annotated[str, Field()]

    Optimum_Part_Load_Ratio: Annotated[str, Field()]

    Shaft_Power_Curve_Name: Annotated[str, Field()]
    """curve = a + b*PLR + c*PLR**2"""

    Jacket_Heat_Recovery_Curve_Name: Annotated[str, Field()]
    """curve = a + b*PLR + c*PLR**2"""

    Lube_Heat_Recovery_Curve_Name: Annotated[str, Field()]
    """curve = a + b*PLR + c*PLR**2"""

    Total_Exhaust_Energy_Curve_Name: Annotated[str, Field()]
    """curve = a + b*PLR + c*PLR**2"""

    Exhaust_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*PLR + c*PLR**2"""

    Coefficient_1_of_UFactor_Times_Area_Curve: Annotated[str, Field()]
    """curve = C1 * Generator Rated Power Output**C2"""

    Coefficient_2_of_UFactor_Times_Area_Curve: Annotated[str, Field()]
    """curve = C1 * Generator Rated Power Output**C2"""

    Maximum_Exhaust_Flow_per_Unit_of_Power_Output: Annotated[str, Field()]

    Design_Minimum_Exhaust_Temperature: Annotated[str, Field()]

    Fuel_Higher_Heating_Value: Annotated[str, Field()]

    Design_Heat_Recovery_Water_Flow_Rate: Annotated[str, Field(default='0.0')]
    """if non-zero, then inlet, outlet nodes must be entered."""

    Heat_Recovery_Inlet_Node_Name: Annotated[str, Field()]

    Heat_Recovery_Outlet_Node_Name: Annotated[str, Field()]

    Fuel_Type: Annotated[Literal['NaturalGas', 'PropaneGas', 'Diesel', 'Gasoline', 'FuelOil#1', 'FuelOil#2', 'OtherFuel1', 'OtherFuel2'], Field(default='Diesel')]

    Heat_Recovery_Maximum_Temperature: Annotated[str, Field(default='80.0')]