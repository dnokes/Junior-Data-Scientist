# Data Dictionary

## Bronze
- bronze_program: discipline/program identifiers and URLs exactly as supplied in 1503_program_master.xlsx.
- bronze_discipline: discipline lookup from 1503_discipline.xlsx.
- bronze_description: wide-format program descriptions and sections from 1503_program_descriptions_x_section.csv.

## Silver
- silver_program: cleaned programs with province parsed from program_site and is_valid flagging row-level sanity.
- silver_discipline: discipline lookup with is_valid flag.
- silver_description_section: long-form description sections (program_description_id, program_name, section_name, section_text, is_valid).

## Gold
- gold_program_profile: curated combination of program metadata and concatenated descriptions to support API and semantic search.
- gold_geo_summary: provincial rollups of program counts and average quota (nullable when quota data is absent).
