from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from dagster import AssetIn, asset
from sqlmodel import Session, delete, select

from carms.core.database import engine
from carms.models.gold import GoldGeoSummary, GoldProgramProfile
from carms.models.silver import SilverDescriptionSection, SilverProgram

DESCRIPTION_SECTION_ORDER = [
    "program_highlights",
    "selection_criteria",
    "interviews",
    "program_curriculum",
    "training_sites",
    "additional_information",
]


def _render_section_title(section_name: str) -> str:
    return section_name.replace("_", " ").title()


def _aggregate_descriptions(sections: List[SilverDescriptionSection]) -> Dict[int, str]:
    grouped: Dict[int, Dict[str, str]] = defaultdict(dict)
    for section in sections:
        if not section.section_text:
            continue
        if section.section_name not in DESCRIPTION_SECTION_ORDER:
            continue
        grouped[section.program_description_id][section.section_name] = section.section_text

    aggregated: Dict[int, str] = {}
    for program_description_id, section_map in grouped.items():
        chunks: List[str] = []
        for section_name in DESCRIPTION_SECTION_ORDER:
            section_text: Optional[str] = section_map.get(section_name)
            if not section_text:
                continue
            chunks.append(f"## {_render_section_title(section_name)}\n{section_text}")

        if chunks:
            aggregated[program_description_id] = "\n\n".join(chunks)

    return aggregated


@asset(
    group_name="gold",
    ins={
        "silver_programs": AssetIn("silver_programs"),
        "silver_disciplines": AssetIn("silver_disciplines"),
        "silver_description_sections": AssetIn("silver_description_sections"),
    },
)
def gold_program_profiles(
    silver_programs, silver_disciplines, silver_description_sections
) -> int:  # type: ignore[unused-argument]
    with Session(engine) as session:
        programs = session.exec(select(SilverProgram)).all()
        sections = session.exec(select(SilverDescriptionSection)).all()

        description_map = _aggregate_descriptions(sections)

        session.exec(delete(GoldProgramProfile))
        gold_rows: List[GoldProgramProfile] = []
        for program in programs:
            description_text = description_map.get(program.program_stream_id)
            gold_rows.append(
                GoldProgramProfile(
                    program_stream_id=program.program_stream_id,
                    program_name=program.program_name,
                    program_stream_name=program.program_stream_name,
                    program_stream=program.program_stream,
                    discipline_name=program.discipline_name,
                    province=program.province or "UNKNOWN",
                    school_name=program.school_name,
                    program_site=program.program_site,
                    program_url=program.program_url,
                    description_text=description_text,
                    is_valid=program.is_valid,
                )
            )

        session.add_all(gold_rows)
        session.commit()
        return len(gold_rows)


@asset(
    group_name="gold",
    ins={"silver_programs": AssetIn("silver_programs")},
)
def gold_geo_summary(silver_programs) -> int:  # type: ignore[unused-argument]
    with Session(engine) as session:
        programs = session.exec(select(SilverProgram)).all()

        rollups: Dict[Tuple[str, str], List[int]] = defaultdict(list)
        program_counts: Dict[Tuple[str, str], int] = defaultdict(int)
        for program in programs:
            key = (program.province or "UNKNOWN", program.discipline_name)
            program_counts[key] += 1
            if program.quota is not None:
                rollups[key].append(program.quota)

        session.exec(delete(GoldGeoSummary))
        rows: List[GoldGeoSummary] = []
        for (province, discipline_name), count in program_counts.items():
            quotas = rollups.get((province, discipline_name), [])
            avg_quota = sum(quotas) / len(quotas) if quotas else None
            rows.append(
                GoldGeoSummary(
                    province=province,
                    discipline_name=discipline_name,
                    program_count=count,
                    avg_quota=avg_quota,
                )
            )

        session.add_all(rows)
        session.commit()
        return len(rows)
