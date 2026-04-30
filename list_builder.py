import argparse
import os
import re
import sys
import tkinter as tk
from dataclasses import dataclass
from tkinter import filedialog, messagebox, scrolledtext, ttk


CATEGORY_ORDER = ("zombies", "plants", "grid")
CATEGORY_LABELS = {
    "zombies": "Zombies",
    "plants": "Plants",
    "grid": "Grid Items",
}
CATEGORY_SINGULAR = {
    "zombies": "Zombie",
    "plants": "Plant",
    "grid": "Grid item",
}
SECTION_HEADERS = {
    "# zombie codename list": ("zombies", "codes"),
    "# zombie entry list": ("zombies", "entries"),
    "# plant codename list": ("plants", "codes"),
    "# plant entry list": ("plants", "entries"),
    "# grid item codename list": ("grid", "codes"),
    "# grid item flag list": ("grid", "flags"),
}


@dataclass
class BuilderEntry:
    alias: str = ""
    typename: str = ""
    is_boss: bool = False
    include_entry: bool = True
    is_portal: bool = False
    source_alias: str = ""
    source_typename: str = ""
    plant_gameversion: str = "0"
    plant_classname: str = ""


PLACEHOLDER_ALIAS = "Aliases"
PLACEHOLDER_TYPENAME = "Typename"


def configure_tk_environment():
    base_dir = os.path.dirname(sys.executable)
    tcl_dir = os.path.join(base_dir, "tcl")
    tcl_library = os.path.join(tcl_dir, "tcl8.6")
    tk_library = os.path.join(tcl_dir, "tk8.6")

    if os.path.isdir(tcl_library) and "TCL_LIBRARY" not in os.environ:
        os.environ["TCL_LIBRARY"] = tcl_library
    if os.path.isdir(tk_library) and "TK_LIBRARY" not in os.environ:
        os.environ["TK_LIBRARY"] = tk_library


def expand_pattern(code):
    pattern = re.compile(r"\(([^()]+)\)")
    if "(" not in code:
        return [code]

    match = pattern.search(code)
    if not match:
        return [code]

    options = []
    for raw_option in match.group(1).split("/"):
        option = raw_option.strip()
        range_match = re.fullmatch(r"(-?\d+)-(-?\d+)", option)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            step = 1 if end >= start else -1
            options.extend(str(value) for value in range(start, end + step, step))
        elif option:
            options.append(option)

    prefix = code[: match.start()]
    suffix = code[match.end() :]
    expanded = []
    for option in options:
        expanded.extend(expand_pattern(prefix + option + suffix))
    return expanded


def _split_top_level(segment, separators):
    parts = []
    current = []
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


def _split_top_level_slashes(segment):
    return _split_top_level(segment, {"/"})


def _split_top_level_commas(segment):
    return _split_top_level(segment, {","})


def _expand_shorthand_code_part(previous_code, part):
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


def parse_code_segment(segment):
    codes = []
    for comma_part in _split_top_level_commas(segment):
        parts = _split_top_level_slashes(comma_part)
        for part in parts:
            if codes:
                shorthand_codes = _expand_shorthand_code_part(codes[-1], part)
                if shorthand_codes:
                    codes.extend(shorthand_codes)
                    continue
            codes.extend(expand_pattern(part))
    return codes


def parse_primary_code_segment(segment):
    codes = parse_code_segment(segment)
    if not codes:
        return []
    return [codes[0]]


def split_pipe_items(text):
    return [item.strip() for item in text.split("|") if item.strip()]


def is_grid_flag_list_line(text):
    items = split_pipe_items(text)
    if not items:
        return False
    for item in items:
        normalized = item.strip().lower()
        if normalized.startswith("0"):
            continue
        if normalized.startswith("1"):
            continue
        return False
    return True


PLANT_KEYWORDS = [
    "sunflower",
    "shroom",
    "pult",
    "bean",
    "choy",
    "cactus",
    "lilypad",
    "pumpkin",
    "cherry",
    "banana",
    "dandelion",
    "gravebuster",
    "torchwood",
    "empea",
    "tanglekelp",
    "aloe",
    "imitater",
    "potatomine",
    "iceburg",
    "snowpea",
    "wintermelon",
    "starfruit",
    "magnifyinggrass",
    "ghostpepper",
    "redstinger",
    "nightshade",
    "wallnut",
    "tallnut",
    "hulonut",
    "endurian",
    "kernelpult",
    "hurrikale",
    "stunion",
    "stallia",
    "thymewarp",
    "primal",
    "moss",
    "mint",
    "tool_",
]

GRID_KEYWORDS = [
    "grave",
    "gravestone",
    "railcart",
    "minecart",
    "portal",
    "present",
    "tar",
    "powertile",
    "goldtile",
    "bufftile",
    "plank",
    "tile",
    "portal",
    "present",
    "potion",
    "lilypad",
    "vase",
    "surfboard",
    "tent",
    "backpack",
    "slider",
    "sap",
    "lava",
    "wisp",
    "trap",
    "crater",
    "speaker",
    "cabinet",
    "flower",
    "seed",
    "boosttile",
    "score_",
    "staff",
    "oil",
    "butter",
    "rock",
    "egg",
    "sewer",
    "scarecrow",
    "holidaydrink",
    "traptile",
    "fireworks",
    "snow",
    "cloud",
    "effect",
    "rain",
    "thunderstorm",
    "puddle",
    "table",
    "box",
    "card",
    "fog",
    "shield",
    "cauldron",
    "yuanbao",
]


def normalize_display_name(name):
    return re.sub(r"\s+", " ", name.strip())


def humanize_typename(code):
    cleaned = re.sub(r"[_-]+", " ", code.strip())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return "Untitled Entry"
    return cleaned.title()


def is_probable_typename(value):
    candidate = value.strip()
    if not candidate:
        return False
    if any(char in candidate for char in ('"', "'", ":", ",")):
        return False
    if " " in candidate:
        return False
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", candidate))


def filter_typenames(codes):
    return [code for code in codes if is_probable_typename(code)]


def pipe_join(items):
    if not items:
        return ""
    return "|".join(items) + "|"


def effective_alias(entry):
    alias = normalize_display_name(entry.alias)
    if alias:
        return alias
    return PLACEHOLDER_ALIAS


def effective_typename(entry):
    typename = entry.typename.strip()
    if typename:
        return typename
    return PLACEHOLDER_TYPENAME


def display_alias(entry):
    if entry.source_alias:
        return entry.source_alias
    return effective_alias(entry)


def display_typename(entry):
    if entry.source_typename:
        return entry.source_typename
    return effective_typename(entry)


def is_portal_entry(name, codes):
    if "portal" in name.lower():
        return True
    for code in codes:
        if "portal" in code.lower():
            return True
    return False


