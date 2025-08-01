from datetime import datetime
from typing import Any
from typing import Mapping
from typing import TypeAlias

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_serializer
from pydantic import field_validator
from pydantic import model_validator

ParameterType: TypeAlias = list[dict] | str | None


class ParameterValue(BaseModel):
    parameter_value_start_date: datetime = Field(alias="parameterValueStartDate")
    parameter_value_id: int = Field(alias="parameterValueId")
    parameter_value: str = Field(alias="parameterValue")

    @field_validator("parameter_value_start_date", mode="before")
    def set_default_start_date(cls, v):
        if v is None:
            return datetime(1, 1, 1)
        return v


class Parameter(BaseModel):
    parameter_name: str = Field(alias="parameterName")
    parameter_values: list[ParameterValue] = Field(alias="parameterValues")


class ParameterParser(BaseModel):
    parameters: list[Parameter]
    dataset_date: datetime
    filtered_parameters: list[Mapping[str, Any]] | None = None

    @model_validator(mode="after")
    def filter_latest_parameters(self) -> "ParameterParser":
        """
        Filters the parameter values to keep only the most recent value for each parameter name,
        based on the dataset date. The result is stored in `filtered_parameters`.

        Returns:
            ParameterParser: The model instance with `filtered_parameters` populated.
        """

        # parameters is always a list, checking for emptiness
        if not self.parameters:
            self.filtered_parameters = []
            return self

        filtered_data = []
        for parameter in self.parameters:
            valid_values = [
                value
                for value in parameter.parameter_values
                if value.parameter_value_start_date <= self.dataset_date
            ]
            if valid_values:
                latest_value = max(
                    valid_values, key=lambda x: x.parameter_value_start_date.isoformat()
                )
                filtered_param = {
                    "parameterName": parameter.parameter_name,
                    "parameterValues": [
                        {
                            "parameterValue": latest_value.parameter_value,
                            "parameterValueId": latest_value.parameter_value_id,
                            "parameterValueStartDate": latest_value.parameter_value_start_date.isoformat(),
                        }
                    ],
                }
                filtered_data.append(filtered_param)

        self.filtered_parameters = filtered_data
        return self
