from __future__ import annotations

import argparse
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


PROBABLE_CODE_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*")
PAREN_PATTERN = re.compile(r"\(([^()]+)\)")
ROOT_SECTION_TITLES = {
    "zombies",
    "plants",
    "grid items",
    "music types",
}


@dataclass(frozen=True)
class CodenameEntry:
    section_path: str
    name: str
    code_spec: str
    codes: tuple[str, ...]
    line_number: int

    @property
    def logical_key(self) -> tuple[str, str]:
        return self.section_path.casefold(), self.name.casefold()

    @property
    def identity(self) -> tuple[str, str, tuple[str, ...]]:
        return self.section_path.casefold(), self.name.casefold(), self.codes

    def display_line(self) -> str:
        if self.section_path:
            return f"[{self.section_path}] {self.name} - {self.code_spec}"
        return f"{self.name} - {self.code_spec}"


@dataclass
class ParsedSheet:
    path: Path
    entries_by_identity: dict[tuple[str, str, tuple[str, ...]], CodenameEntry]
    entries_by_logical_key: dict[tuple[str, str], list[CodenameEntry]]
    code_to_entries: dict[str, list[CodenameEntry]]


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def looks_like_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return False
    return stripped.endswith(":") and " - " not in stripped


def next_meaningful_line(lines: list[str], start_index: int) -> str:
    for index in range(start_index, len(lines)):
        stripped = lines[index].strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return ""


def _split_top_level(segment: str, separators: set[str]) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0

    for char in segment:
        if char == "(":
            depth += 1
        elif char == ")" and depth > 0:
            depth -= 1

        if char in separators and depth == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
        else:
            current.append(char)

    part = "".join(current).strip()
    if part:
        parts.append(part)
    return parts


def _split_top_level_commas(segment: str) -> list[str]:
    return _split_top_level(segment, {","})


def _split_top_level_slashes(segment: str) -> list[str]:
    return _split_top_level(segment, {"/"})


def _expand_shorthand_code_part(previous_code: str, part: str) -> list[str]:
    token = part.strip()
    if not token:
        return []

    if re.fullmatch(r"\d+", token):
        match = re.search(r"(.*?)(\d+)$", previous_code)
        if match:
            return [match.group(1) + token]

    if re.fullmatch(r"[A-Za-z][A-Za-z0-9-]*", token):
        if "_" in previous_code:
            prefix = previous_code[: previous_code.rfind("_") + 1]
            return [prefix + token]

    return []


def strip_trailing_annotation(code_spec: str) -> str:
    cleaned = normalize_space(code_spec)
    while True:
        match = re.fullmatch(r"(.*?\S)\s+\(([^()]*)\)", cleaned)
        if not match:
            return cleaned
        annotation = match.group(2)
        if not re.search(r"\s", annotation):
            return cleaned
        cleaned = match.group(1).strip()


def normalize_code_spec_text(code_spec: str) -> str:
    cleaned = strip_trailing_annotation(code_spec)
    cleaned = re.sub(r"\s*/\s*", "/", cleaned)
    cleaned = re.sub(r"\s*,\s*", ",", cleaned)
    return cleaned.strip()


def expand_safe_pattern(code: str) -> list[str]:
    if "(" not in code:
        return [code]

    match = PAREN_PATTERN.search(code)
    if not match:
        return [code]

    options: list[str] = []
    for raw_option in match.group(1).split("/"):
        option = raw_option.strip()
        if not option or re.search(r"\s", option):
            return [code]

        range_match = re.fullmatch(r"(-?\d+)-(-?\d+)", option)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            step = 1 if end >= start else -1
            options.extend(str(value) for value in range(start, end + step, step))
            continue

        if not re.fullmatch(r"[A-Za-z0-9_.-]+", option):
            return [code]
        options.append(option)

    prefix = code[: match.start()]
    suffix = code[match.end() :]
    expanded: list[str] = []
    for option in options:
        expanded.extend(expand_safe_pattern(prefix + option + suffix))
    return expanded


