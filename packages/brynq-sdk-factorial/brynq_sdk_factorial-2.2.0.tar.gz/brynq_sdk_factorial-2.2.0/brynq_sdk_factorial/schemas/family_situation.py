# Auto-generated schemas for category: family_situation

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class Family_situationGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="ID of the family situation.", alias="id")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Employee id of the family situation.", alias="employee_id")
    civil_status: Series[String] = pa.Field(coerce=True, nullable=True, description="Civil status of the employee.", alias="civil_status")
    number_of_dependants: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Number of dependants of the employee.", alias="number_of_dependants")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class Family_situationCreate(BaseModel):
    employee_id: int = Field(..., description="Employee id.", alias="employee_id")
    civil_status: Optional[Annotated[str, StringConstraints(pattern=r'^single|cohabitating|divorced|married|unknown|civil_partnership|separated|widow|not_applicable$', strip_whitespace=True)]] = Field(None, description="Civil status of the employee.", alias="civil_status")
    number_of_dependants: Optional[int] = Field(None, description="Number of dependants of the employee.", alias="number_of_dependants")

class Family_situationDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")
