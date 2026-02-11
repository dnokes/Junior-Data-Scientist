from collections import defaultdict
from typing import Dict, List, Tuple

from dagster import AssetIn, asset
from sqlmodel import Session, delete, select

from carms.core.database import engine
from carms.models.gold import GoldGeoSummary, GoldProgramProfile
from carms.models.silver import SilverDescriptionSection, SilverProgram


def _aggregate_descriptions(sections: List[SilverDescriptionSection]) -> Dict[str, str]:
    grouped: Dict[str, List[str]] = defaultdict(list)
    for section in sections:
        key = section.program_name or str(section.program_description_id)
        grouped[key].append(f"{section.section_name}: {section.section_text}")
    return {k: "\n".join(v) for k, v in grouped.items()}


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
            description_text = description_map.get(program.program_name)
            gold_rows.append(
                GoldProgramProfile(
                    program_stream_id=program.program_stream_id,
                    program_name=program.program_name,
                    program_stream_name=program.program_stream_name,
                    program_stream=program.program_stream,
                    discipline_name=program.discipline_name,
                    province=program.province,
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
