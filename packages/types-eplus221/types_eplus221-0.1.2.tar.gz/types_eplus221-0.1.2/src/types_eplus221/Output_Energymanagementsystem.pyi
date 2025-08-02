from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Energymanagementsystem(EpBunch):
    """This object is used to control the output produced by the Energy Management System"""

    Actuator_Availability_Dictionary_Reporting: Annotated[Literal['None', 'NotByUniqueKeyNames', 'Verbose'], Field()]

    Internal_Variable_Availability_Dictionary_Reporting: Annotated[Literal['None', 'NotByUniqueKeyNames', 'Verbose'], Field()]

    EMS_Runtime_Language_Debug_Output_Level: Annotated[Literal['None', 'ErrorsOnly', 'Verbose'], Field()]