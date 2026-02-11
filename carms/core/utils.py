def canonical_id(match_iteration_id: int, program_description_id: int) -> str:
    return f"{match_iteration_id}-{program_description_id}"


def normalize_json_id(json_id: str) -> str:
    return json_id.replace("|", "-")