def is_zomboss_entry(name, codes):
    if "zomboss" in name.lower() or "boss" in name.lower():
        return True
    for code in codes:
        if "zomboss" in code.lower() or code.endswith("_zomboss"):
            return True
    return False


def is_plant_entry(name, codes):
    lower = name.lower()
    if any(keyword in lower for keyword in PLANT_KEYWORDS):
        return True
    for code in codes:
        lower_code = code.lower()
        if any(keyword in lower_code for keyword in PLANT_KEYWORDS):
            return True
    return False


def is_grid_entry(name, codes):
    lower = name.lower()
    if any(keyword in lower for keyword in GRID_KEYWORDS):
        return True
    for code in codes:
        lower_code = code.lower()
        if any(keyword in lower_code for keyword in GRID_KEYWORDS):
            return True
    return False


def classify_raw_codes(codes):
    if codes and all(any(keyword in code.lower() for keyword in PLANT_KEYWORDS) for code in codes):
        return "plants"
    if codes and all(is_grid_entry(code, [code]) for code in codes):
        return "grid"
    return "zombies"


def infer_category(name, codes):
    if is_grid_entry(name, codes):
        return "grid"
    if is_plant_entry(name, codes):
        return "plants"
    return classify_raw_codes(codes)


def looks_like_heading(line):
    if any(token in line for token in (" - ", "|")):
        return False
    if re.fullmatch(r"[01]\s*,.*", line):
        return False
    if line.endswith(":"):
        return True
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9 '&()/.-]{1,60}", line) and line == line.title():
        return True
    return False


def detect_section_header(line):
    return SECTION_HEADERS.get(line.strip().lower())


def parse_named_code_segment(segment):
    raw_parts = _split_top_level_slashes(segment)
    expanded_codes = filter_typenames(parse_code_segment(segment))
    if len(expanded_codes) <= 1:
        return expanded_codes

    if "," in segment:
        return expanded_codes

    if "(" in segment:
        return expanded_codes

    if any(re.fullmatch(r"\d+", part.strip()) for part in raw_parts[1:]):
        return expanded_codes

    if any(_expand_shorthand_code_part(expanded_codes[0], part.strip()) for part in raw_parts[1:]):
        return expanded_codes

    base_code = expanded_codes[0]
    if all(
        code == base_code
        or code.startswith(base_code)
        or code.startswith(base_code + "_")
        or code.startswith(base_code + "-")
        for code in expanded_codes[1:]
    ):
        return expanded_codes

    return [base_code]


def token_starts_code_section(token):
    cleaned = token.strip().strip(",")
    if not cleaned:
        return False
    if is_probable_typename(cleaned):
        return True
    if "(" in cleaned:
        prefix = cleaned.split("(", 1)[0].strip()
        if prefix and is_probable_typename(prefix):
            return True
    return False


def split_named_line_without_dash(line):
    tokens = line.split()
    for index in range(1, len(tokens)):
        if not token_starts_code_section(tokens[index]):
            continue
        name = " ".join(tokens[:index]).strip()
        code_section = " ".join(tokens[index:]).strip()
        if not name or not code_section:
            continue
        codes = parse_named_code_segment(code_section)
        if codes:
            return name, code_section
    return None, None


def make_entries_from_alias_and_codes(alias, codes, category):
    normalized_alias = normalize_display_name(alias)
    entries = []
    for code in codes:
        entry = BuilderEntry(
            alias=PLACEHOLDER_ALIAS,
            typename=PLACEHOLDER_TYPENAME,
            source_alias=normalized_alias,
            source_typename=code,
        )
        if category == "zombies":
            entry.is_boss = is_zomboss_entry(normalized_alias or code, [code])
        elif category == "plants":
            entry.include_entry = True
        elif category == "grid":
            entry.is_portal = is_portal_entry(normalized_alias or code, [code])
        entries.append(entry)
    return entries


def parse_plant_metadata(typename_with_meta):
    if not isinstance(typename_with_meta, str):
        return typename_with_meta, "0", ""

    parts = typename_with_meta.split(",", 1)
    if len(parts) == 1:
        part = parts[0].strip()
        if re.fullmatch(r"[\d.]+", part):
            return "", part, ""
        else:
            return part, "0", ""

    first = parts[0].strip()
    rest = parts[1].strip()

    if re.fullmatch(r"[\d.]+", first):
        return "", first, rest
    else:
        return first, "0", rest


def parse_plant_metadata_line(line):
    segments = split_pipe_items(line)
    if not segments:
        return None

    metadata = []
    for segment in segments:
        typename, gameversion, classname = parse_plant_metadata(segment)
        if typename:
            return None
        metadata.append((gameversion, classname))
    return metadata


def make_plant_entries_from_codes_and_metadata(codes, metadata=None):
    entries = []
    metadata = metadata or []

    for index, code in enumerate(codes):
        gameversion = "0"
        classname = ""
        if index < len(metadata):
            gameversion, classname = metadata[index]

        entry = BuilderEntry(
            alias=PLACEHOLDER_ALIAS,
            typename=PLACEHOLDER_TYPENAME,
            source_typename=code,
            plant_gameversion=gameversion,
            plant_classname=classname,
        )
        entry.include_entry = True
        entries.append(entry)

    return entries


def make_entries_from_codes(category, codes):
    entries = []
    for code in codes:
        if category == "plants":
            typename, gameversion, classname = parse_plant_metadata(code)
            entry = BuilderEntry(
                alias=PLACEHOLDER_ALIAS,
                typename=PLACEHOLDER_TYPENAME,
                source_typename=typename or code,
                plant_gameversion=gameversion,
                plant_classname=classname,
            )
            entry.include_entry = True
        else:
            entry = BuilderEntry(
                alias=PLACEHOLDER_ALIAS,
                typename=PLACEHOLDER_TYPENAME,
                source_typename=code,
            )
            if category == "zombies":
                entry.is_boss = is_zomboss_entry(code, [code])
            else:
                entry.is_portal = is_portal_entry(code, [code])
        entries.append(entry)
    return entries


def is_structured_entry_segment(segment):
    parts = [part.strip() for part in segment.split(",", 2)]
    return len(parts) == 3 and parts[0] in {"0", "1"} and bool(parts[2])


def parse_structured_entry_line(line, forced_category=None):
    raw_segments = split_pipe_items(line)
    segments = raw_segments or ([line.strip()] if line.strip() else [])
    if not segments or not all(is_structured_entry_segment(segment) for segment in segments):
        return None, []

    unpacked = []
    all_codes = []

    for segment in segments:
        flag, alias, code_spec = [part.strip() for part in segment.split(",", 2)]
        codes = filter_typenames(parse_code_segment(code_spec))
        if not codes:
            continue
        unpacked.append((flag, normalize_display_name(alias), codes))
        all_codes.extend(codes)

    if not unpacked:
        return None, []

    category = forced_category or classify_raw_codes(all_codes)
    entries = []

    for flag, alias, codes in unpacked:
        for code in codes:
            entry = BuilderEntry(alias=alias, typename=code)
            if category == "zombies":
                entry.is_boss = flag == "0" or is_zomboss_entry(alias, [code])
            elif category == "plants":
                entry.include_entry = flag != "0"
            else:
                entry.is_portal = flag == "0" or "portal" in alias.lower()
            entries.append(entry)

    return category, entries


