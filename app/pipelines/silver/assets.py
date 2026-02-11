import re
from typing import List, Optional

from dagster import AssetIn, asset
from sqlmodel import Session, delete, select

from carms.core.database import engine
from carms.models.bronze import BronzeDescription, BronzeDiscipline, BronzeProgram
from carms.models.silver import SilverDescriptionSection, SilverDiscipline, SilverProgram

PROVINCE_CODES = {
    "NL",
    "PE",
    "NS",
    "NB",
    "QC",
    "ON",
    "MB",
    "SK",
    "AB",
    "BC",
    "YT",
    "NT",
    "NU",
}


def parse_province(program_site: Optional[str]) -> Optional[str]:
    if not program_site:
        return None
    tokens = [t.strip() for t in program_site.replace(";", ",").split(",") if t.strip()]
    for token in reversed(tokens):
        candidate = token.upper()
        if len(candidate) in (2, 3) and candidate in PROVINCE_CODES:
            return candidate
    return None


def is_valid_text(value: Optional[str]) -> bool:
    return bool(value and str(value).strip())


def parse_quota(match_iteration_name: Optional[str]) -> Optional[int]:
    if not match_iteration_name:
        return None
    match = re.search(r"Approximate Quota:\s*(\d+)", str(match_iteration_name))
    return int(match.group(1)) if match else None


@asset(group_name="silver", ins={"bronze_programs": AssetIn("bronze_programs")})
def silver_programs(bronze_programs) -> int:  # type: ignore[unused-argument]
    with Session(engine) as session:
        programs = session.exec(select(BronzeProgram)).all()
        session.exec(delete(SilverProgram))

        silver_rows: List[SilverProgram] = []
        for row in programs:
            province = parse_province(row.program_site)
            is_valid = all([row.program_stream_id, row.program_name, row.discipline_id])
            silver_rows.append(
                SilverProgram(
                    program_stream_id=row.program_stream_id,
                    discipline_id=row.discipline_id,
                    discipline_name=row.discipline_name,
                    school_id=row.school_id,
                    school_name=row.school_name,
                    program_stream_name=row.program_stream_name,
                    program_site=row.program_site,
                    program_stream=row.program_stream,
                    program_name=row.program_name,
                    program_url=row.program_url,
                    quota=parse_quota(getattr(row, "match_iteration_name", None)),
                    province=province,
                    is_valid=is_valid,
                )
            )

        session.add_all(silver_rows)
        session.commit()
        return len(silver_rows)


@asset(group_name="silver", ins={"bronze_disciplines": AssetIn("bronze_disciplines")})
def silver_disciplines(bronze_disciplines) -> int:  # type: ignore[unused-argument]
    with Session(engine) as session:
        disciplines = session.exec(select(BronzeDiscipline)).all()
        session.exec(delete(SilverDiscipline))

        silver_rows: List[SilverDiscipline] = [
            SilverDiscipline(
                discipline_id=row.discipline_id,
                discipline=row.discipline,
                province=None,
                is_valid=is_valid_text(row.discipline),
            )
            for row in disciplines
        ]

        session.add_all(silver_rows)
        session.commit()
        return len(silver_rows)


@asset(group_name="silver", ins={"bronze_descriptions": AssetIn("bronze_descriptions")})
def silver_description_sections(bronze_descriptions) -> int:  # type: ignore[unused-argument]
    section_columns = [
        "program_contracts",
        "general_instructions",
        "supporting_documentation_information",
        "review_process",
        "interviews",
        "selection_criteria",
        "program_highlights",
        "program_curriculum",
        "training_sites",
        "additional_information",
        "return_of_service",
        "faq",
        "summary_of_changes",
    ]

    with Session(engine) as session:
        descriptions = session.exec(select(BronzeDescription)).all()
        session.exec(delete(SilverDescriptionSection))

        silver_rows: List[SilverDescriptionSection] = []
        for desc in descriptions:
            for col in section_columns:
                text = getattr(desc, col)
                if not is_valid_text(text):
                    continue
                silver_rows.append(
                    SilverDescriptionSection(
                        program_description_id=desc.program_description_id,
                        program_name=desc.program_name,
                        section_name=col,
                        section_text=str(text),
                        is_valid=True,
                    )
                )

        session.add_all(silver_rows)
        session.commit()
        return len(silver_rows)