def parse_code_spec(code_spec: str) -> list[str]:
    cleaned = normalize_code_spec_text(code_spec)

    codes: list[str] = []
    for comma_part in _split_top_level_commas(cleaned):
        for part in _split_top_level_slashes(comma_part):
            token = part.strip()
            if not token:
                continue

            if codes:
                shorthand_codes = _expand_shorthand_code_part(codes[-1], token)
                if shorthand_codes:
                    codes.extend(shorthand_codes)
                    continue

            codes.extend(expand_safe_pattern(token))

    unique_codes: list[str] = []
    seen: set[str] = set()
    for code in codes:
        if not PROBABLE_CODE_RE.fullmatch(code):
            continue
        if code in seen:
            continue
        seen.add(code)
        unique_codes.append(code)

    return unique_codes


def parse_entry_line(line: str, section_path: str, line_number: int) -> CodenameEntry | None:
    if " - " not in line:
        return None

    name, code_spec = [part.strip() for part in line.split(" - ", 1)]
    if not name or not code_spec:
        return None

    normalized_name = normalize_space(name)
    normalized_code_spec = normalize_code_spec_text(code_spec)
    codes = tuple(parse_code_spec(code_spec))
    if not codes:
        return None

    return CodenameEntry(
        section_path=section_path,
        name=normalized_name,
        code_spec=normalized_code_spec,
        codes=codes,
        line_number=line_number,
    )


def parse_sheet(path: Path) -> ParsedSheet:
    text = path.read_text(encoding="utf-8", errors="replace").lstrip("\ufeff")
    lines = text.splitlines()
    entries_by_identity: dict[tuple[str, str, tuple[str, ...]], CodenameEntry] = {}
    parent_heading = ""
    current_section = ""

    for index, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if looks_like_heading(stripped):
            title = normalize_space(stripped[:-1])
            normalized_title = title.casefold()
            if normalized_title in ROOT_SECTION_TITLES:
                parent_heading = title
                current_section = ""
                continue

            next_line = next_meaningful_line(lines, index)
            if next_line and looks_like_heading(next_line):
                parent_heading = title
                current_section = ""
            else:
                current_section = title
            continue

        section_path = current_section
        if parent_heading and current_section and parent_heading.casefold() != current_section.casefold():
            section_path = f"{parent_heading} > {current_section}"
        elif not section_path:
            section_path = parent_heading

        entry = parse_entry_line(stripped, section_path, index)
        if entry is None:
            continue
        entries_by_identity.setdefault(entry.identity, entry)

    entries_by_logical_key: dict[tuple[str, str], list[CodenameEntry]] = defaultdict(list)
    code_to_entries: dict[str, list[CodenameEntry]] = defaultdict(list)

    for entry in sorted(entries_by_identity.values(), key=lambda item: (item.section_path, item.name, item.codes)):
        entries_by_logical_key[entry.logical_key].append(entry)
        for code in entry.codes:
            code_to_entries[code].append(entry)

    return ParsedSheet(
        path=path,
        entries_by_identity=entries_by_identity,
        entries_by_logical_key=dict(entries_by_logical_key),
        code_to_entries=dict(code_to_entries),
    )