def structured_entries_reference_codes(line, codes):
    _, entries = parse_structured_entry_line(line)
    if not entries:
        return False

    code_set = {code.strip() for code in codes if code.strip()}
    if not code_set:
        return False

    return all(entry.typename.strip() in code_set for entry in entries if entry.typename.strip())


def parse_pipe_codes(line):
    codes = []
    for item in split_pipe_items(line):
        codes.extend(parse_code_segment(item))
    return filter_typenames(codes)


def parse_general_line(line):
    category, structured_entries = parse_structured_entry_line(line)
    if structured_entries:
        return {category: structured_entries}

    if " - " in line:
        name, code_section = [part.strip() for part in line.split(" - ", 1)]
        codes = parse_named_code_segment(code_section)
        if not codes:
            return {}
        category = infer_category(name, codes)
        return {category: make_entries_from_alias_and_codes(name, codes, category)}

    name, code_section = split_named_line_without_dash(line)
    if name and code_section:
        codes = parse_named_code_segment(code_section)
        if codes:
            category = infer_category(name, codes)
            return {category: make_entries_from_alias_and_codes(name, codes, category)}

    if "," in line and "|" not in line:
        return {}

    if "|" in line:
        codes = parse_pipe_codes(line)
        if not codes:
            return {}
        category = classify_raw_codes(codes)
        return {category: make_entries_from_codes(category, codes)}

    codes = filter_typenames(parse_code_segment(line))
    if not codes:
        return {}

    category = classify_raw_codes(codes)
    return {category: make_entries_from_codes(category, codes)}


def parse_input_lines(lines):
    parsed = {category: [] for category in CATEGORY_ORDER}
    pending_codes = {category: [] for category in CATEGORY_ORDER}
    pending_grid_flags = []
    pending_plant_metadata = []
    current_section = None
    index = 0

    while index < len(lines):
        raw_line = lines[index]
        line = raw_line.strip()
        if not line:
            index += 1
            continue

        section = detect_section_header(line)
        if section:
            current_section = section
            index += 1
            continue

        if line.startswith("#"):
            index += 1
            continue

        if looks_like_heading(line):
            index += 1
            continue

        if current_section is None and "|" in line:
            lookahead_index = index + 1
            while lookahead_index < len(lines) and not lines[lookahead_index].strip():
                lookahead_index += 1

            if lookahead_index < len(lines):
                next_line = lines[lookahead_index].strip()
                codes = parse_pipe_codes(line)
                if codes:
                    category = classify_raw_codes(codes)
                    if structured_entries_reference_codes(next_line, codes):
                        index += 1
                        continue
                    if category == "grid" and is_grid_flag_list_line(next_line):
                        pending_codes["grid"].extend(codes)
                        pending_grid_flags.extend(split_pipe_items(next_line))
                        index = lookahead_index + 1
                        continue
                    metadata = parse_plant_metadata_line(next_line)
                    if (
                        metadata is not None
                        and category != "grid"
                        and not structured_entries_reference_codes(next_line, codes)
                    ):
                        parsed["plants"].extend(
                            make_plant_entries_from_codes_and_metadata(codes, metadata)
                        )
                        index = lookahead_index + 1
                        continue

        if current_section:
            category, mode = current_section
            if mode == "codes":
                codes = parse_pipe_codes(line) or filter_typenames(parse_code_segment(line))
                if codes:
                    pending_codes[category].extend(codes)
                    index += 1
                    continue
            elif mode == "entries":
                if category == "plants":
                    metadata = parse_plant_metadata_line(line)
                    if metadata is not None:
                        pending_plant_metadata.extend(metadata)
                        index += 1
                        continue
                forced_category, entries = parse_structured_entry_line(line, forced_category=category)
                if entries:
                    parsed[forced_category].extend(entries)
                    index += 1
                    continue
            elif mode == "flags":
                flags = split_pipe_items(line)
                if flags:
                    pending_grid_flags.extend(flags)
                    index += 1
                    continue

        general_entries = parse_general_line(line)
        for category, entries in general_entries.items():
            parsed[category].extend(entries)
        index += 1

    if not parsed["zombies"] and pending_codes["zombies"]:
        parsed["zombies"].extend(make_entries_from_codes("zombies", pending_codes["zombies"]))

    if not parsed["plants"] and pending_codes["plants"]:
        if pending_plant_metadata:
            parsed["plants"].extend(
                make_plant_entries_from_codes_and_metadata(
                    pending_codes["plants"],
                    pending_plant_metadata,
                )
            )
        else:
            parsed["plants"].extend(make_entries_from_codes("plants", pending_codes["plants"]))

    if not parsed["grid"] and pending_codes["grid"]:
        if pending_grid_flags and len(pending_grid_flags) >= len(pending_codes["grid"]):
            for code, flag in zip(pending_codes["grid"], pending_grid_flags):
                entry = BuilderEntry(
                    alias=PLACEHOLDER_ALIAS,
                    typename=PLACEHOLDER_TYPENAME,
                    source_typename=code,
                )
                entry.is_portal = flag.strip().startswith("0") or "portal" in flag.lower()
                parsed["grid"].append(entry)
        else:
            parsed["grid"].extend(make_entries_from_codes("grid", pending_codes["grid"]))

    return parsed["zombies"], parsed["plants"], parsed["grid"]


def build_zombie_output(zombies):
    codes = []
    entries = []
    for entry in zombies:
        source_typename = entry.source_typename.strip() or entry.typename.strip()
        if not source_typename:
            continue
        codes.append(source_typename)
        entries.append(f"{0 if entry.is_boss else 1},{effective_alias(entry)},{effective_typename(entry)}")
    return codes, entries


def build_plant_output(plants):
    codes = []
    entries = []
    for entry in plants:
        source_typename = entry.source_typename.strip() or entry.typename.strip()
        if not source_typename:
            continue

        plant_meta = entry.plant_gameversion or "0"
        if entry.plant_classname:
            plant_meta += f",{entry.plant_classname}"

        codes.append(source_typename)
        if entry.include_entry:
            entries.append(plant_meta)
    return codes, entries


def build_grid_output(grid_items):
    codes = []
    flags = []
    for entry in grid_items:
        source_typename = entry.source_typename.strip() or entry.typename.strip()
        if not source_typename:
            continue
        codes.append(source_typename)
        flags.append("0,Portal" if entry.is_portal else "1")
    return codes, flags


