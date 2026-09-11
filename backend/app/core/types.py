from typing import Annotated

from pydantic import Field

HexColor = Annotated[
    str,
    Field(
        min_length=7,
        max_length=7,
        pattern=r"^#[0-9a-fA-F]{6}$",
        description="HEX color code (e.g., #FFFFFF)",
        examples=["#ffffff"],
    ),
]
