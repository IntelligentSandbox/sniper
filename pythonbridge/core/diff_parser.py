import re


def parse_patch(patch: str) -> tuple[str, set[int]]:
    """Annotate a raw unified diff with real new-file line numbers.

    Returns the annotated string and the set of added line numbers (valid comment targets).
    """
    annotated_lines = []
    valid_lines = set()
    new_line = 0

    for raw_line in patch.splitlines():
        # Hunk header: @@ -old_start,old_count +new_start,new_count @@
        hunk_match = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", raw_line)
        if hunk_match:
            new_line = int(hunk_match.group(1))
            annotated_lines.append(raw_line)
            continue

        if raw_line.startswith("+"):
            # Added line -- exists in new file, valid comment target
            annotated_lines.append(f"line {new_line}: {raw_line}")
            valid_lines.add(new_line)
            new_line += 1
        elif raw_line.startswith("-"):
            # Removed line -- skip line number increment, cannot be commented on
            annotated_lines.append(f"(removed): {raw_line}")
        else:
            # Context line -- unchanged, advance new file counter
            annotated_lines.append(f"line {new_line}: {raw_line}")
            new_line += 1

    return "\n".join(annotated_lines), valid_lines


def clamp_to_valid(comments: list[dict], valid_lines: set[int]) -> list[dict]:
    """Drop comments whose line numbers are outside the diff (GitHub would reject them)."""
    return [c for c in comments if c.get("line") in valid_lines]