def build_output_sections(zombies, plants, grid_items):
    sections = {
        "full": "",
        "zombies": "",
        "plants": "",
        "grid": "",
        "zombie_codes_line": "",
        "zombie_entries_line": "",
        "plant_codes_line": "",
        "plant_entries_line": "",
        "grid_codes_line": "",
        "grid_flags_line": "",
    }
    blocks = []

    if zombies:
        zombie_codes, zombie_entries = build_zombie_output(zombies)
        sections["zombie_codes_line"] = pipe_join(zombie_codes)
        sections["zombie_entries_line"] = pipe_join(zombie_entries)
        sections["zombies"] = "\n".join(
            [
                "# Zombie codename list",
                sections["zombie_codes_line"],
                "",
                "# Zombie entry list",
                sections["zombie_entries_line"],
            ]
        ).strip()
        blocks.append(sections["zombies"])

    if plants:
        plant_codes, plant_entries = build_plant_output(plants)
        sections["plant_codes_line"] = pipe_join(plant_codes)
        sections["plant_entries_line"] = pipe_join(plant_entries)
        plant_block = ["# Plant codename list", sections["plant_codes_line"]]
        if plant_entries:
            plant_block.extend(["", "# Plant entry list", sections["plant_entries_line"]])
        sections["plants"] = "\n".join(plant_block).strip()
        blocks.append(sections["plants"])

    if grid_items:
        grid_codes, grid_flags = build_grid_output(grid_items)
        sections["grid_codes_line"] = pipe_join(grid_codes)
        sections["grid_flags_line"] = pipe_join(grid_flags)
        sections["grid"] = "\n".join(
            [
                "# Grid item codename list",
                sections["grid_codes_line"],
                "",
                "# Grid item flag list",
                sections["grid_flags_line"],
            ]
        ).strip()
        blocks.append(sections["grid"])

    sections["full"] = "\n\n".join(blocks).strip()
    return sections


def build_output_text(zombies, plants, grid_items):
    return build_output_sections(zombies, plants, grid_items)["full"]


def parse_mapping_text(mapping_text):
    lines = mapping_text.splitlines()
    return parse_input_lines(lines)


