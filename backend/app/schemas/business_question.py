from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BusinessQuestionCreate(BaseModel):
    investigation_id: UUID
    question_text: str
    question_objective: str | None = None


class BusinessQuestionUpdate(BaseModel):
    investigation_id: UUID | None = None
    question_text: str | None = None
    question_objective: str | None = None


class BusinessQuestionResponse(BaseModel):
    business_question_id: UUID
    investigation_id: UUID
    question_text: str
    question_objective: str | None

    model_config = ConfigDict(from_attributes=True)