from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Distribution_Component_Duct(EpBunch):
    """This object defines the relationship between pressure and air flow through the duct."""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this object."""

    Duct_Length: Annotated[float, Field(default=..., gt=0.0)]
    """Enter the length of the duct."""

    Hydraulic_Diameter: Annotated[float, Field(default=..., gt=0.0)]
    """Enter the hydraulic diameter of the duct."""

    Cross_Section_Area: Annotated[float, Field(default=..., gt=0.0)]
    """Enter the cross section area of the duct."""

    Surface_Roughness: Annotated[float, Field(gt=0.0, default=0.0009)]
    """Enter the inside surface roughness of the duct."""

    Coefficient_For_Local_Dynamic_Loss_Due_To_Fitting: Annotated[float, Field(ge=0.0, default=0.0)]
    """Enter the coefficient used to calculate dynamic losses of fittings (e.g. elbows)."""

    Heat_Transmittance_Coefficient__U_Factor__For_Duct_Wall_Construction: Annotated[float, Field(gt=0.0, default=0.943)]
    """conduction only"""

    Overall_Moisture_Transmittance_Coefficient_From_Air_To_Air: Annotated[float, Field(gt=0.0, default=0.001)]
    """Enter the overall moisture transmittance coefficient"""

    Outside_Convection_Coefficient: Annotated[float, Field(gt=0.0)]
    """optional. convection coefficient calculated automatically, unless specified"""

    Inside_Convection_Coefficient: Annotated[float, Field(gt=0.0)]
    """optional. convection coefficient calculated automatically, unless specified"""