def run_cli(input_file=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    if input_file:
        with open(input_file, "r", encoding="utf-8") as file_obj:
            lines = file_obj.readlines()
    else:
        lines = sys.stdin.read().splitlines()

    zombies, plants, grid_items = parse_input_lines(lines)
    print(build_output_text(zombies, plants, grid_items))


def copy_to_clipboard(root, text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()


class ListBuilderApp:
    def __init__(self, root, initial_file=None):
        self.root = root
        self.root.title("ELM List Generator")
        self.root.geometry("1480x920")
        self.root.minsize(1240, 780)

        self.colors = {
            "bg": "#0f172a",
            "panel": "#111827",
            "surface": "#1f2937",
            "surface_alt": "#273449",
            "input_bg": "#0b1220",
            "text": "#e5e7eb",
            "muted": "#94a3b8",
            "accent": "#38bdf8",
        }

        self.entries = {category: [] for category in CATEGORY_ORDER}
        self.selected_indices = {category: None for category in CATEGORY_ORDER}
        self.category_views = {}
        self.output_boxes = {}
        self.output_sections = build_output_sections([], [], [])
        self._loading_editor = False

        self.summary_var = tk.StringVar(value="0 zombies | 0 plants | 0 grid items")
        self.status_var = tk.StringVar(value="Paste or load text on the left, then parse it into editable entries.")
        self.input_path_var = tk.StringVar(value="No file loaded")

        self._configure_styles()
        self._build_ui()
        self._bind_editor_traces()
        self.refresh_all_views()

        if initial_file:
            self.load_text_from_file(initial_file)
            self.parse_input(replace=True)

    def _configure_styles(self):
        self.root.configure(bg=self.colors["bg"])

        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("TFrame", background=self.colors["bg"])
        style.configure("Card.TFrame", background=self.colors["panel"])
        style.configure(
            "TLabelframe",
            background=self.colors["panel"],
            foreground=self.colors["text"],
            bordercolor=self.colors["surface_alt"],
            relief="solid",
        )
        style.configure(
            "TLabelframe.Label",
            background=self.colors["panel"],
            foreground=self.colors["text"],
        )
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["text"])
        style.configure("Muted.TLabel", background=self.colors["bg"], foreground=self.colors["muted"])
        style.configure(
            "TButton",
            background=self.colors["surface"],
            foreground=self.colors["text"],
            padding=(10, 6),
            borderwidth=1,
        )
        style.map(
            "TButton",
            background=[("active", self.colors["surface_alt"])],
            foreground=[("active", self.colors["text"])],
        )
        style.configure("Accent.TButton", background=self.colors["accent"], foreground="#08111f")
        style.map("Accent.TButton", background=[("active", "#7dd3fc")], foreground=[("active", "#08111f")])
        style.configure("TEntry", fieldbackground=self.colors["input_bg"], foreground=self.colors["text"])
        style.configure("TCheckbutton", background=self.colors["panel"], foreground=self.colors["text"])
        style.configure("Treeview", background=self.colors["input_bg"], fieldbackground=self.colors["input_bg"], foreground=self.colors["text"], rowheight=28)
        style.configure("Treeview.Heading", background=self.colors["surface"], foreground=self.colors["text"], relief="flat")
        style.map("Treeview", background=[("selected", self.colors["accent"])], foreground=[("selected", "#08111f")])
        style.configure("TNotebook", background=self.colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=self.colors["surface"], foreground=self.colors["text"], padding=(14, 8))
        style.map("TNotebook.Tab", background=[("selected", self.colors["surface_alt"])])

    def _build_ui(self):
        header = tk.Frame(self.root, bg=self.colors["bg"], padx=18, pady=16)
        header.pack(fill="x")

        title_label = tk.Label(
            header,
            text="ELM List Generator",
            bg=self.colors["bg"],
            fg=self.colors["text"],
            font=("Segoe UI Semibold", 20),
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header,
            text="Parse raw mapping text, organize entries one by one, and keep the final list visible while editing.",
            bg=self.colors["bg"],
            fg=self.colors["muted"],
            font=("Segoe UI", 10),
        )
        subtitle_label.pack(anchor="w", pady=(4, 0))

        summary_label = tk.Label(
            header,
            textvariable=self.summary_var,
            bg=self.colors["bg"],
            fg=self.colors["accent"],
            font=("Segoe UI Semibold", 10),
        )
        summary_label.pack(anchor="w", pady=(8, 0))

        toolbar = tk.Frame(self.root, bg=self.colors["bg"], padx=18, pady=0)
        toolbar.pack(fill="x", pady=(0, 12))

        ttk.Button(toolbar, text="Copy Full Output", style="Accent.TButton", command=self.copy_full_output).pack(side="left")
        ttk.Button(toolbar, text="Copy Current Preview", command=self.copy_current_preview).pack(side="left", padx=(8, 0))
        ttk.Button(toolbar, text="Save Full Output", command=self.save_full_output).pack(side="left", padx=(8, 0))
        ttk.Button(toolbar, text="Clear All Entries", command=self.clear_all_entries).pack(side="left", padx=(8, 0))

        main_pane = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill="both", expand=True, padx=18, pady=(0, 10))

        left_panel = ttk.Frame(main_pane)
        right_panel = ttk.Frame(main_pane)
        main_pane.add(left_panel, weight=2)
        main_pane.add(right_panel, weight=5)

        self._build_input_panel(left_panel)
        self._build_editor_panel(right_panel)

        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            anchor="w",
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            padx=14,
            pady=8,
        )
        status_bar.pack(fill="x", side="bottom")

    def _build_input_panel(self, parent):
        frame = ttk.LabelFrame(parent, text="Import / Scratchpad", padding=12)
        frame.pack(fill="both", expand=True)

        button_row = ttk.Frame(frame)
        button_row.pack(fill="x")

        ttk.Button(button_row, text="Load File", command=self.load_file_dialog).pack(side="left")
        ttk.Button(button_row, text="Clear Input", command=self.clear_input).pack(side="left", padx=(8, 0))

        category_row = ttk.Frame(frame)
        category_row.pack(fill="x", pady=(8, 0))

        ttk.Button(category_row, text="Import as Zombies", style="Accent.TButton", command=lambda: self.import_codenames_as_category("zombies")).pack(side="left")
        ttk.Button(category_row, text="Import as Plants", style="Accent.TButton", command=lambda: self.import_codenames_as_category("plants")).pack(side="left", padx=(8, 0))
        ttk.Button(category_row, text="Import as Grid Items", style="Accent.TButton", command=lambda: self.import_codenames_as_category("grid")).pack(side="left", padx=(8, 0))

        path_label = tk.Label(
            frame,
            textvariable=self.input_path_var,
            anchor="w",
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            font=("Segoe UI", 9),
        )
        path_label.pack(fill="x", pady=(10, 8))

        self.input_text = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            undo=True,
            height=22,
            bg=self.colors["input_bg"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            relief="flat",
            font=("Consolas", 10),
            padx=10,
            pady=10,
        )
        self.input_text.pack(fill="both", expand=True)

        hint = (
            "Paste or load codenames:\n"
            "code_a|code_b|code_c|\n\n"
            "Or use named format:\n"
            "Name - code_x/code_y/code_z\n\n"
            "Then click Import as [category]\n"
            "to assign the entire list."
        )
        hint_label = tk.Label(
            frame,
            text=hint,
            justify="left",
            anchor="w",
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            font=("Segoe UI", 9),
            wraplength=360,
        )
        hint_label.pack(fill="x", pady=(10, 0))

    def _build_editor_panel(self, parent):
        split = ttk.Panedwindow(parent, orient=tk.VERTICAL)
        split.pack(fill="both", expand=True)

        editor_frame = ttk.LabelFrame(split, text="Structured Editor", padding=10)
        output_frame = ttk.LabelFrame(split, text="Generated Output", padding=10)
        split.add(editor_frame, weight=3)
        split.add(output_frame, weight=2)

        self.editor_notebook = ttk.Notebook(editor_frame)
        self.editor_notebook.pack(fill="both", expand=True)

        for category in CATEGORY_ORDER:
            self._build_category_tab(category)

        preview_toolbar = ttk.Frame(output_frame)
        preview_toolbar.pack(fill="x", pady=(0, 8))

        ttk.Button(preview_toolbar, text="Copy Current Preview", command=self.copy_current_preview).pack(side="left")
        ttk.Button(preview_toolbar, text="Copy Full Output", command=self.copy_full_output).pack(side="left", padx=(8, 0))

        self.preview_notebook = ttk.Notebook(output_frame)
        self.preview_notebook.pack(fill="both", expand=True)

        for key, label in (
            ("full", "Full Output"),
            ("zombies", "Zombie Entry Line"),
            ("plants", "Plant Metadata Line"),
            ("grid", "Grid Flag Line"),
        ):
            tab = ttk.Frame(self.preview_notebook)
            self.preview_notebook.add(tab, text=label)

            text_box = scrolledtext.ScrolledText(
                tab,
                wrap=tk.WORD,
                bg=self.colors["input_bg"],
                fg=self.colors["text"],
                insertbackground=self.colors["text"],
                relief="flat",
                font=("Consolas", 10),
                padx=10,
                pady=10,
            )
            text_box.pack(fill="both", expand=True)
            text_box.config(state=tk.DISABLED)
            self.output_boxes[key] = text_box

    def _build_category_tab(self, category):
        tab = ttk.Frame(self.editor_notebook, padding=8)
        self.editor_notebook.add(tab, text=CATEGORY_LABELS[category])

        split = ttk.Panedwindow(tab, orient=tk.HORIZONTAL)
        split.pack(fill="both", expand=True)

        list_frame = ttk.LabelFrame(split, text=f"{CATEGORY_LABELS[category]} List", padding=8)
        editor_frame = ttk.LabelFrame(split, text="Selected Entry", padding=12)
        split.add(list_frame, weight=3)
        split.add(editor_frame, weight=2)

        toolbar = ttk.Frame(list_frame)
        toolbar.pack(fill="x", pady=(0, 8))

        ttk.Button(toolbar, text="Add", command=lambda c=category: self.add_entry(c)).pack(side="left")
        ttk.Button(toolbar, text="Duplicate", command=lambda c=category: self.duplicate_selected(c)).pack(side="left", padx=(8, 0))
        ttk.Button(toolbar, text="Remove", command=lambda c=category: self.remove_selected(c)).pack(side="left", padx=(8, 0))
        ttk.Button(toolbar, text="Up", command=lambda c=category: self.move_selected(c, -1)).pack(side="left", padx=(8, 0))
        ttk.Button(toolbar, text="Down", command=lambda c=category: self.move_selected(c, 1)).pack(side="left", padx=(8, 0))

        count_var = tk.StringVar(value="0 entries")
        count_label = tk.Label(
            toolbar,
            textvariable=count_var,
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            font=("Segoe UI", 9),
        )
        count_label.pack(side="right")

        tree_wrap = ttk.Frame(list_frame)
        tree_wrap.pack(fill="both", expand=True)
        tree_wrap.rowconfigure(0, weight=1)
        tree_wrap.columnconfigure(0, weight=1)

        tree = ttk.Treeview(tree_wrap, columns=("index", "mode", "alias", "typename"), show="headings", selectmode="browse")
        tree.heading("index", text="#")
        tree.heading("mode", text="Mode")
        tree.heading("alias", text="Aliases")
        tree.heading("typename", text="Typename")
        tree.column("index", width=46, stretch=False, anchor="center")
        tree.column("mode", width=120, stretch=False, anchor="center")
        tree.column("alias", width=250, anchor="w")
        tree.column("typename", width=250, anchor="w")
        tree.grid(row=0, column=0, sticky="nsew")

        tree_scroll = ttk.Scrollbar(tree_wrap, orient="vertical", command=tree.yview)
        tree_scroll.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=tree_scroll.set)
        tree.bind("<<TreeviewSelect>>", lambda _event, c=category: self.on_tree_selected(c))
        tree.bind("<Delete>", lambda _event, c=category: self.remove_selected(c))

        selection_var = tk.StringVar(value="Select an entry from the list or add a new one.")
        preview_var = tk.StringVar(value="")
        alias_var = tk.StringVar()
        typename_var = tk.StringVar()
        toggle_var = tk.BooleanVar(value=False)
        gameversion_var = tk.StringVar(value="0") if category == "plants" else None
        classname_var = tk.StringVar(value="") if category == "plants" else None

        editor_title = tk.Label(
            editor_frame,
            textvariable=selection_var,
            justify="left",
            anchor="w",
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("Segoe UI Semibold", 12),
            wraplength=360,
        )
        editor_title.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        ttk.Label(editor_frame, text="Aliases").grid(row=1, column=0, sticky="w")
        alias_entry = ttk.Entry(editor_frame, textvariable=alias_var)
        alias_entry.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(4, 10))

        ttk.Label(editor_frame, text="Typename").grid(row=3, column=0, sticky="w")
        typename_entry = ttk.Entry(editor_frame, textvariable=typename_var)
        typename_entry.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(4, 10))

        next_row = 5
        if category == "plants":
            ttk.Label(editor_frame, text="Game Version").grid(row=next_row, column=0, sticky="w")
            gameversion_entry = ttk.Entry(editor_frame, textvariable=gameversion_var, width=10)
            gameversion_entry.grid(row=next_row + 1, column=0, sticky="w", pady=(4, 6))

            ttk.Label(editor_frame, text="Class Name").grid(row=next_row, column=1, sticky="w")
            classname_entry = ttk.Entry(editor_frame, textvariable=classname_var)
            classname_entry.grid(row=next_row + 1, column=1, sticky="ew", pady=(4, 6))

            next_row += 2

        toggle = ttk.Checkbutton(editor_frame, text=self._toggle_label(category), variable=toggle_var)
        toggle.grid(row=next_row, column=0, columnspan=2, sticky="w", pady=(0, 10))

        guess_alias_button = ttk.Button(editor_frame, text="Guess Alias From Typename", command=lambda c=category: self.guess_alias(c))
        guess_alias_button.grid(row=next_row + 1, column=0, sticky="w")

        duplicate_button = ttk.Button(editor_frame, text="Duplicate Selected", command=lambda c=category: self.duplicate_selected(c))
        duplicate_button.grid(row=next_row + 1, column=1, sticky="e")

        ttk.Label(editor_frame, text="Generated Preview").grid(row=next_row + 2, column=0, columnspan=2, sticky="w", pady=(16, 4))
        preview_label = tk.Label(
            editor_frame,
            textvariable=preview_var,
            justify="left",
            anchor="nw",
            bg=self.colors["input_bg"],
            fg=self.colors["text"],
            padx=10,
            pady=10,
            relief="flat",
            wraplength=360,
            font=("Consolas", 10),
        )
        preview_label.grid(row=next_row + 3, column=0, columnspan=2, sticky="nsew")

        help_label = tk.Label(
            editor_frame,
            text=self._editor_help_text(category),
            justify="left",
            anchor="w",
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            wraplength=360,
            font=("Segoe UI", 9),
        )
        help_label.grid(row=next_row + 4, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        editor_frame.columnconfigure(0, weight=1)
        editor_frame.columnconfigure(1, weight=1)
        editor_frame.rowconfigure(next_row + 3, weight=1)

        widgets_list = [alias_entry, typename_entry, toggle, guess_alias_button, duplicate_button]
        if category == "plants":
            widgets_list.extend([gameversion_entry, classname_entry])

        self.category_views[category] = {
            "tree": tree,
            "count_var": count_var,
            "selection_var": selection_var,
            "preview_var": preview_var,
            "alias_var": alias_var,
            "typename_var": typename_var,
            "toggle_var": toggle_var,
            "gameversion_var": gameversion_var,
            "classname_var": classname_var,
            "widgets": widgets_list,
        }

        self.set_editor_enabled(category, False)

    def _bind_editor_traces(self):
        for category, view in self.category_views.items():
            view["alias_var"].trace_add("write", lambda *_args, c=category: self.on_editor_changed(c))
            view["typename_var"].trace_add("write", lambda *_args, c=category: self.on_editor_changed(c))
            view["toggle_var"].trace_add("write", lambda *_args, c=category: self.on_editor_changed(c))
            if category == "plants":
                if view.get("gameversion_var"):
                    view["gameversion_var"].trace_add("write", lambda *_args, c=category: self.on_editor_changed(c))
                if view.get("classname_var"):
                    view["classname_var"].trace_add("write", lambda *_args, c=category: self.on_editor_changed(c))

    def _toggle_label(self, category):
        if category == "zombies":
            return "Zomboss entry (outputs 0 instead of 1)"
        if category == "plants":
            return "Include this row in the plant metadata list"
        return "Portal flag (outputs 0,Portal)"

    def _editor_help_text(self, category):
        if category == "zombies":
            return "Zombie output format is exactly '1,Aliases,Typename|' for regular rows and '0,Aliases,Typename|' for Zomboss rows."
        if category == "plants":
            return "Plant output uses two lines: a plant codename list plus a metadata line such as '0,Appeasemint|' or '0|'."
        return "Grid items generate a flag line using either '1' or '0,Portal'."

    def current_preview_key(self):
        current_tab = self.preview_notebook.select()
        tab_index = self.preview_notebook.index(current_tab)
        return ("full", "zombies", "plants", "grid")[tab_index]

    def current_category(self):
        current_tab = self.editor_notebook.select()
        tab_index = self.editor_notebook.index(current_tab)
        return CATEGORY_ORDER[tab_index]

    def load_file_dialog(self):
        file_path = filedialog.askopenfilename(
            title="Open mapping file",
            filetypes=[("Text files", "*.txt"), ("All files", "*")],
        )
        if file_path:
            self.load_text_from_file(file_path)

    def load_text_from_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file_obj:
                content = file_obj.read()
        except OSError as exc:
            messagebox.showerror("Open file error", str(exc))
            return

        self.input_text.delete("1.0", tk.END)
        self.input_text.insert(tk.END, content)
        self.input_path_var.set(file_path)
        self.status_var.set("Loaded file into the input box.")

    def clear_input(self):
        self.input_text.delete("1.0", tk.END)
        self.input_path_var.set("No file loaded")
        self.status_var.set("Input box cleared.")

    def clear_all_entries(self):
        if not any(self.entries[category] for category in CATEGORY_ORDER):
            self.status_var.set("There are no entries to clear.")
            return

        if not messagebox.askyesno("Clear all entries", "Remove all parsed entries from the editor?"):
            return

        self.entries = {category: [] for category in CATEGORY_ORDER}
        self.selected_indices = {category: None for category in CATEGORY_ORDER}
        self.refresh_all_views()
        self.status_var.set("All parsed entries were cleared.")

    def parse_input(self, replace=True):
        raw_text = self.input_text.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showinfo("No input", "Paste or load some text first.")
            return

        zombies, plants, grid_items = parse_mapping_text(raw_text)
        imported_total = len(zombies) + len(plants) + len(grid_items)
        if imported_total == 0:
            messagebox.showinfo("Nothing parsed", "No supported entries were found in the input text.")
            return

        if replace:
            self.entries["zombies"] = zombies
            self.entries["plants"] = plants
            self.entries["grid"] = grid_items
            self.selected_indices = {category: None for category in CATEGORY_ORDER}
        else:
            self.entries["zombies"].extend(zombies)
            self.entries["plants"].extend(plants)
            self.entries["grid"].extend(grid_items)

        self.refresh_all_views()
        self.status_var.set(
            f"Imported {len(zombies)} zombies, {len(plants)} plants, and {len(grid_items)} grid items."
        )

    def import_codenames_as_category(self, category):
        raw_text = self.input_text.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showinfo("No input", "Paste some codenames first.")
            return

        all_codes = []

        for line in raw_text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if " - " in line:
                name, code_section = [part.strip() for part in line.split(" - ", 1)]
                codes = filter_typenames(parse_code_segment(code_section))
                all_codes.extend(codes)
            else:
                codes = split_pipe_items(line)
                all_codes.extend(codes)

        if not all_codes:
            messagebox.showinfo("Nothing parsed", "No codenames found in the input.")
            return

        entries = make_entries_from_codes(category, all_codes)
        self.entries[category] = entries
        self.selected_indices[category] = None

        self.refresh_all_views()
        self.status_var.set(f"Imported {len(entries)} {CATEGORY_LABELS[category].lower()} entries.")

    def refresh_all_views(self):
        for category in CATEGORY_ORDER:
            self.refresh_tree(category)
        self.refresh_output_previews()
        self.update_summary()

    def update_summary(self):
        self.summary_var.set(
            f"{len(self.entries['zombies'])} zombies | {len(self.entries['plants'])} plants | {len(self.entries['grid'])} grid items"
        )

    def refresh_tree(self, category):
        view = self.category_views[category]
        tree = view["tree"]
        tree.delete(*tree.get_children())

        for index, entry in enumerate(self.entries[category]):
            tree.insert("", "end", iid=str(index), values=self.tree_values(category, index, entry))

        count = len(self.entries[category])
        view["count_var"].set(f"{count} entries")

        if count == 0:
            self.selected_indices[category] = None
            self.load_selected_into_editor(category)
            return

        selected_index = self.selected_indices[category]
        if selected_index is None or selected_index >= count:
            selected_index = 0

        self.selected_indices[category] = selected_index
        tree.selection_set(str(selected_index))
        tree.focus(str(selected_index))
        tree.see(str(selected_index))
        self.load_selected_into_editor(category)

    def tree_values(self, category, index, entry):
        if category == "zombies":
            mode = "Zomboss" if entry.is_boss else "Regular"
        elif category == "plants":
            mode = "Metadata" if entry.include_entry else "Codes only"
        else:
            mode = "Portal" if entry.is_portal else "Normal"
        return (index + 1, mode, display_alias(entry), display_typename(entry))

    def on_tree_selected(self, category):
        selection = self.category_views[category]["tree"].selection()
        if not selection:
            self.selected_indices[category] = None
        else:
            self.selected_indices[category] = int(selection[0])
        self.load_selected_into_editor(category)

    def set_editor_enabled(self, category, enabled):
        for widget in self.category_views[category]["widgets"]:
            if enabled:
                widget.state(["!disabled"])
            else:
                widget.state(["disabled"])

    def load_selected_into_editor(self, category):
        view = self.category_views[category]
        index = self.selected_indices[category]

        if index is None or index >= len(self.entries[category]):
            self._loading_editor = True
            view["alias_var"].set("")
            view["typename_var"].set("")
            view["toggle_var"].set(False)
            if category == "plants":
                if view.get("gameversion_var"):
                    view["gameversion_var"].set("0")
                if view.get("classname_var"):
                    view["classname_var"].set("")
            self._loading_editor = False
            view["selection_var"].set("Select an entry from the list or add a new one.")
            view["preview_var"].set("")
            self.set_editor_enabled(category, False)
            return

        entry = self.entries[category][index]
        self.set_editor_enabled(category, True)
        self._loading_editor = True
        view["alias_var"].set(entry.alias)
        view["typename_var"].set(entry.typename)
        view["toggle_var"].set(self.entry_toggle_value(category, entry))
        if category == "plants":
            if view.get("gameversion_var"):
                view["gameversion_var"].set(entry.plant_gameversion)
            if view.get("classname_var"):
                view["classname_var"].set(entry.plant_classname)
        self._loading_editor = False
        view["selection_var"].set(
            f"Editing {CATEGORY_SINGULAR[category]} {index + 1} of {len(self.entries[category])}"
        )
        view["preview_var"].set(self.entry_preview_text(category, entry))

    def entry_toggle_value(self, category, entry):
        if category == "zombies":
            return entry.is_boss
        if category == "plants":
            return entry.include_entry
        return entry.is_portal

    def on_editor_changed(self, category):
        if self._loading_editor:
            return

        index = self.selected_indices[category]
        if index is None or index >= len(self.entries[category]):
            return

        view = self.category_views[category]
        entry = self.entries[category][index]
        entry.alias = normalize_display_name(view["alias_var"].get())
        entry.typename = view["typename_var"].get().strip()

        toggle_value = bool(view["toggle_var"].get())
        if category == "zombies":
            entry.is_boss = toggle_value
        elif category == "plants":
            entry.include_entry = toggle_value
            if view.get("gameversion_var"):
                entry.plant_gameversion = view["gameversion_var"].get().strip() or "0"
            if view.get("classname_var"):
                entry.plant_classname = view["classname_var"].get().strip()
        else:
            entry.is_portal = toggle_value

        self.refresh_tree_row(category, index)
        view["preview_var"].set(self.entry_preview_text(category, entry))
        self.refresh_output_previews()
        self.update_summary()

    def refresh_tree_row(self, category, index):
        tree = self.category_views[category]["tree"]
        if tree.exists(str(index)):
            tree.item(str(index), values=self.tree_values(category, index, self.entries[category][index]))

    def entry_preview_text(self, category, entry):
        typename = effective_typename(entry)
        alias = effective_alias(entry)

        if category == "zombies":
            return f"{0 if entry.is_boss else 1},{alias},{typename}|"

        if category == "plants":
            plant_meta = entry.plant_gameversion
            if entry.plant_classname:
                plant_meta += f",{entry.plant_classname}"
            if entry.include_entry:
                return f"{plant_meta}|"
            return "(not included in plant metadata list)"

        flag_row = "0,Portal" if entry.is_portal else "1"
        return f"{flag_row}|"

    def add_entry(self, category):
        entry = BuilderEntry(alias=PLACEHOLDER_ALIAS, typename=PLACEHOLDER_TYPENAME)
        if category == "plants":
            entry.include_entry = True
            entry.plant_gameversion = "0"
            entry.plant_classname = ""
        self.entries[category].append(entry)
        self.selected_indices[category] = len(self.entries[category]) - 1
        self.refresh_tree(category)
        self.refresh_output_previews()
        self.update_summary()
        self.status_var.set(f"Added a new {CATEGORY_SINGULAR[category].lower()} entry.")

    def duplicate_selected(self, category):
        index = self.selected_indices[category]
        if index is None or index >= len(self.entries[category]):
            self.status_var.set(f"Select a {CATEGORY_SINGULAR[category].lower()} entry to duplicate.")
            return

        entry = self.entries[category][index]
        duplicate = BuilderEntry(
            alias=entry.alias,
            typename=entry.typename,
            is_boss=entry.is_boss,
            include_entry=entry.include_entry,
            is_portal=entry.is_portal,
            source_alias=entry.source_alias,
            source_typename=entry.source_typename,
            plant_gameversion=entry.plant_gameversion,
            plant_classname=entry.plant_classname,
        )
        self.entries[category].insert(index + 1, duplicate)
        self.selected_indices[category] = index + 1
        self.refresh_tree(category)
        self.refresh_output_previews()
        self.update_summary()
        self.status_var.set(f"Duplicated {CATEGORY_SINGULAR[category].lower()} entry {index + 1}.")

    def remove_selected(self, category):
        index = self.selected_indices[category]
        if index is None or index >= len(self.entries[category]):
            self.status_var.set(f"Select a {CATEGORY_SINGULAR[category].lower()} entry to remove.")
            return "break"

        del self.entries[category][index]
        if self.entries[category]:
            self.selected_indices[category] = min(index, len(self.entries[category]) - 1)
        else:
            self.selected_indices[category] = None
        self.refresh_tree(category)
        self.refresh_output_previews()
        self.update_summary()
        self.status_var.set(f"Removed {CATEGORY_SINGULAR[category].lower()} entry {index + 1}.")
        return "break"

    def move_selected(self, category, delta):
        index = self.selected_indices[category]
        if index is None or index >= len(self.entries[category]):
            self.status_var.set(f"Select a {CATEGORY_SINGULAR[category].lower()} entry to move.")
            return

        new_index = index + delta
        if new_index < 0 or new_index >= len(self.entries[category]):
            return

        self.entries[category][index], self.entries[category][new_index] = (
            self.entries[category][new_index],
            self.entries[category][index],
        )
        self.selected_indices[category] = new_index
        self.refresh_tree(category)
        self.refresh_output_previews()
        self.status_var.set(
            f"Moved {CATEGORY_SINGULAR[category].lower()} entry to position {new_index + 1}."
        )

    def guess_alias(self, category):
        index = self.selected_indices[category]
        if index is None or index >= len(self.entries[category]):
            self.status_var.set(f"Select a {CATEGORY_SINGULAR[category].lower()} entry first.")
            return

        typename = self.category_views[category]["typename_var"].get().strip()
        if not typename:
            self.status_var.set("Typename is empty, so there is nothing to turn into an alias yet.")
            return

        self.category_views[category]["alias_var"].set(humanize_typename(typename))
        self.status_var.set("Alias filled from typename.")

    def refresh_output_previews(self):
        self.output_sections = build_output_sections(
            self.entries["zombies"],
            self.entries["plants"],
            self.entries["grid"],
        )

        preview_text = {
            "full": self.output_sections["full"] or "Nothing generated yet.",
            "zombies": self.output_sections["zombie_entries_line"] or "1,Alias,Typename|1,Alias,Typename|...",
            "plants": self.output_sections["plant_entries_line"] or "0,Appeasemint|0,Enlightenmint,SunProducer|...",
            "grid": self.output_sections["grid_flags_line"] or "1|1|0,Portal|...",
        }

        for key, widget in self.output_boxes.items():
            widget.config(state=tk.NORMAL)
            widget.delete("1.0", tk.END)
            widget.insert(tk.END, preview_text[key])
            widget.config(state=tk.DISABLED)

    def copy_current_preview(self):
        key = self.current_preview_key()
        text = self.output_boxes[key].get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Copy preview", "There is no preview text to copy.")
            return
        copy_to_clipboard(self.root, text)
        self.status_var.set("Copied the current preview.")

    def copy_full_output(self):
        text = self.output_sections["full"].strip()
        if not text:
            messagebox.showinfo("Copy full output", "There is no generated output to copy yet.")
            return
        copy_to_clipboard(self.root, text)
        self.status_var.set("Copied the full output.")

    def save_full_output(self):
        text = self.output_sections["full"].strip()
        if not text:
            messagebox.showwarning("Save output", "There is no generated output to save yet.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save output as",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*")],
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as file_obj:
                file_obj.write(text)
        except OSError as exc:
            messagebox.showerror("Save file error", str(exc))
            return

        self.status_var.set("Saved the full output to disk.")


def create_gui(initial_file=None):
    configure_tk_environment()
    root = tk.Tk()
    ListBuilderApp(root, initial_file=initial_file)
    return root


def main():
    parser = argparse.ArgumentParser(
        description="ELM list generator with a structured Tkinter editor. Use --nogui for console mode."
    )
    parser.add_argument("input_file", nargs="?", help="Optional text file to load into the GUI or process in CLI mode.")
    parser.add_argument("--nogui", action="store_true", help="Run in console mode and print the generated output.")
    args = parser.parse_args()

    if args.nogui:
        run_cli(args.input_file)
        return

    root = create_gui(initial_file=args.input_file)
    root.mainloop()


if __name__ == "__main__":
    main()
