from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Table_Independentvariable(EpBunch):
    """An independent variable representing a single dimension of a Table:Lookup"""

    Name: Annotated[str, Field(default=...)]

    Interpolation_Method: Annotated[Literal['Linear', 'Cubic'], Field(default='Linear')]

    Extrapolation_Method: Annotated[Literal['Constant', 'Linear'], Field(default='Constant')]

    Minimum_Value: Annotated[float, Field()]

    Maximum_Value: Annotated[float, Field()]

    Normalization_Reference_Value: Annotated[float, Field()]

    Unit_Type: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance', 'Angle'], Field(default='Dimensionless')]

    External_File_Name: Annotated[str, Field()]

    External_File_Column_Number: Annotated[int, Field(ge=1)]

    External_File_Starting_Row_Number: Annotated[int, Field(ge=1)]

    Value_1: Annotated[float, Field()]

    Value_2: Annotated[float, Field()]

    Value_3: Annotated[float, Field()]

    Value_4: Annotated[float, Field()]

    Value_5: Annotated[float, Field()]

    Value_6: Annotated[float, Field()]

    Value_7: Annotated[float, Field()]

    Value_8: Annotated[float, Field()]

    Value_9: Annotated[float, Field()]

    Value_10: Annotated[float, Field()]

    Value_11: Annotated[float, Field()]

    Value_12: Annotated[float, Field()]

    Value_13: Annotated[float, Field()]

    Value_14: Annotated[float, Field()]

    Value_15: Annotated[float, Field()]