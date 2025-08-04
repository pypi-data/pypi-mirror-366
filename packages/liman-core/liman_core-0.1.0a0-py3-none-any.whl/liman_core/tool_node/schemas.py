from typing import Literal

from pydantic import BaseModel

from liman_core.base import BaseSpec
from liman_core.languages import LocalizedValue


class ToolArgument(BaseModel):
    name: str
    type: str
    description: LocalizedValue
    optional: bool = False


class ToolNodeSpec(BaseSpec):
    kind: Literal["ToolNode"] = "ToolNode"
    name: str
    description: LocalizedValue

    func: str | None = None
    arguments: list[ToolArgument] | None = None
    triggers: list[LocalizedValue] | None = None
    tool_prompt_template: LocalizedValue | None = None
