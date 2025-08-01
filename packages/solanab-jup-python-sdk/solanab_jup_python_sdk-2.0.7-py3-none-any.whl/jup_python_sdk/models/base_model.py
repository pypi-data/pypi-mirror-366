from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic.alias_generators import to_camel


class BaseModel(PydanticBaseModel):
    """
    Base model class that provides common functionality for all models.

    This class extends Pydantic's BaseModel to provide a standardized
    to_dict() method that converts model fields to camelCase format,
    which is commonly required for API requests.
    """

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the model to a dictionary with camelCase keys.

        This method dumps the model fields, excludes None values,
        and converts snake_case field names to camelCase format
        suitable for API requests.

        Returns:
            Dict with camelCase keys and non-None values.
        """
        params = self.model_dump(exclude_none=True)
        camel_case_params = {to_camel(key): value for key, value in params.items()}
        return camel_case_params
