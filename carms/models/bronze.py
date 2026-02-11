from typing import Optional

from sqlmodel import Field, SQLModel


class BronzeProgram(SQLModel, table=True):
    __tablename__ = "bronze_program"
    program_stream_id: int = Field(primary_key=True)
    discipline_id: int
    discipline_name: str
    school_id: int
    school_name: str
    program_stream_name: str
    program_site: str
    program_stream: str
    program_name: str
    program_url: Optional[str] = None


class BronzeDiscipline(SQLModel, table=True):
    __tablename__ = "bronze_discipline"
    discipline_id: int = Field(primary_key=True)
    discipline: str


class BronzeDescription(SQLModel, table=True):
    __tablename__ = "bronze_description"
    document_id: str = Field(primary_key=True)
    source: Optional[str] = None
    n_program_description_sections: Optional[int] = None
    program_name: str
    match_iteration_name: Optional[str] = None
    program_contracts: Optional[str] = None
    general_instructions: Optional[str] = None
    supporting_documentation_information: Optional[str] = None
    review_process: Optional[str] = None
    interviews: Optional[str] = None
    selection_criteria: Optional[str] = None
    program_highlights: Optional[str] = None
    program_curriculum: Optional[str] = None
    training_sites: Optional[str] = None
    additional_information: Optional[str] = None
    return_of_service: Optional[str] = None
    faq: Optional[str] = None
    summary_of_changes: Optional[str] = None
    match_iteration_id: Optional[int] = None
    program_description_id: int
