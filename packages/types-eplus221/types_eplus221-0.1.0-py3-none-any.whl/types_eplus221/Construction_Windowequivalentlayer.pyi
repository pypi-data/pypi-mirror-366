from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Construction_Windowequivalentlayer(EpBunch):
    """Start with outside layer and work your way to the inside Layer"""

    Name: Annotated[str, Field(default=...)]

    Outside_Layer: Annotated[str, Field(default=...)]

    Layer_2: Annotated[str, Field()]

    Layer_3: Annotated[str, Field()]

    Layer_4: Annotated[str, Field()]

    Layer_5: Annotated[str, Field()]

    Layer_6: Annotated[str, Field()]

    Layer_7: Annotated[str, Field()]

    Layer_8: Annotated[str, Field()]

    Layer_9: Annotated[str, Field()]

    Layer_10: Annotated[str, Field()]

    Layer_11: Annotated[str, Field()]