def compare_sheets(old_sheet: ParsedSheet, new_sheet: ParsedSheet) -> dict[str, object]:
    changed_entries: list[tuple[CodenameEntry, CodenameEntry]] = []
    changed_old_ids: set[tuple[str, str, tuple[str, ...]]] = set()
    changed_new_ids: set[tuple[str, str, tuple[str, ...]]] = set()

    shared_logical_keys = set(old_sheet.entries_by_logical_key) & set(new_sheet.entries_by_logical_key)
    for logical_key in sorted(shared_logical_keys):
        old_entries = old_sheet.entries_by_logical_key[logical_key]
        new_entries = new_sheet.entries_by_logical_key[logical_key]
        if len(old_entries) != 1 or len(new_entries) != 1:
            continue

        old_entry = old_entries[0]
        new_entry = new_entries[0]
        if old_entry.codes != new_entry.codes or old_entry.code_spec != new_entry.code_spec:
            changed_entries.append((old_entry, new_entry))
            changed_old_ids.add(old_entry.identity)
            changed_new_ids.add(new_entry.identity)

    added_entries = [
        entry
        for entry in new_sheet.entries_by_identity.values()
        if entry.identity not in old_sheet.entries_by_identity and entry.identity not in changed_new_ids
    ]
    removed_entries = [
        entry
        for entry in old_sheet.entries_by_identity.values()
        if entry.identity not in new_sheet.entries_by_identity and entry.identity not in changed_old_ids
    ]

    added_entries.sort(key=lambda item: (item.section_path, item.name, item.codes))
    removed_entries.sort(key=lambda item: (item.section_path, item.name, item.codes))

    old_codes = set(old_sheet.code_to_entries)
    new_codes = set(new_sheet.code_to_entries)
    added_codes = sorted(new_codes - old_codes)
    removed_codes = sorted(old_codes - new_codes)

    return {
        "added_entries": added_entries,
        "removed_entries": removed_entries,
        "changed_entries": changed_entries,
        "added_codes": added_codes,
        "removed_codes": removed_codes,
    }


def format_entry_origin_list(entries: list[CodenameEntry]) -> str:
    parts = []
    seen: set[str] = set()
    for entry in entries:
        label = entry.display_line()
        if label in seen:
            continue
        seen.add(label)
        parts.append(label)
    return "; ".join(parts)


def collect_new_sheet_entries(diff: dict[str, object]) -> list[CodenameEntry]:
    added_entries: list[CodenameEntry] = diff["added_entries"]  # type: ignore[assignment]
    changed_entries: list[tuple[CodenameEntry, CodenameEntry]] = diff["changed_entries"]  # type: ignore[assignment]

    collected: list[CodenameEntry] = []
    seen: set[tuple[str, str, tuple[str, ...]]] = set()

    for entry in added_entries:
        if entry.identity in seen:
            continue
        seen.add(entry.identity)
        collected.append(entry)

    for _old_entry, new_entry in changed_entries:
        if new_entry.identity in seen:
            continue
        seen.add(new_entry.identity)
        collected.append(new_entry)

    collected.sort(key=lambda item: (item.line_number, item.section_path.casefold(), item.name.casefold()))
    return collected


def format_added_sheet(entries: list[CodenameEntry]) -> str:
    ordered_entries = sorted(entries, key=lambda item: (item.line_number, item.section_path.casefold(), item.name.casefold()))
    if not ordered_entries:
        return "No new codename differences found.\n"

    lines: list[str] = []
    last_root_heading = ""
    last_subheading_path: tuple[str, ...] = ()

    for entry in ordered_entries:
        heading_path = tuple(part.strip() for part in entry.section_path.split(" > ") if part.strip())
        root_heading = heading_path[0] if heading_path else "Misc"
        subheading_path = heading_path[1:]

        if root_heading != last_root_heading:
            if lines and lines[-1] != "":
                lines.append("")
            lines.append(f"new {root_heading}:")
            lines.append("")
            last_root_heading = root_heading
            last_subheading_path = ()

        shared_length = 0
        max_shared = min(len(last_subheading_path), len(subheading_path))
        while shared_length < max_shared and last_subheading_path[shared_length] == subheading_path[shared_length]:
            shared_length += 1

        if subheading_path != last_subheading_path:
            if lines and lines[-1] != "":
                lines.append("")
            for heading in subheading_path[shared_length:]:
                lines.append(f"{heading}:")
                lines.append("")
            last_subheading_path = subheading_path

        lines.append(f"{entry.name} - {entry.code_spec}")

    return "\n".join(lines).rstrip() + "\n"


