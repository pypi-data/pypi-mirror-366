from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from pysimplesat.models.base.base_model import SimpleSatModel

class Pagination(SimpleSatModel):
    current_page: int | None = Field(default=None, alias="CurrentPage")
    current_page_count: int | None = Field(default=None, alias="CurrentPageCount")
    limit: int | None = Field(default=None, alias="Limit")
    total_count: int | None = Field(default=None, alias="TotalCount")
    next_page: int | None = Field(default=None, alias="NextPage")
    next_page_url: str | None = Field(default=None, alias="NextPageURL")
    next_page_token: str | None = Field(default=None, alias="NextPageToken")
    
class Answer(SimpleSatModel):
    id: int | None = Field(default=None, alias="Id")
    created: datetime | None = Field(default=None, alias="Created")
    modified: datetime | None = Field(default=None, alias="Modified")
    question: dict[str, Any] | None = Field(default=None, alias="Question")
    choice: str | None = Field(default=None, alias="Choice")
    choice_label: str | None = Field(default=None, alias="ChoiceLabel")
    choices: list | None = Field(default=None, alias="Choices")
    sentiment: str | None = Field(default=None, alias="Sentiment")
    comment: str | None = Field(default=None, alias="Comment")
    follow_up_answer: str | None = Field(default=None, alias="FollowUpAnswer")
    follow_up_answer_choice: str | None = Field(default=None, alias="FollowUpAnswerChoice")
    follow_up_answer_choices: list | None = Field(default=None, alias="FollowUpAnswerChoices")
    survey: dict[str, str | int] | None = Field(default=None, alias="Survey")
    published_as_testimonial: bool | None = Field(default=None, alias="PublishedAsTestimonial")
    response_id: int | None = Field(default=None, alias="ResponseId")

class Customer(SimpleSatModel):
    id: int | None = Field(default=None, alias="Id")
    external_id: str | None = Field(default=None, alias="ExternalId")
    created: datetime | None = Field(default=None, alias="Created")
    modified: datetime | None = Field(default=None, alias="Modified")
    name: str | None = Field(default=None, alias="Name")
    email: str | None = Field(default=None, alias="Email")
    company: str | None = Field(default=None, alias="Company")
    custom_attributes: dict[str, str | int] | None = Field(default=None, alias="CustomAttributes")

class TeamMember(SimpleSatModel):
    id: int | None = Field(default=None, alias="Id")
    external_id: str | None = Field(default=None, alias="ExternalId")
    created: datetime | None = Field(default=None, alias="Created")
    modified: datetime | None = Field(default=None, alias="Modified")
    name: str | None = Field(default=None, alias="Name")
    email: str | None = Field(default=None, alias="Email")
    custom_attributes: dict[str, str | int] | None = Field(default=None, alias="CustomAttributes")

class Response(SimpleSatModel):
    survey_id: int | None = Field(default=None, alias="SurveyId")
    tags: list | None = Field(default=None, alias="Tags")
    answers: list[dict[str, Any]] | None = Field(default=None, alias="Answers")
    team_members: list[dict[str, Any]] | None = Field(default=None, alias="TeamMembers")
    ticket: dict[str, Any] | None = Field(default=None, alias="Ticket")
    customer: dict[str, Any] | None = Field(default=None, alias="Customer")

class Survey(SimpleSatModel):
    id: int | None = Field(default=None, alias="Id")
    name: str | None = Field(default=None, alias="Name")
    metric: str | None = Field(default=None, alias="Metric")
    survey_token: str | None = Field(default=None, alias="SurveyToken")
    survey_type: str | None = Field(default=None, alias="SurveyType")
    brand_name: str | None = Field(default=None, alias="BrandName")

class CustomerBulk(SimpleSatModel):
    request_id: str | None = Field(default=None, alias="RequestId")
    detail: str | None = Field(default=None, alias="Detail")
    
class SurveyEmail(SimpleSatModel):
    detail: str | None = Field(default=None, alias="Detail")
