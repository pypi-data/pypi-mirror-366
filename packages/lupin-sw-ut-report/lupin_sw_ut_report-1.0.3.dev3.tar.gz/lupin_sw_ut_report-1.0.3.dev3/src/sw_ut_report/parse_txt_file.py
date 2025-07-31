import re
from typing import Dict, List, Tuple

from sw_ut_report.utils import remove_excess_space


def _format_scenario_cover(line: str) -> Tuple[str, List[str]]:
    """
    Extract covers information from a line.

    Args:
        line: Line containing covers information (e.g., "Covers: [SmlPrep-SUBSR-339][SmlPrep-SWID-58]")

    Returns:
        Tuple[str, List[str]]: (formatted_string, list_of_requirement_ids)
    """
    line = re.sub(r"Covers:\s*", "", line).strip()
    result = re.findall(r"\[([^\]]+)\]", line)
    formatted_string = ", ".join(result)
    requirement_list = result  # List of individual requirement IDs
    return formatted_string, requirement_list


def format_txt_file(file_content: str) -> List[Dict]:
    print("\n==================== NEW FILE ====================")
    lines = file_content.splitlines()

    if lines and lines[0].strip().lower().startswith("test case:"):
        scenarios = []
        current_scenario = {}
        current_steps = []
        current_step = {}

        for line in lines:
            line_lower = line.strip().lower()

            if line_lower.startswith("test case:"):
                # Save the current scenario if there is one
                if current_scenario.get("test_case"):
                    if current_step:  # Save any pending step
                        current_steps.append(current_step)
                        current_step = {}
                    current_scenario["steps"] = current_steps
                    scenarios.append(current_scenario)  # Save the complete scenario
                    current_scenario = {}  # Reset the scenario
                    current_steps = []  # Reset the steps

                # Start a new structured scenario
                current_scenario["test_case"] = remove_excess_space(
                    re.sub(r"Test case:\s*", "", line).strip()
                )

            elif line_lower.startswith("covers:"):
                covers_formatted, covers_list = _format_scenario_cover(line)
                current_scenario["covers"] = covers_formatted
                current_scenario["covers_list"] = covers_list  # Add structured list for Jama integration

            elif "given:" in line_lower:
                if current_step:  # If there's an existing step, append it
                    current_steps.append(current_step)
                current_step = {
                    "given": remove_excess_space(line.split(": ", 1)[1].strip())
                }

            elif "when:" in line_lower:
                current_step["when"] = remove_excess_space(
                    line.split(": ", 1)[1].strip()
                )

            elif "then:" in line_lower:
                current_step["then"] = remove_excess_space(
                    line.split(": ", 1)[1].strip()
                )
                current_steps.append(current_step)  # Complete the step and add to steps
                current_step = {}  # Reset for next step

        # Add the last scenario if it's complete (i.e., has a 'test_case')
        if current_scenario.get("test_case"):
            if current_step:  # Add any remaining step
                current_steps.append(current_step)
            current_scenario["steps"] = current_steps
            scenarios.append(current_scenario)

    else:
        # New logic for unstructured TXT files
        scenarios = []
        warnings = []
        i = 0
        lines_len = len(lines)
        while i < lines_len:
            line = lines[i]
            stripped = line.strip()
            if stripped.lower().startswith("covers:"):
                # Find previous non-empty line
                j = i - 1
                while j >= 0 and not lines[j].strip():
                    j -= 1
                if j < 0:
                    warnings.append(f"Warning: 'Covers:' at line {i+1} has no preceding non-empty line. Skipped.")
                    print(f"[DEBUG] Skipping Covers at line {i+1}: no preceding non-empty line.")
                    i += 1
                    continue
                prev_line = lines[j]
                if prev_line.strip().lower().startswith("covers:"):
                    warnings.append(f"Warning: Consecutive 'Covers:' at lines {j+1} and {i+1}. Skipping second.")
                    print(f"[DEBUG] Skipping Covers at line {i+1}: previous line is also Covers.")
                    i += 1
                    continue
                # Parse covers
                covers_formatted, covers_list = _format_scenario_cover(stripped)
                # Collect all lines for this test: test_case, covers, and description
                raw_lines = []
                # Add test_case line
                raw_lines.append(prev_line.rstrip("\n") + "\n")
                # Add covers line
                raw_lines.append(line.rstrip("\n") + "\n")
                # Add description lines
                k = i + 1
                while k < lines_len:
                    next_line = lines[k]
                    lookahead = k + 1
                    while lookahead < lines_len and not lines[lookahead].strip():
                        lookahead += 1
                    if lookahead < lines_len and lines[lookahead].strip().lower().startswith("covers:"):
                        break
                    raw_lines.append(next_line.rstrip("\n") + "\n")
                    k += 1
                print(f"[DEBUG] Found raw_lines: {raw_lines}")
                scenarios.append({
                    "raw_lines": raw_lines,
                    "covers_list": covers_list
                })
                i = k
            else:
                i += 1
        # Optionally: attach warnings somewhere if needed
    return scenarios
