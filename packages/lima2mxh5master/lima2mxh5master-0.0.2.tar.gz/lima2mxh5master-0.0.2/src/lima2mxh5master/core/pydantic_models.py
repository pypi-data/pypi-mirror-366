import keyword
from typing import Any
from typing import Dict
from typing import List

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class InstanceMethodCall(BaseModel):
    """
    InstanceMethodCall is a Pydantic model that represents a call to an instance
    method.
    """

    class_name: str = Field(alias="__class__")
    method_name: str = Field(alias="__method__")
    kwargs: Dict[str, Any] = Field(default_factory=dict, alias="__kwargs__")
    args: List[Any] = Field(default_factory=list, alias="__args__")

    @field_validator("method_name")
    def method_name_valid(cls, v):
        """
        Validate that the method name does not start with an underscore.

        This ensures that the method name provided for dynamic invocation
        is a public method and avoids calling private or special methods.
        """
        if v.startswith("_"):
            raise ValueError("Method name cannot start with underscore")
        return v

    @field_validator("class_name")
    def validate_class_name(cls, v):
        """
        Validate that the class name is a valid Python identifier and not a keyword.

        Ensures that the class name used for instance resolution is syntactically
        valid and not reserved by Python.
        """
        if not v.isidentifier():
            raise ValueError("Class name must be a valid Python identifier.")
        if keyword.iskeyword(v):
            raise ValueError("Class name cannot be a Python keyword.")
        return v