def format_changelog(old_sheet: ParsedSheet, new_sheet: ParsedSheet, diff: dict[str, object], additions_only: bool) -> str:
    added_entries: list[CodenameEntry] = diff["added_entries"]  # type: ignore[assignment]
    removed_entries: list[CodenameEntry] = diff["removed_entries"]  # type: ignore[assignment]
    changed_entries: list[tuple[CodenameEntry, CodenameEntry]] = diff["changed_entries"]  # type: ignore[assignment]
    added_codes: list[str] = diff["added_codes"]  # type: ignore[assignment]
    removed_codes: list[str] = diff["removed_codes"]  # type: ignore[assignment]

    lines = [
        "Codename Changelog",
        f"Old file: {old_sheet.path}",
        f"New file: {new_sheet.path}",
        "",
        "Summary",
        f"- Added entries: {len(added_entries)}",
        f"- Changed entries: {len(changed_entries)}",
        f"- Removed entries: {len(removed_entries)}",
        f"- New unique codes: {len(added_codes)}",
        f"- Removed unique codes: {len(removed_codes)}",
    ]

    if added_codes:
        lines.extend(["", "New Unique Codenames"])
        for code in added_codes:
            origin_text = format_entry_origin_list(new_sheet.code_to_entries.get(code, []))
            lines.append(f"- {code}")
            lines.append(f"  Added in: {origin_text}")

    if added_entries:
        lines.extend(["", "Added Entries"])
        for entry in added_entries:
            lines.append(f"- {entry.display_line()}")

    if changed_entries and not additions_only:
        lines.extend(["", "Changed Entries"])
        for old_entry, new_entry in changed_entries:
            label = f"[{new_entry.section_path}] {new_entry.name}" if new_entry.section_path else new_entry.name
            lines.append(f"- {label}")
            lines.append(f"  Old: {old_entry.code_spec}")
            lines.append(f"  New: {new_entry.code_spec}")

    if removed_codes and not additions_only:
        lines.extend(["", "Removed Unique Codenames"])
        for code in removed_codes:
            origin_text = format_entry_origin_list(old_sheet.code_to_entries.get(code, []))
            lines.append(f"- {code}")
            lines.append(f"  Removed from: {origin_text}")

    if removed_entries and not additions_only:
        lines.extend(["", "Removed Entries"])
        for entry in removed_entries:
            lines.append(f"- {entry.display_line()}")

    return "\n".join(lines).strip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare two codename sheets and output either a mini sheet of new entries or a full changelog, while ignoring blank or whitespace-only noise."
    )
    parser.add_argument("old_file", type=Path, help="Older codename sheet.")
    parser.add_argument("new_file", type=Path, help="Newer codename sheet.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional output text file. If omitted, the result is printed to stdout.",
    )
    parser.add_argument(
        "--format",
        choices=("added-sheet", "changelog"),
        default="added-sheet",
        help="Output mode. 'added-sheet' writes everything present in the new file but not shared with the old one, in codename-sheet style. 'changelog' writes the detailed report.",
    )
    parser.add_argument(
        "--additions-only",
        action="store_true",
        help="When using --format changelog, only show new entries and new unique codes.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    old_sheet = parse_sheet(args.old_file.resolve())
    new_sheet = parse_sheet(args.new_file.resolve())
    diff = compare_sheets(old_sheet, new_sheet)
    if args.format == "added-sheet":
        output_text = format_added_sheet(collect_new_sheet_entries(diff))
    else:
        output_text = format_changelog(old_sheet, new_sheet, diff, additions_only=args.additions_only)

    if args.output:
        args.output.write_text(output_text, encoding="utf-8")
        print(f"Wrote output to {args.output.resolve()}")
        return

    print(output_text, end="")


if __name__ == "__main__":
    main()
