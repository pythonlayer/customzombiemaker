import copy
import json
import random
import re
import sys
from pathlib import Path

APP_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))

templates=["farfuture"]
chosenone=random.choice(templates)
DEFAULT_TEMPLATE_PATH = Path(chosenone+".json")
DEFAULT_TYPES_PATH = Path("ZOMBIETYPES_UPDATED.json")
DEFAULT_PROPS_PATH = Path("ZOMBIEPROPERTIES_UPDATED.json")

DEFAULT_AMBUSH_WAVE_MESSAGES = {
    "egypt_imp": "Feline Frenzy!",
    "pirate_imp": "Swab the Deck!",
    "west_bull": "Stampede!",
    "west_bullrider": "Rodeo Tournament!",
    "future_imp": "Bot Swarm!",
    "dark_imp": "Enlightnement!",
    "dark_imp_dragon": "Dragon's Spell",
    "beach_imp": "Mermaid Magic!",
    "beach_greaser_imp": "Drop in Style!",
    "greaser_imp": "Drop in Style!",
    "summer_greaser_imp": "Drop in Style!",
    "iceage_imp": "Avalanche!",
    "lostcity_imp": "Plane Dropoff!",
    "lostcity_lostpilot": "Parachute Rain!",
    "eighties_imp": "Mosh Pit!",
    "dino_imp": "Caveimps!",
    "dino_eggshell": "Dinosaur's Eggs!",
    "tutorial_imp": "Imp Rain!",
    "modern_superfanimp": "Adoration Scourge!",
    "valentines_imp": "Cupid's Arrow!",
    "valentines_superfanimp": "Love in the Air!",
    "leprachaun_imp": "Leprechauns!",
    "spring_imp": "Egg Raid!",
    "birthday_imp": "Pesky Presents!",
    "children_imp": "Recess!",
    "childrensday_imp": "Cub Club!",
    "summer_imp": "Hot Dogs!",
    "bighead_imp": "Crash Course!",
    "bighead_superfan": "Big Bang!",
    "halloween_imp": "Bridal Shower!",
    "hero_impfinity": "Impfinity Clones!",
    "hero_neptuna": "Heart of the Sea!",
    "foodfight_imp": "Taco Tuesday!",
    "feastivus_imp": "Sweater Swarm!",
    "holiday_imp": "Santa's Little Helpers!",
    "zcorp_imp": "Corporal Punishment!",
    "zcorp_helpdesk": "Tech support!",
    "lunar_imp": "Sheep Attack!",
    "lunar_superfanimp": "Lunar Landing!",
    "harvest_imp": "Feathery Frenzy!",
    "harvest_eggshell": "Eggstravaganza!",
    "sportzball_imp": "GOOOOOOOOOOOOOOOOOOOOOOAL!",
    "steam_imp": "Overtime!",
    "steam_back_imp": "!nalP pukcaB",
    "steam_miner_coal": "Shipment!",
    "carnie_imp_twins": "Twinsanity!",
    "carnie_imp_split": "Solo Performance!",
    "carnie_toy_ball": "Bonus Balls!",
    "carnie_imp": "Cannonballs!",
    "carnie_toy_gargantuar": "Plastic Plunge!",
    "imppear_imp": "Mysterious Origin!",
    "rift_sniffer_rain": "Dangerous Whiff!",
    "rift_imp": "Lunch Break!",
    "rift_imp_wrench": "Lunch Break!",
    "rift_imp_sandwich": "Lunch Break!",
    "rift_gargimp": "Miniature Might!",
    "zcorp_racer": "Corporal Stunt!",
}

PORTAL_WORLD_NAMES = {
    "egypt",
    "pirate",
    "west",
    "future",
    "dark",
    "beach",
    "lostcity",
    "iceage",
    "eighties",
    "dino",
    "modern",
    "holiday",
    "steam",
    "carnival",
    "hollows",
    "skycity",
    "travellog",
}

PORTAL_HOMEWORLD_ALIASES = {
    "cowboy": "west",
    "rift1a": "travellog",
    "rift2": "travellog",
    "tutorial": "modern",
    "zombotany": "modern",
}

DEFAULT_GENERATED_PORTAL_GROUP_MODES = (
    "same_world",
    "same_cost",
    "same_suffix",
    "random",
)

DEFAULT_STAMPEDE_MODULES = [
    "RTID(StandardIntro@LevelModules)",
    "RTID(StampedeDinoSpawns@LevelModules)",
]

def generate_random_railcarts():
    rails = []
    railcarts = []
    num_rails = random.randint(3, 5)
    for _ in range(num_rails):
        column = random.randint(0, 8)
        row_start = random.randint(0, 3)
        length = random.randint(2, 5)
        row_end = min(row_start + length - 1, 4)
        rails.append({"Column": column, "RowEnd": row_end, "RowStart": row_start})
        max_carts = 1
        if length >= 3:
            max_carts = 2
        if length >= 5:
            max_carts = 3
        num_carts = 1
        if random.random() < 0.3:  # 30% chance for more
            num_carts = random.randint(1, max_carts)
        rows = list(range(row_start, row_end + 1))
        random.shuffle(rows)
        for i in range(num_carts):
            if i < len(rows):
                railcarts.append({"Column": column, "Row": rows[i]})
    return {
        "RailcartType": "",
        "Railcarts": railcarts,
        "Rails": rails
    }

DEFAULT_JAM_STAGE_MODULES = [
    "RTID(EightiesStage@LevelModules)",
    "RTID(EightiesAltverzStage@LevelModules)",
    "RTID(FrontLawnEightiesStage@LevelModules)",
    "RTID(ModernAllJamsStage@LevelModules)",
]

DEFAULT_JAM_STYLE_OVERRIDES = {
    "eighties_gargantuar": "jam_metal",
    "eighties_imp": "jam_metal",
    "eighties_boombox_8bit": "jam_8bit",
    "eighties_gargantuar_8bit": "jam_8bit",
    "eighties_armor1": "jam_all",
    "eighties_armor2": "jam_all",
    "eighties_armor4": "jam_all",
}

JAM_ALL_STYLE = "jam_all"

DINO_PTERO_SUPPORT_ZOMBIES = {
    "dino",
    "dino_armor1",
    "dino_armor2",
    "dino_armor3",
    "dino_armor4",
    "dino_bully",
    "dino_bully_veteran",
}


def resolve_input_path(path):
    candidate = Path(path)
    if candidate.is_absolute() or candidate.exists():
        return candidate

    bundled_candidate = APP_DIR / candidate
    if bundled_candidate.exists():
        return bundled_candidate

    script_candidate = Path(__file__).resolve().parent / candidate
    if script_candidate.exists():
        return script_candidate

    return candidate


def load_json_file(path, label):
    resolved_path = resolve_input_path(path)
    try:
        with resolved_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"{label} file not found: {resolved_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} file is not valid JSON: {resolved_path} ({exc})") from exc


def as_number(value, field_name):
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a number, got boolean")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a number, got {value!r}") from exc


def as_int(value, field_name):
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be an integer, got boolean")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer, got {value!r}") from exc


def parse_int_range(raw_range, field_name):
    if not isinstance(raw_range, list) or len(raw_range) != 2:
        raise ValueError(f"{field_name} must be [min, max]")
    low = as_int(raw_range[0], f"{field_name}[0]")
    high = as_int(raw_range[1], f"{field_name}[1]")
    if low > high:
        raise ValueError(f"{field_name} min cannot be greater than max")
    return low, high


def parse_float_range(raw_range, field_name):
    if not isinstance(raw_range, list) or len(raw_range) != 2:
        raise ValueError(f"{field_name} must be [min, max]")
    low = as_number(raw_range[0], f"{field_name}[0]")
    high = as_number(raw_range[1], f"{field_name}[1]")
    if low > high:
        raise ValueError(f"{field_name} min cannot be greater than max")
    return low, high


def extract_rtid_name(rtid, field_name):
    if not isinstance(rtid, str):
        raise ValueError(f"{field_name} must be an RTID string")
    match = re.search(r"RTID\((.+?)@", rtid)
    if not match:
        raise ValueError(f"{field_name} is not a valid RTID string: {rtid!r}")
    return match.group(1)


def make_alias_lookup(objects):
    lookup = {}
    for obj in objects:
        aliases = obj.get("aliases")
        if not isinstance(aliases, list):
            continue
        for alias in aliases:
            if isinstance(alias, str) and alias and alias not in lookup:
                lookup[alias] = obj
    return lookup


def get_zombie_type_aliases(types_objects):
    alias_set = set()
    for obj in types_objects:
        if obj.get("objclass") != "ZombieType":
            continue
        aliases = obj.get("aliases")
        if not isinstance(aliases, list):
            continue
        for alias in aliases:
            if isinstance(alias, str) and alias:
                alias_set.add(alias)
    return alias_set


def make_unique_alias(base_alias, existing_aliases):
    alias = base_alias
    idx = 2
    while alias in existing_aliases:
        alias = f"{base_alias}_{idx}"
        idx += 1
    existing_aliases.add(alias)
    return alias


def normalize_portal_world_name(world_name, fallback_world="modern"):
    cleaned = str(world_name or "").strip().lower()
    cleaned = PORTAL_HOMEWORLD_ALIASES.get(cleaned, cleaned)
    if cleaned in PORTAL_WORLD_NAMES:
        return cleaned
    return fallback_world


def parse_portal_world_name(value, field_name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    cleaned = normalize_portal_world_name(value, fallback_world="")
    if cleaned not in PORTAL_WORLD_NAMES:
        raise ValueError(
            f"{field_name} must be one of: " + ", ".join(sorted(PORTAL_WORLD_NAMES))
        )
    return cleaned


def extract_portal_group_suffix(zombie_alias):
    parts = [part for part in str(zombie_alias).strip().split("_") if part]
    while parts and (parts[-1] == "veteran" or re.fullmatch(r"armor\d+", parts[-1])):
        parts.pop()
    return parts[-1] if parts else str(zombie_alias).strip()


def build_zombie_type_metadata(types_objects):
    metadata = {}
    for obj in types_objects:
        if obj.get("objclass") != "ZombieType":
            continue
        aliases = obj.get("aliases")
        if not isinstance(aliases, list):
            continue
        objdata = obj.get("objdata", {})
        raw_home_world = str(objdata.get("HomeWorld", "")).strip().lower()
        portal_world = normalize_portal_world_name(raw_home_world)
        for alias in aliases:
            if not isinstance(alias, str) or not alias:
                continue
            metadata[alias] = {
                "raw_home_world": raw_home_world,
                "portal_world": portal_world,
                "suffix": extract_portal_group_suffix(alias),
            }
    return metadata


def normalize_generated_portal_group_modes(raw_modes, field_name):
    if raw_modes is None:
        return list(DEFAULT_GENERATED_PORTAL_GROUP_MODES)
    if not isinstance(raw_modes, list) or len(raw_modes) == 0:
        raise ValueError(f"{field_name} must be a non-empty array")

    modes = []
    valid_modes = set(DEFAULT_GENERATED_PORTAL_GROUP_MODES)
    for idx, raw_mode in enumerate(raw_modes):
        if not isinstance(raw_mode, str) or not raw_mode.strip():
            raise ValueError(f"{field_name}[{idx}] must be a non-empty string")
        mode = raw_mode.strip().lower()
        if mode not in valid_modes:
            raise ValueError(
                f"{field_name}[{idx}] must be one of: "
                + ", ".join(DEFAULT_GENERATED_PORTAL_GROUP_MODES)
            )
        if mode not in modes:
            modes.append(mode)
    return modes


def collect_event_zombie_aliases(events_cfg):
    aliases = set()
    if not isinstance(events_cfg, dict):
        return aliases

    imp_cfgs = events_cfg.get("imp_ambushes", [])
    if isinstance(imp_cfgs, list):
        for imp_cfg in imp_cfgs:
            if not isinstance(imp_cfg, dict):
                continue
            spider_name = imp_cfg.get("spider_zombie_name")
            if isinstance(spider_name, str) and spider_name.strip():
                aliases.add(spider_name.strip())
    parachute_cfgs = events_cfg.get("parachute_rains", [])
    if isinstance(parachute_cfgs, list):
        for parachute_cfg in parachute_cfgs:
            if not isinstance(parachute_cfg, dict):
                continue
            spider_name = parachute_cfg.get("spider_zombie_name", parachute_cfg.get("SpiderZombieName"))
            spider_alias = optional_zombie_alias(spider_name)
            if spider_alias:
                aliases.add(spider_alias)
            aliases.update(
                collect_zombie_aliases_from_entries(
                    parachute_cfg.get(
                        "spider_zombie_pool",
                        parachute_cfg.get("SpiderZombiePool", parachute_cfg.get("zombie_pool")),
                    ),
                    value_keys=("SpiderZombieName", "spider_zombie_name", "zombie_name", "type_name", "type", "Type"),
                )
            )
    for array_name in ("storm_ambushes", "sandstorm_ambushes", "snowstorm_ambushes"):
        storm_cfgs = events_cfg.get(array_name, [])
        if not isinstance(storm_cfgs, list):
            continue
        for storm_cfg in storm_cfgs:
            if not isinstance(storm_cfg, dict):
                continue
            aliases.update(collect_zombie_aliases_from_entries(storm_cfg.get("zombie_pool", [])))
            spawners = storm_cfg.get("spawners", [])
            if isinstance(spawners, list):
                for spawner in spawners:
                    if not isinstance(spawner, dict):
                        continue
                    aliases.update(collect_zombie_aliases_from_entries(spawner.get("zombies", [])))
    low_tide_cfgs = events_cfg.get("low_tides", [])
    if isinstance(low_tide_cfgs, list):
        for tide_cfg in low_tide_cfgs:
            if not isinstance(tide_cfg, dict):
                continue
            zombie_name = tide_cfg.get("zombie_name")
            if isinstance(zombie_name, str) and zombie_name.strip():
                aliases.add(zombie_name.strip())
            zombie_names = tide_cfg.get("zombie_names", [])
            if isinstance(zombie_names, list):
                for zombie_alias in zombie_names:
                    if isinstance(zombie_alias, str) and zombie_alias.strip():
                        aliases.add(zombie_alias.strip())
            variants = tide_cfg.get("variants", [])
            if isinstance(variants, list):
                for variant_cfg in variants:
                    if not isinstance(variant_cfg, dict):
                        continue
                    zombie_name = variant_cfg.get("zombie_name")
                    if isinstance(zombie_name, str) and zombie_name.strip():
                        aliases.add(zombie_name.strip())
    necro_cfgs = events_cfg.get("necromancy_spawns", [])
    if isinstance(necro_cfgs, list):
        for necro_cfg in necro_cfgs:
            if not isinstance(necro_cfg, dict):
                continue
            aliases.update(
                collect_zombie_aliases_from_entries(
                    necro_cfg.get("zombies", necro_cfg.get("Zombies")),
                )
            )
            aliases.update(
                collect_zombie_aliases_from_entries(
                    necro_cfg.get("zombie_pool", necro_cfg.get("ZombiePool")),
                )
            )

    generated_portal_cfg = events_cfg.get("generated_portals", {})
    if isinstance(generated_portal_cfg, dict):
        aliases.update(
            collect_zombie_aliases_from_entries(
                generated_portal_cfg.get("zombie_pool", []),
            )
        )

    return aliases


def collect_initial_zombie_aliases(initial_cfg, variant_alias_to_roll=None):
    if not isinstance(initial_cfg, dict) or not initial_cfg.get("enabled", False):
        return set()

    raw_pool = initial_cfg.get("pool", initial_cfg.get("zombie_pool"))
    if raw_pool is None:
        return set()

    aliases = collect_zombie_aliases_from_entries(raw_pool)
    if variant_alias_to_roll is not None:
        return {
            canonicalize_zombie_alias(alias, variant_alias_to_roll)
            for alias in aliases
        }
    return aliases


def resolve_zombie_weights(selected_pool, types_objects, props_objects):
    type_lookup = {}
    for obj in types_objects:
        if obj.get("objclass") != "ZombieType":
            continue
        aliases = obj.get("aliases")
        if not isinstance(aliases, list):
            continue
        for alias in aliases:
            if isinstance(alias, str) and alias and alias not in type_lookup:
                type_lookup[alias] = obj

    props_lookup = make_alias_lookup(props_objects)

    zombie_costs = {}
    errors = []

    for zombie_alias in selected_pool:
        type_entry = type_lookup.get(zombie_alias)
        if type_entry is None:
            errors.append(f'"{zombie_alias}": alias not found in ZombieTypes')
            continue

        properties_rtid = type_entry.get("objdata", {}).get("Properties")
        if not properties_rtid:
            errors.append(f'"{zombie_alias}": missing objdata.Properties in ZombieTypes')
            continue

        try:
            props_alias = extract_rtid_name(
                properties_rtid,
                f"ZombieTypes[{zombie_alias}].objdata.Properties",
            )
        except ValueError as exc:
            errors.append(f'"{zombie_alias}": {exc}')
            continue

        props_entry = props_lookup.get(props_alias)
        if props_entry is None:
            errors.append(
                f'"{zombie_alias}": properties alias "{props_alias}" not found in ZombieProperties'
            )
            continue

        cost_raw = props_entry.get("objdata", {}).get("WavePointCost")
        if cost_raw is None:
            errors.append(
                f'"{zombie_alias}": properties "{props_alias}" missing objdata.WavePointCost'
            )
            continue

        try:
            cost_value = as_number(
                cost_raw,
                f"ZombieProperties[{props_alias}].objdata.WavePointCost",
            )
        except ValueError as exc:
            errors.append(f'"{zombie_alias}": {exc}')
            continue

        zombie_costs[zombie_alias] = cost_value / 100.0

    if errors:
        raise ValueError("Zombie weight extraction failed:\n- " + "\n- ".join(errors))
    return zombie_costs


def resolve_zombie_jam_styles(selected_pool, types_objects, props_objects, overrides=None):
    type_lookup = {}
    for obj in types_objects:
        if obj.get("objclass") != "ZombieType":
            continue
        aliases = obj.get("aliases")
        if not isinstance(aliases, list):
            continue
        for alias in aliases:
            if isinstance(alias, str) and alias and alias not in type_lookup:
                type_lookup[alias] = obj

    props_lookup = make_alias_lookup(props_objects)
    overrides = overrides or {}
    jam_styles = {}

    for zombie_alias in selected_pool:
        override_style = overrides.get(zombie_alias)
        if isinstance(override_style, str) and override_style.strip():
            jam_styles[zombie_alias] = override_style.strip()
            continue

        type_entry = type_lookup.get(zombie_alias)
        if type_entry is None:
            continue

        properties_rtid = type_entry.get("objdata", {}).get("Properties")
        if not properties_rtid:
            continue

        try:
            props_alias = extract_rtid_name(
                properties_rtid,
                f"ZombieTypes[{zombie_alias}].objdata.Properties",
            )
        except ValueError:
            continue

        props_entry = props_lookup.get(props_alias)
        if props_entry is None:
            continue

        jam_style = props_entry.get("objdata", {}).get("JamStyle")
        if isinstance(jam_style, str) and jam_style.strip():
            jam_styles[zombie_alias] = jam_style.strip()

    return jam_styles


def pop_required_zombie(required_zombies, zombie_costs, max_cost, validator=None):
    for idx, zombie_name in enumerate(required_zombies):
        if zombie_costs[zombie_name] > (max_cost + 1e-9):
            continue
        if validator is not None and not validator(zombie_name):
            continue
        return required_zombies.pop(idx)
    return None


def normalize_string_list(value, field_name):
    if value is None:
        return []
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(f"{field_name} must not be empty")
        return [cleaned]
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a string or array of strings")

    cleaned_values = []
    for idx, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field_name}[{idx}] must be a non-empty string")
        cleaned_values.append(item.strip())
    return cleaned_values


def normalize_int_list(value, field_name):
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be an array of integers")

    cleaned_values = []
    for idx, item in enumerate(value):
        cleaned_values.append(as_int(item, f"{field_name}[{idx}]"))
    return cleaned_values


def get_config_weight(config, field_name, default=1.0):
    weight = as_number(config.get("weight", default), field_name)
    if weight < 0:
        raise ValueError(f"{field_name} cannot be negative")
    return weight


def pick_weighted_dict(entries, field_name):
    total_weight = sum(entry["weight"] for entry in entries)
    if total_weight <= 0:
        raise ValueError(f"{field_name} must contain at least one entry with weight > 0")

    roll = random.uniform(0.0, total_weight)
    running = 0.0
    for entry in entries:
        running += entry["weight"]
        if roll <= running:
            return entry
    return entries[-1]


def resolve_wave_structure(wave_cfg):
    def pick_wave_int(field_name, range_field_name, default_range):
        if field_name in wave_cfg:
            value = as_int(wave_cfg.get(field_name), f"wave_settings.{field_name}")
        else:
            raw_range = wave_cfg.get(range_field_name)
            if raw_range is None:
                low, high = default_range
            else:
                low, high = parse_int_range(raw_range, f"wave_settings.{range_field_name}")
            value = random.randint(low, high)
        if value <= 0:
            raise ValueError(f"wave_settings.{field_name} must be > 0")
        return value

    flag_interval = pick_wave_int("flag_interval", "flag_interval_range", (7, 10))

    explicit_wave_count = wave_cfg.get("wave_count")
    if explicit_wave_count is not None:
        wave_count = as_int(explicit_wave_count, "wave_settings.wave_count")
        if wave_count <= 0:
            raise ValueError("wave_settings.wave_count must be > 0")

        if "flag_count" in wave_cfg or "flag_count_range" in wave_cfg:
            flag_count = pick_wave_int("flag_count", "flag_count_range", (1, 4))
            expected_wave_count = flag_interval * flag_count
            if wave_count != expected_wave_count:
                raise ValueError(
                    "wave_settings.wave_count must equal "
                    "wave_settings.flag_interval * wave_settings.flag_count"
                )
        else:
            if wave_count % flag_interval != 0:
                raise ValueError(
                    "wave_settings.wave_count must be divisible by "
                    "wave_settings.flag_interval when flag_count is omitted"
                )
            flag_count = wave_count // flag_interval
    else:
        flag_count = pick_wave_int("flag_count", "flag_count_range", (1, 4))
        wave_count = flag_interval * flag_count

    return flag_interval, flag_count, wave_count


def build_plantfood_waves(wave_cfg, wave_count, flag_interval):
    plantfood_mode = str(wave_cfg.get("plantfood_mode", "auto")).strip().lower()
    if plantfood_mode == "auto":
        plantfood_mode = "interval_jittered" if "plantfood_interval" in wave_cfg else "count_range"

    if plantfood_mode == "count_range":
        min_pf = as_int(wave_cfg.get("min_pf", 1), "wave_settings.min_pf")
        max_pf = as_int(wave_cfg.get("max_pf", 3), "wave_settings.max_pf")
        if max_pf < min_pf:
            raise ValueError("wave_settings.max_pf cannot be lower than wave_settings.min_pf")
        pf_count = min(random.randint(min_pf, max_pf), wave_count)
        return set(random.sample(range(1, wave_count + 1), pf_count))

    if plantfood_mode == "fixed_count":
        pf_count = as_int(wave_cfg.get("plantfood_count", 0), "wave_settings.plantfood_count")
        pf_count = max(0, min(pf_count, wave_count))
        return set(random.sample(range(1, wave_count + 1), pf_count))

    if plantfood_mode in {"interval", "interval_jittered"}:
        interval = as_int(wave_cfg.get("plantfood_interval", 8), "wave_settings.plantfood_interval")
        per_interval = as_int(
            wave_cfg.get("plantfood_per_interval", 1),
            "wave_settings.plantfood_per_interval",
        )
        if interval <= 0:
            raise ValueError("wave_settings.plantfood_interval must be > 0")
        if per_interval < 0:
            raise ValueError("wave_settings.plantfood_per_interval cannot be negative")

        avoid_flag_waves = bool(wave_cfg.get("plantfood_avoid_flag_waves", False))
        pf_waves = set()
        for block_start in range(1, wave_count + 1, interval):
            block_end = min(wave_count, block_start + interval - 1)
            candidates = list(range(block_start, block_end + 1))
            if avoid_flag_waves:
                non_flag_candidates = [wave for wave in candidates if wave % flag_interval != 0]
                if non_flag_candidates:
                    candidates = non_flag_candidates
            sample_count = min(per_interval, len(candidates))
            if sample_count > 0:
                pf_waves.update(random.sample(candidates, sample_count))
        return pf_waves

    raise ValueError(
        "wave_settings.plantfood_mode must be one of "
        "'auto', 'count_range', 'fixed_count', 'interval', or 'interval_jittered'"
    )


def canonicalize_zombie_alias(zombie_alias, variant_alias_to_roll=None):
    if not isinstance(zombie_alias, str):
        return zombie_alias
    cleaned = zombie_alias.strip()
    if not cleaned or not variant_alias_to_roll:
        return cleaned
    return variant_alias_to_roll.get(cleaned, cleaned)


def build_zombie_variant_groups(raw_groups, all_zombie_aliases):
    if raw_groups is None:
        return {}, {}
    if not isinstance(raw_groups, dict):
        raise ValueError("zombie_variant_groups must be an object")

    zombie_variant_groups = {}
    variant_alias_to_roll = {}
    for raw_roll_alias, group_cfg in raw_groups.items():
        if not isinstance(raw_roll_alias, str) or not raw_roll_alias.strip():
            raise ValueError("zombie_variant_groups keys must be non-empty strings")

        roll_alias = raw_roll_alias.strip()
        entry_label = f'zombie_variant_groups["{roll_alias}"]'
        if roll_alias not in all_zombie_aliases:
            raise ValueError(f'{entry_label} roll alias "{roll_alias}" not found in ZombieTypes')

        variants_field = f"{entry_label}.variants"
        if isinstance(group_cfg, dict):
            variants = normalize_string_list(group_cfg.get("variants"), variants_field)
        else:
            variants = normalize_string_list(group_cfg, variants_field)

        group_aliases = []
        seen_in_group = set()
        for zombie_alias in [roll_alias] + variants:
            if zombie_alias not in all_zombie_aliases:
                raise ValueError(f'{variants_field} alias "{zombie_alias}" not found in ZombieTypes')
            if zombie_alias in seen_in_group:
                continue
            previous_owner = variant_alias_to_roll.get(zombie_alias)
            if previous_owner is not None and previous_owner != roll_alias:
                raise ValueError(
                    f'{variants_field} alias "{zombie_alias}" is already assigned to '
                    f'zombie_variant_groups["{previous_owner}"]'
                )
            seen_in_group.add(zombie_alias)
            variant_alias_to_roll[zombie_alias] = roll_alias
            group_aliases.append(zombie_alias)

        zombie_variant_groups[roll_alias] = group_aliases

    return zombie_variant_groups, variant_alias_to_roll


def expand_zombie_roll_pool(roll_pool, zombie_variant_groups):
    expanded_pool = []
    seen = set()
    for zombie_name in roll_pool:
        variants = zombie_variant_groups.get(zombie_name, [zombie_name])
        for variant_name in variants:
            if variant_name in seen:
                continue
            expanded_pool.append(variant_name)
            seen.add(variant_name)
    return expanded_pool


def pick_zombie_variant_alias(zombie_name, zombie_variant_groups=None):
    if zombie_variant_groups is None:
        return zombie_name
    variants = zombie_variant_groups.get(zombie_name)
    if not variants:
        return zombie_name
    return random.choice(variants)


def register_zombie_usage(zombies_used, zombie_name, zombie_variant_groups=None):
    if zombies_used is None:
        return
    zombies_used.add(zombie_name)
    if zombie_variant_groups and zombie_name in zombie_variant_groups:
        zombies_used.update(zombie_variant_groups[zombie_name])


def apply_zombie_pool_dependencies(selected_pool, dependency_cfg, variant_alias_to_roll=None):
    if dependency_cfg is None:
        return selected_pool[:]
    if not isinstance(dependency_cfg, list):
        raise ValueError("zombie_pool_dependencies must be an array")

    resolved_pool = selected_pool[:]
    pool_set = set(resolved_pool)

    changed = True
    while changed:
        changed = False
        for idx, rule in enumerate(dependency_cfg):
            if not isinstance(rule, dict):
                raise ValueError("zombie_pool_dependencies entries must be objects")

            entry_label = f"zombie_pool_dependencies[{idx}]"
            trigger_aliases = [
                canonicalize_zombie_alias(alias, variant_alias_to_roll)
                for alias in normalize_string_list(
                    rule.get("when_present", rule.get("zombie")),
                    f"{entry_label}.when_present",
                )
            ]
            trigger_aliases = list(dict.fromkeys(trigger_aliases))
            if not any(alias in pool_set for alias in trigger_aliases):
                continue

            requires_all = [
                canonicalize_zombie_alias(alias, variant_alias_to_roll)
                for alias in normalize_string_list(
                    rule.get("requires_all"),
                    f"{entry_label}.requires_all",
                )
            ]
            requires_all = list(dict.fromkeys(requires_all))
            for zombie_name in requires_all:
                if zombie_name not in pool_set:
                    resolved_pool.append(zombie_name)
                    pool_set.add(zombie_name)
                    changed = True

            requires_any = [
                canonicalize_zombie_alias(alias, variant_alias_to_roll)
                for alias in normalize_string_list(
                    rule.get("requires_any"),
                    f"{entry_label}.requires_any",
                )
            ]
            requires_any = list(dict.fromkeys(requires_any))
            if requires_any and not any(alias in pool_set for alias in requires_any):
                add_any_count = as_int(rule.get("add_any_count", 1), f"{entry_label}.add_any_count")
                if add_any_count < 1:
                    raise ValueError(f"{entry_label}.add_any_count must be >= 1")
                candidates = [alias for alias in requires_any if alias not in pool_set]
                random.shuffle(candidates)
                for zombie_name in candidates[:add_any_count]:
                    resolved_pool.append(zombie_name)
                    pool_set.add(zombie_name)
                    changed = True

    return resolved_pool


def prepare_wave_companion_rules(raw_rules, zombie_costs, variant_alias_to_roll=None):
    if raw_rules is None:
        return {}
    if not isinstance(raw_rules, list):
        raise ValueError("zombie_wave_rules must be an array")

    def parse_rule_count_range(rule, entry_label, exact_field, range_field, default_range):
        if exact_field in rule:
            value = as_int(rule.get(exact_field), f"{entry_label}.{exact_field}")
            if value < 0:
                raise ValueError(f"{entry_label}.{exact_field} cannot be negative")
            return (value, value)
        if range_field in rule:
            low, high = parse_int_range(rule.get(range_field), f"{entry_label}.{range_field}")
            if low < 0:
                raise ValueError(f"{entry_label}.{range_field} minimum cannot be negative")
            return (low, high)
        return default_range

    prepared = {}
    for idx, rule in enumerate(raw_rules):
        if not isinstance(rule, dict):
            raise ValueError("zombie_wave_rules entries must be objects")

        entry_label = f"zombie_wave_rules[{idx}]"
        zombie_name = canonicalize_zombie_alias(str(rule.get("zombie", "")).strip(), variant_alias_to_roll)
        if not zombie_name:
            raise ValueError(f"{entry_label}.zombie is required")

        requires_all = [
            canonicalize_zombie_alias(alias, variant_alias_to_roll)
            for alias in normalize_string_list(rule.get("requires_all"), f"{entry_label}.requires_all")
        ]
        requires_any = [
            canonicalize_zombie_alias(alias, variant_alias_to_roll)
            for alias in normalize_string_list(rule.get("requires_any"), f"{entry_label}.requires_any")
        ]
        requires_all = list(dict.fromkeys(requires_all))
        requires_any = list(dict.fromkeys(requires_any))
        default_any_count_range = (1, 1) if requires_any else (0, 0)
        requires_any_count_range = parse_rule_count_range(
            rule,
            entry_label,
            "requires_any_count",
            "requires_any_count_range",
            default_any_count_range,
        )
        followup_wave_count_range = parse_rule_count_range(
            rule,
            entry_label,
            "followup_wave_count",
            "followup_wave_count_range",
            (0, 0),
        )
        default_followup_any_count_range = (
            requires_any_count_range if followup_wave_count_range[1] > 0 else (0, 0)
        )
        followup_requires_any_count_range = parse_rule_count_range(
            rule,
            entry_label,
            "followup_requires_any_count",
            "followup_requires_any_count_range",
            default_followup_any_count_range,
        )
        requires_any_allow_duplicates = bool(rule.get("requires_any_allow_duplicates", True))

        if not requires_all and not requires_any:
            raise ValueError(f"{entry_label} must define requires_all and/or requires_any")
        if not requires_any:
            if requires_any_count_range[1] > 0:
                raise ValueError(
                    f"{entry_label}.requires_any_count_range requires {entry_label}.requires_any"
                )
            if followup_wave_count_range[1] > 0 or followup_requires_any_count_range[1] > 0:
                raise ValueError(
                    f"{entry_label}.followup_* fields require {entry_label}.requires_any"
                )
        if followup_requires_any_count_range[1] > 0 and followup_wave_count_range[1] <= 0:
            raise ValueError(
                f"{entry_label}.followup_requires_any_count_range requires "
                f"{entry_label}.followup_wave_count_range"
            )

        missing_costs = [
            alias for alias in [zombie_name] + requires_all + requires_any if alias not in zombie_costs
        ]
        if missing_costs:
            raise ValueError(
                f"{entry_label} references zombies missing from the final zombie pool: "
                + ", ".join(sorted(set(missing_costs)))
            )

        new_rule = {
            "requires_all": requires_all,
            "requires_any": requires_any,
            "requires_any_count_range": requires_any_count_range,
            "followup_wave_count_range": followup_wave_count_range,
            "followup_requires_any_count_range": followup_requires_any_count_range,
            "requires_any_allow_duplicates": requires_any_allow_duplicates,
        }
        existing = prepared.setdefault(zombie_name, copy.deepcopy(new_rule))
        for alias in requires_all:
            if alias not in existing["requires_all"]:
                existing["requires_all"].append(alias)
        for alias in requires_any:
            if alias not in existing["requires_any"]:
                existing["requires_any"].append(alias)
        for field_name in (
            "requires_any_count_range",
            "followup_wave_count_range",
            "followup_requires_any_count_range",
            "requires_any_allow_duplicates",
        ):
            if existing[field_name] != new_rule[field_name]:
                raise ValueError(
                    f"{entry_label} duplicates zombie_wave_rules for {zombie_name} "
                    f"with conflicting {field_name}"
                )

    return prepared


def is_flag_zombie_alias(zombie_name):
    if not isinstance(zombie_name, str) or not zombie_name.strip():
        return False
    parts = zombie_name.strip().split("_")
    if "flag" not in parts:
        return False

    flag_index = parts.index("flag")
    trailing = parts[flag_index + 1 :]
    for segment in trailing:
        if segment == "veteran":
            continue
        if re.fullmatch(r"armor\d+", segment):
            continue
        return False
    return True


def is_flag_zombie_reference(zombie_ref):
    if not isinstance(zombie_ref, str) or not zombie_ref.strip():
        return False
    cleaned = zombie_ref.strip()
    if cleaned.startswith("RTID("):
        try:
            cleaned = extract_rtid_name(cleaned, "zombie_ref")
        except ValueError:
            return False
    return is_flag_zombie_alias(cleaned)


def can_spawn_zombie_in_wave(
    zombie_name,
    remaining,
    wave_present,
    wave_counts,
    zombie_costs,
    companion_rules,
    zombie_jam_styles=None,
    allow_flag_zombies=True,
    active_jam=None,
):
    if not allow_flag_zombies and is_flag_zombie_alias(zombie_name):
        return False

    active_jam_names = get_active_jam_names(active_jam)

    # jam-related styles are used for preference only, not hard exclusion.
    # jam_all zombies are eligible in every jam.
    # eighties_8bit variants are still restricted to jam_8bit.
    if zombie_jam_styles is not None:
        jam_style = zombie_jam_styles.get(zombie_name)
        if jam_style == JAM_ALL_STYLE:
            pass

    # Restrict eighties_8bit variants to only spawn during jam_8bit
    if "eighties" in zombie_name and "8bit" in zombie_name:
        if "jam_8bit" not in active_jam_names:
            return False

    base_cost = zombie_costs.get(zombie_name)
    if base_cost is None or base_cost > (remaining + 1e-9):
        return False

    rule = companion_rules.get(zombie_name)
    if rule is None:
        return True

    required_cost = 0.0
    for companion in rule["requires_all"]:
        if companion == zombie_name or companion in wave_present:
            continue
        if not allow_flag_zombies and is_flag_zombie_alias(companion):
            return False
        companion_cost = zombie_costs.get(companion)
        if companion_cost is None:
            return False
        required_cost += companion_cost

    if rule["requires_any_count_range"][0] > 0:
        valid_any_candidates = [
            alias
            for alias in rule["requires_any"]
            if alias in zombie_costs and (allow_flag_zombies or not is_flag_zombie_alias(alias))
        ]
        if not valid_any_candidates:
            return False
        current_any_count = sum(wave_counts.get(alias, 0) for alias in valid_any_candidates)
        if zombie_name in valid_any_candidates:
            current_any_count += 1
        additional_needed = max(0, rule["requires_any_count_range"][0] - current_any_count)
        if additional_needed > 0:
            candidate_costs = sorted(zombie_costs[alias] for alias in valid_any_candidates)
            if rule["requires_any_allow_duplicates"]:
                required_cost += candidate_costs[0] * additional_needed
            else:
                if len(candidate_costs) < additional_needed:
                    return False
                required_cost += sum(candidate_costs[:additional_needed])

    return (base_cost + required_cost) <= (remaining + 1e-9)


def pick_greedy_zombie(candidates, zombie_costs, greediness):
    ordered = sorted(candidates, key=zombie_costs.__getitem__)
    if len(ordered) == 1:
        return ordered[0]

    if greediness >= 0.5:
        choice_count = max(1, int(len(ordered) * greediness))
        return random.choice(ordered[len(ordered) - choice_count :])

    choice_count = max(1, int(len(ordered) * (1 - greediness)))
    return random.choice(ordered[:choice_count])


def append_wave_zombie(
    zombies_list,
    wave_present,
    wave_counts,
    zombie_name,
    zombie_rtid,
    spawn_row_range,
    planks,
    zombies_used=None,
    zombie_variant_groups=None,
):
    wave_present.add(zombie_name)
    if wave_counts is not None:
        wave_counts[zombie_name] = wave_counts.get(zombie_name, 0) + 1
    register_zombie_usage(zombies_used, zombie_name, zombie_variant_groups)
    spawn_alias = pick_zombie_variant_alias(zombie_name, zombie_variant_groups)
    spawn_rtid = zombie_rtid.get(spawn_alias, f"RTID({spawn_alias}@ZombieTypes)")

    if not planks:
        zombies_list.append(
            {
                "Row": str(random.randint(*spawn_row_range)),
                "Type": spawn_rtid,
            }
        )
    else:
        zombies_list.append(
            {
                "Type": spawn_rtid,
            }
        )


def pick_wave_companion_target(existing_count, count_range, candidates, remaining, zombie_costs, allow_duplicates):
    min_count, max_count = count_range
    if max_count <= existing_count or not candidates:
        return existing_count

    feasible_totals = []
    for desired_total in range(existing_count + 1, max_count + 1):
        additions_needed = desired_total - existing_count
        candidate_costs = sorted(zombie_costs[alias] for alias in candidates if alias in zombie_costs)
        if not candidate_costs:
            break
        if allow_duplicates:
            required_cost = candidate_costs[0] * additions_needed
        else:
            if len(candidate_costs) < additions_needed:
                continue
            required_cost = sum(candidate_costs[:additions_needed])
        if required_cost <= (remaining + 1e-9):
            feasible_totals.append(desired_total)

    preferred_totals = [total for total in feasible_totals if total >= min_count]
    if preferred_totals:
        return random.choice(preferred_totals)
    if feasible_totals:
        return feasible_totals[-1]
    return existing_count


def add_requires_any_companions(
    candidates,
    count_range,
    remaining,
    zombies_list,
    wave_present,
    wave_counts,
    zombie_rtid,
    spawn_row_range,
    planks,
    zombie_costs,
    allow_flag_zombies=True,
    allow_duplicates=True,
    prefer_cheapest=False,
    zombies_used=None,
    zombie_variant_groups=None,
):
    if count_range[1] <= 0:
        return remaining, []

    valid_candidates = [
        alias
        for alias in candidates
        if alias in zombie_costs and (allow_flag_zombies or not is_flag_zombie_alias(alias))
    ]
    if not valid_candidates:
        return remaining, []

    existing_count = sum(wave_counts.get(alias, 0) for alias in valid_candidates)
    target_total = pick_wave_companion_target(
        existing_count,
        count_range,
        valid_candidates,
        remaining,
        zombie_costs,
        allow_duplicates,
    )
    if target_total <= existing_count:
        return remaining, []

    added = []
    available_choices = valid_candidates[:]
    while existing_count < target_total:
        affordable = [
            alias
            for alias in available_choices
            if zombie_costs.get(alias, remaining + 1.0) <= (remaining + 1e-9)
        ]
        if not affordable:
            break
        if prefer_cheapest:
            companion = min(affordable, key=zombie_costs.__getitem__)
        else:
            companion = random.choice(affordable)
        remaining -= zombie_costs[companion]
        append_wave_zombie(
            zombies_list,
            wave_present,
            wave_counts,
            companion,
            zombie_rtid,
            spawn_row_range,
            planks,
            zombies_used=zombies_used,
            zombie_variant_groups=zombie_variant_groups,
        )
        added.append(companion)
        existing_count += 1
        if not allow_duplicates:
            available_choices = [alias for alias in available_choices if alias != companion]

    return remaining, added


def schedule_followup_wave_companions(pending_by_wave, zombie_name, companion_rules, current_wave, wave_count):
    rule = companion_rules.get(zombie_name)
    if rule is None or rule["followup_wave_count_range"][1] <= 0:
        return
    if rule["followup_requires_any_count_range"][1] <= 0 or not rule["requires_any"]:
        return

    followup_count = random.randint(*rule["followup_wave_count_range"])
    for offset in range(1, followup_count + 1):
        target_wave = current_wave + offset
        if target_wave > wave_count:
            break
        pending_by_wave.setdefault(target_wave, []).append(
            {
                "requires_any": rule["requires_any"][:],
                "count_range": rule["followup_requires_any_count_range"],
                "allow_duplicates": rule["requires_any_allow_duplicates"],
            }
        )


def refresh_non_basic_pool(active_non_basics, non_basics_set, new_count, retained_count):
    retained = set()
    if active_non_basics and retained_count > 0:
        kept = random.sample(sorted(active_non_basics), min(retained_count, len(active_non_basics)))
        retained.update(kept)

    additions = set()
    fresh_candidates = list(non_basics_set - active_non_basics)
    if new_count > 0 and fresh_candidates:
        additions.update(random.sample(fresh_candidates, min(new_count, len(fresh_candidates))))

    remaining_slots = max(0, new_count - len(additions))
    if remaining_slots > 0:
        fallback_candidates = list((non_basics_set - retained) - additions)
        if fallback_candidates:
            additions.update(random.sample(fallback_candidates, min(remaining_slots, len(fallback_candidates))))

    return retained | additions


def add_required_wave_companions(
    zombie_name,
    remaining,
    zombies_list,
    wave_present,
    wave_counts,
    zombie_rtid,
    spawn_row_range,
    planks,
    zombie_costs,
    companion_rules,
    allow_flag_zombies=True,
    zombies_used=None,
    zombie_variant_groups=None,
):
    rule = companion_rules.get(zombie_name)
    if rule is None:
        return remaining

    for companion in rule["requires_all"]:
        if companion == zombie_name or companion in wave_present:
            continue
        remaining -= zombie_costs[companion]
        append_wave_zombie(
            zombies_list,
            wave_present,
            wave_counts,
            companion,
            zombie_rtid,
            spawn_row_range,
            planks,
            zombies_used=zombies_used,
            zombie_variant_groups=zombie_variant_groups,
        )

    remaining, _ = add_requires_any_companions(
        rule["requires_any"],
        rule["requires_any_count_range"],
        remaining,
        zombies_list,
        wave_present,
        wave_counts,
        zombie_rtid,
        spawn_row_range,
        planks,
        zombie_costs,
        allow_flag_zombies=allow_flag_zombies,
        allow_duplicates=rule["requires_any_allow_duplicates"],
        prefer_cheapest=(
            rule["requires_any_count_range"] == (1, 1)
            and rule["followup_wave_count_range"] == (0, 0)
        ),
        zombies_used=zombies_used,
        zombie_variant_groups=zombie_variant_groups,
    )

    return remaining


def get_enabled_ambushes(events_cfg, zombies_used, wave_zombies=None):
    available = []

    def add_weighted(kind, config, field_name):
        weight = get_config_weight(config, f"{field_name}.weight")
        if weight <= 0:
            return
        available.append({"kind": kind, "config": config, "weight": weight})

    market_cfg = events_cfg.get("market", {})
    if market_cfg.get("enabled", False):
        add_weighted("market", market_cfg, "events.market")
    raidpty_cfg = events_cfg.get("raidpty", {})
    if raidpty_cfg.get("enabled"):
        add_weighted("raidpty", raidpty_cfg, "events.raidpty")
    Parrotrousle_cfg = events_cfg.get("Parrotrousle", {})
    if Parrotrousle_cfg.get("enabled"):
        add_weighted("Parrotrousle", Parrotrousle_cfg, "events.Parrotrousle")
    sun_cfg = events_cfg.get("sun_crash", {})
    if sun_cfg.get("enabled", False):
        add_weighted("sun_crash", sun_cfg, "events.sun_crash")

    imp_cfgs = events_cfg.get("imp_ambushes", [])
    if not isinstance(imp_cfgs, list):
        raise ValueError("events.imp_ambushes must be an array")

    for idx, imp_cfg in enumerate(imp_cfgs):
        if not isinstance(imp_cfg, dict):
            raise ValueError("events.imp_ambushes entries must be objects")
        if not imp_cfg.get("enabled", True):
            continue

        required_zombie = imp_cfg.get("requires_wave_zombie", "")
        if required_zombie and required_zombie not in zombies_used:
            continue

        add_weighted("imp_ambush", imp_cfg, f"events.imp_ambushes[{idx}]")

    parachute_cfgs = events_cfg.get("parachute_rains", [])
    if not isinstance(parachute_cfgs, list):
        raise ValueError("events.parachute_rains must be an array")

    for idx, parachute_cfg in enumerate(parachute_cfgs):
        if not isinstance(parachute_cfg, dict):
            raise ValueError("events.parachute_rains entries must be objects")
        if not parachute_cfg.get("enabled", True):
            continue

        required_zombie = parachute_cfg.get("requires_wave_zombie", "")
        if required_zombie and required_zombie not in zombies_used:
            continue

        add_weighted("parachute_rain", parachute_cfg, f"events.parachute_rains[{idx}]")

    for array_name, idx, storm_cfg in iter_storm_event_configs(events_cfg, strict=True):
        if not storm_cfg.get("enabled", True):
            continue

        required_zombie = storm_cfg.get("requires_wave_zombie", "")
        if required_zombie and required_zombie not in zombies_used:
            continue

        add_weighted("storm_ambush", storm_cfg, f"events.{array_name}[{idx}]")

    portal_cfgs = events_cfg.get("portal_spawns", [])
    if not isinstance(portal_cfgs, list):
        raise ValueError("events.portal_spawns must be an array")

    for idx, portal_cfg in enumerate(portal_cfgs):
        if not isinstance(portal_cfg, dict):
            raise ValueError("events.portal_spawns entries must be objects")
        if not portal_cfg.get("enabled", True):
            continue

        add_weighted("portal_spawn", portal_cfg, f"events.portal_spawns[{idx}]")

    grid_spawn_cfgs = events_cfg.get("grid_spawns", [])
    if not isinstance(grid_spawn_cfgs, list):
        raise ValueError("events.grid_spawns must be an array")

    for idx, grid_cfg in enumerate(grid_spawn_cfgs):
        if not isinstance(grid_cfg, dict):
            raise ValueError("events.grid_spawns entries must be objects")
        if not grid_cfg.get("enabled", True):
            continue
        required_zombie = grid_cfg.get("requires_wave_zombie", "")
        if required_zombie and required_zombie not in zombies_used:
            continue
        add_weighted("grid_spawn", grid_cfg, f"events.grid_spawns[{idx}]")

    frost_cfgs = events_cfg.get("frost_winds", [])
    if not isinstance(frost_cfgs, list):
        raise ValueError("events.frost_winds must be an array")

    for idx, frost_cfg in enumerate(frost_cfgs):
        if not isinstance(frost_cfg, dict):
            raise ValueError("events.frost_winds entries must be objects")
        if not frost_cfg.get("enabled", True):
            continue
        add_weighted("frost_wind", frost_cfg, f"events.frost_winds[{idx}]")

    low_tide_cfgs = events_cfg.get("low_tides", [])
    if not isinstance(low_tide_cfgs, list):
        raise ValueError("events.low_tides must be an array")

    for idx, tide_cfg in enumerate(low_tide_cfgs):
        if not isinstance(tide_cfg, dict):
            raise ValueError("events.low_tides entries must be objects")
        if not tide_cfg.get("enabled", True):
            continue
        add_weighted("low_tide", tide_cfg, f"events.low_tides[{idx}]")

    necro_cfgs = events_cfg.get("necromancy_spawns", [])
    if not isinstance(necro_cfgs, list):
        raise ValueError("events.necromancy_spawns must be an array")

    for idx, necro_cfg in enumerate(necro_cfgs):
        if not isinstance(necro_cfg, dict):
            raise ValueError("events.necromancy_spawns entries must be objects")
        if not necro_cfg.get("enabled", True):
            continue
        add_weighted("necromancy_spawn", necro_cfg, f"events.necromancy_spawns[{idx}]")

    dino_cfgs = events_cfg.get("dino_ambushes", [])
    if not isinstance(dino_cfgs, list):
        raise ValueError("events.dino_ambushes must be an array")

    for idx, dino_cfg in enumerate(dino_cfgs):
        if not isinstance(dino_cfg, dict):
            raise ValueError("events.dino_ambushes entries must be objects")
        if not dino_cfg.get("enabled", True):
            continue
        if wave_zombies is not None and not dino_event_has_spawnable_actions(dino_cfg, wave_zombies):
            continue
        add_weighted("dino_ambush", dino_cfg, f"events.dino_ambushes[{idx}]")

    tide_cfgs = events_cfg.get("tide_changes", [])
    if not isinstance(tide_cfgs, list):
        raise ValueError("events.tide_changes must be an array")

    for idx, tide_cfg in enumerate(tide_cfgs):
        if not isinstance(tide_cfg, dict):
            raise ValueError("events.tide_changes entries must be objects")
        if not tide_cfg.get("enabled", True):
            continue
        add_weighted("tide_change", tide_cfg, f"events.tide_changes[{idx}]")

    return available


def build_generated_portal_mode_groups(group_mode, portal_pool, zombie_type_metadata, zombie_costs):
    if group_mode == "random":
        return [{"key": "random", "zombies": portal_pool[:], "weight": len(portal_pool)}]

    grouped = {}
    for zombie_alias in portal_pool:
        if group_mode == "same_world":
            group_key = zombie_type_metadata.get(zombie_alias, {}).get("portal_world", "modern")
        elif group_mode == "same_cost":
            if zombie_alias not in zombie_costs:
                continue
            group_key = round(zombie_costs[zombie_alias], 6)
        elif group_mode == "same_suffix":
            group_key = zombie_type_metadata.get(zombie_alias, {}).get(
                "suffix",
                extract_portal_group_suffix(zombie_alias),
            )
        else:
            raise ValueError(f"Unsupported generated portal mode: {group_mode}")
        grouped.setdefault(group_key, []).append(zombie_alias)

    return [
        {"key": group_key, "zombies": zombies[:], "weight": len(zombies)}
        for group_key, zombies in grouped.items()
        if zombies
    ]


def pick_generated_portal_zombies(
    group_mode,
    portal_pool,
    zombie_count_range,
    zombie_type_metadata,
    zombie_costs,
):
    min_count, max_count = zombie_count_range
    groups = build_generated_portal_mode_groups(
        group_mode,
        portal_pool,
        zombie_type_metadata,
        zombie_costs,
    )
    eligible_groups = [
        group
        for group in groups
        if len(group["zombies"]) >= min_count
    ]
    if not eligible_groups:
        return None, None

    chosen_group = pick_weighted_dict(eligible_groups, "events.generated_portals.group_modes")
    group_zombies = chosen_group["zombies"]
    target_count = random.randint(min_count, min(max_count, len(group_zombies)))
    return random.sample(group_zombies, target_count), chosen_group


def choose_generated_portal_world(zombies, zombie_type_metadata, default_world):
    worlds = []
    for zombie_alias in zombies:
        portal_world = zombie_type_metadata.get(zombie_alias, {}).get("portal_world", default_world)
        portal_world = normalize_portal_world_name(portal_world, fallback_world=default_world)
        if portal_world not in worlds:
            worlds.append(portal_world)
    if not worlds:
        return default_world
    if len(worlds) == 1:
        return worlds[0]
    # Mixed worlds — fall back to the configured default (modern or travellog)
    return default_world


def normalize_time_between_spawns(raw_value, field_name):
    if raw_value is None:
        return {"Min": 10.0, "Max": 12.0}
    if isinstance(raw_value, dict):
        min_value = as_number(raw_value.get("Min"), f"{field_name}.Min")
        max_value = as_number(raw_value.get("Max"), f"{field_name}.Max")
    elif isinstance(raw_value, list) and len(raw_value) == 2:
        min_value, max_value = parse_float_range(raw_value, field_name)
    else:
        raise ValueError(f"{field_name} must be an object with Min/Max or a [min, max] array")
    if min_value > max_value:
        raise ValueError(f"{field_name}.Min cannot be greater than {field_name}.Max")
    return {"Min": min_value, "Max": max_value}


def build_generated_portal_objects(
    portal_cfg,
    default_zombie_pool,
    all_zombie_aliases,
    zombie_costs,
    zombie_type_metadata,
    existing_aliases,
    variant_alias_to_roll=None,
):
    if portal_cfg is None:
        return [], [], {}
    if not isinstance(portal_cfg, dict):
        raise ValueError("events.generated_portals must be an object")
    if not portal_cfg.get("enabled", False):
        return [], [], {}

    field_prefix = "events.generated_portals"
    portal_count_range = parse_int_range(
        portal_cfg.get("portal_count_range", [1, 1]),
        f"{field_prefix}.portal_count_range",
    )
    zombie_count_range = parse_int_range(
        portal_cfg.get("zombies_per_portal_range", [2, 4]),
        f"{field_prefix}.zombies_per_portal_range",
    )
    if portal_count_range[0] <= 0:
        raise ValueError(f"{field_prefix}.portal_count_range minimum must be > 0")
    if zombie_count_range[0] <= 0:
        raise ValueError(f"{field_prefix}.zombies_per_portal_range minimum must be > 0")

    raw_pool = portal_cfg.get("zombie_pool", default_zombie_pool)
    portal_pool = unique_zombie_pool(
        raw_pool,
        f"{field_prefix}.zombie_pool",
        variant_alias_to_roll=variant_alias_to_roll,
    )
    validated_pool = []
    for idx, zombie_alias in enumerate(portal_pool):
        if zombie_alias not in all_zombie_aliases:
            raise ValueError(
                f'{field_prefix}.zombie_pool[{idx}] "{zombie_alias}" was not found in ZombieTypes aliases'
            )
        if zombie_alias not in zombie_costs:
            raise ValueError(
                f'{field_prefix}.zombie_pool[{idx}] "{zombie_alias}" is missing a resolved wave cost'
            )
        validated_pool.append(zombie_alias)
    portal_pool = validated_pool

    if bool(portal_cfg.get("exclude_flag_zombies", False)):
        portal_pool = [alias for alias in portal_pool if not is_flag_zombie_alias(alias)]
    if len(portal_pool) < zombie_count_range[0]:
        raise ValueError(
            f"{field_prefix}.zombie_pool must contain at least "
            f"{zombie_count_range[0]} valid zombie aliases"
        )

    group_modes = normalize_generated_portal_group_modes(
        portal_cfg.get("group_modes"),
        f"{field_prefix}.group_modes",
    )
    default_world = parse_portal_world_name(
        str(portal_cfg.get("default_world", "modern")),
        f"{field_prefix}.default_world",
    )
    resource_groups = normalize_string_list(
        portal_cfg.get("resource_groups", ["ModernPortalGroup"]),
        f"{field_prefix}.resource_groups",
    )
    type_alias_prefix = str(portal_cfg.get("type_alias_prefix", "zombieportal_generated")).strip() or "zombieportal_generated"
    props_alias_prefix = str(portal_cfg.get("props_alias_prefix", "zombieportal_props_generated")).strip() or "zombieportal_props_generated"
    type_name_prefix = str(portal_cfg.get("type_name_prefix", type_alias_prefix)).strip() or type_alias_prefix
    time_between_spawns = normalize_time_between_spawns(
        portal_cfg.get("time_between_spawns", {"Min": 10, "Max": 12}),
        f"{field_prefix}.time_between_spawns",
    )

    portal_count = random.randint(*portal_count_range)
    portal_objects = []
    generated_pool = []
    portal_costs = {}

    for portal_index in range(1, portal_count + 1):
        eligible_modes = []
        for group_mode in group_modes:
            portal_zombies, chosen_group = pick_generated_portal_zombies(
                group_mode,
                portal_pool,
                zombie_count_range,
                zombie_type_metadata,
                zombie_costs,
            )
            if portal_zombies:
                eligible_modes.append(
                    {
                        "mode": group_mode,
                        "zombies": portal_zombies,
                        "group": chosen_group,
                        "weight": 1.0,
                    }
                )

        if not eligible_modes:
            raise ValueError(
                f"{field_prefix} could not build a portal with the current zombie_pool and group_modes"
            )

        chosen_mode = pick_weighted_dict(eligible_modes, f"{field_prefix}.group_modes")
        portal_zombies = chosen_mode["zombies"]
        portal_world = choose_generated_portal_world(
            portal_zombies,
            zombie_type_metadata,
            default_world,
        )

        type_alias = make_unique_alias(f"{type_alias_prefix}_{portal_index}", existing_aliases)
        props_alias = make_unique_alias(f"{props_alias_prefix}_{portal_index}", existing_aliases)
        type_name = f"{type_name_prefix}_{portal_index}"

        portal_objects.append(
            {
                "aliases": [type_alias],
                "objclass": "GridItemType",
                "objdata": {
                    "TypeName": type_name,
                    "GridItemClass": str(portal_cfg.get("grid_item_class", "GridItemZombiePortal")),
                    "Properties": f"RTID({props_alias}@CurrentLevel)",
                    "ResourceGroups": resource_groups[:],
                },
            }
        )
        # Calculate portal cost as sum of all zombie costs inside
        portal_cost = sum(zombie_costs.get(zombie_alias, 0) for zombie_alias in portal_zombies) * 100

        portal_objects.append(
            {
                "aliases": [props_alias],
                "objclass": "GridItemZombiePortalProps",
                "objdata": {
                    "CanBeMowed": bool(portal_cfg.get("can_be_mowed", False)),
                    "CloseAnimation": str(portal_cfg.get("close_animation", "end")),
                    "Height": str(portal_cfg.get("height", "ground")),
                    "Hitpoints": as_int(portal_cfg.get("hitpoints", 600), f"{field_prefix}.hitpoints"),
                    "PopAnim": str(portal_cfg.get("pop_anim", "POPANIM_EFFECTS_MODERN_PORTAL")),
                    "PopAnimRenderOffset": copy.deepcopy(
                        portal_cfg.get("pop_anim_render_offset", {"x": 96, "y": 125})
                    ),
                    "PopAnimRigClass": str(
                        portal_cfg.get("pop_anim_rig_class", "GridItemZombiePortal_AnimRig")
                    ),
                    "SpawnAnimation": str(portal_cfg.get("spawn_animation", "spawn")),
                    "World": portal_world,
                    "WavePointsCost": portal_cost,
                    "ZombieSpawnMethod": str(
                        portal_cfg.get("zombie_spawn_method", "NonRandomShuffled")
                    ),
                    "ZombieSpawnPointOffset": as_int(
                        portal_cfg.get("zombie_spawn_point_offset", 15),
                        f"{field_prefix}.zombie_spawn_point_offset",
                    ),
                    "TimeBetweenSpawns": time_between_spawns,
                    "ZombieTypesToSpawn": [
                        {"Weight": 1, "ZombieTypeName": zombie_alias}
                        for zombie_alias in portal_zombies
                    ],
                },
            }
        )
        generated_pool.append({"Count": 1, "Type": f"RTID({type_alias}@.)"})
        portal_costs[type_alias] = portal_cost

    return portal_objects, generated_pool, portal_costs


def build_portal_spawn_event(wave, ambush_count, portal_cfg, portal_costs, max_cost):
    alias_prefix = str(portal_cfg.get("alias_prefix", "PortalSpawn"))
    event_name = str(portal_cfg.get("event_name", "portal_spawn")).strip() or "portal_spawn"
    alias = f"{alias_prefix}{wave}_{ambush_count}_{event_name}"

    portal_pool = portal_cfg.get("portal_pool", [])
    if not isinstance(portal_pool, list) or len(portal_pool) == 0:
        raise ValueError("events.portal_spawns[].portal_pool must be a non-empty array")

    prepared_pool = []
    for idx, raw_portal in enumerate(portal_pool):
        entry_label = f"events.portal_spawns[].portal_pool[{idx}]"
        if isinstance(raw_portal, str):
            portal_type = raw_portal.strip()
            if not portal_type:
                raise ValueError(f"{entry_label} must be a non-empty string")
            # Extract alias from RTID(alias@.)
            if portal_type.startswith("RTID(") and "@" in portal_type:
                alias = portal_type.split("RTID(")[1].split("@")[0]
            else:
                alias = portal_type
            cost = portal_costs.get(alias, 0)
            prepared_pool.append({"type_name": portal_type, "weight": 1.0, "cost": cost})
            continue
        if not isinstance(raw_portal, dict):
            raise ValueError(f"{entry_label} must be a string or object")

        portal_type = str(raw_portal.get("type_name", "")).strip()
        if not portal_type:
            raise ValueError(f"{entry_label}.type_name is required")
        # Extract alias
        if portal_type.startswith("RTID(") and "@" in portal_type:
            alias = portal_type.split("RTID(")[1].split("@")[0]
        else:
            alias = portal_type
        cost = portal_costs.get(alias, 0)
        prepared_pool.append(
            {
                "type_name": portal_type,
                "weight": get_config_weight(raw_portal, f"{entry_label}.weight"),
                "cost": cost,
            }
        )

    # Filter portals that exceed max_cost and sort by cost ascending (prefer cheaper)
    prepared_pool = [p for p in prepared_pool if p["cost"] <= max_cost]
    prepared_pool.sort(key=lambda p: p["cost"])

    count_range = parse_int_range(
        portal_cfg.get("portal_count_range", [1, 2]),
        "events.portal_spawns[].portal_count_range",
    )
    allow_duplicate_portals = bool(portal_cfg.get("allow_duplicate_portals", False))
    portal_count = random.randint(*count_range)

    if not allow_duplicate_portals:
        positive_pool = [entry for entry in prepared_pool if entry["weight"] > 0]
        portal_count = min(portal_count, len(positive_pool))
    if portal_count <= 0:
        return None, None, 0

    chosen_portals = []
    chosen_costs = []
    available_pool = prepared_pool[:]
    for _ in range(portal_count):
        positive_pool = [entry for entry in available_pool if entry["weight"] > 0]
        if not positive_pool:
            break
        chosen = pick_weighted_dict(positive_pool, "events.portal_spawns[].portal_pool")
        chosen_portals.append(chosen["type_name"])
        chosen_costs.append(chosen["cost"])
        if not allow_duplicate_portals:
            available_pool = [entry for entry in available_pool if entry is not chosen]

    if len(chosen_portals) == 0:
        return None, None, 0

    spawn_x_range = parse_int_range(
        portal_cfg.get("spawn_x_range", [5, 8]),
        "events.portal_spawns[].spawn_x_range",
    )
    spawn_y_range = parse_int_range(
        portal_cfg.get("spawn_y_range", [0, 4]),
        "events.portal_spawns[].spawn_y_range",
    )
    all_positions = [
        {"mX": x, "mY": y}
        for x in range(spawn_x_range[0], spawn_x_range[1] + 1)
        for y in range(spawn_y_range[0], spawn_y_range[1] + 1)
    ]
    unique_positions = bool(portal_cfg.get("unique_positions", True))
    if unique_positions and len(chosen_portals) > len(all_positions):
        raise ValueError(
            "events.portal_spawns[] requested more unique portal positions than the configured spawn area allows"
        )

    if unique_positions:
        spawn_positions = random.sample(all_positions, len(chosen_portals))
    else:
        spawn_positions = [random.choice(all_positions) for _ in chosen_portals]

    pool = [
        {"Count": 1, "Type": f"RTID({portal_type}@.)"}
        for portal_type in chosen_portals
    ]
    event_object = {
        "aliases": [alias],
        "objclass": "SpawnGravestonesWaveActionProps",
        "objdata": {
            "GravestonePool": pool,
            "SpawnPositionsPool": spawn_positions,
            "SpawnEffectAnimID": str(portal_cfg.get("spawn_effect", "")),
            "SpawnSoundID": str(portal_cfg.get("spawn_sound_id", "")),
            "DisplacePlants": bool(portal_cfg.get("displace_plants", True)),
            "RandomPlacement": bool(portal_cfg.get("random_placement", False)),
            "ShakeScreen": bool(portal_cfg.get("shake_screen", False)),
            "GridClassesToDestroy": copy.deepcopy(
                portal_cfg.get("grid_classes_to_destroy", [])
            ),
        },
    }

    # Calculate points cost: sum of costs of chosen portals
    points_cost = sum(chosen_costs)

    return event_object, f"RTID({alias}@GridItemTypes)", points_cost


def normalize_grid_item_type(value, field_name,custom=False):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    cleaned = value.strip()
    if cleaned.startswith("RTID("):
        return cleaned
    if not custom:
        return f"RTID({cleaned}@GridItemTypes)"
    else:
        return f"RTID({cleaned}@.)"


def normalize_zombie_type(value, field_name, all_zombie_aliases=None):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    cleaned = value.strip()
    if cleaned.startswith("RTID("):
        return cleaned
    if all_zombie_aliases is not None and cleaned not in all_zombie_aliases:
        raise ValueError(f'{field_name}: "{cleaned}" was not found in ZombieTypes aliases')
    return f"RTID({cleaned}@ZombieTypes)"


def optional_zombie_alias(value):
    if not isinstance(value, str) or not value.strip():
        return None
    cleaned = value.strip()
    if cleaned.startswith("RTID("):
        try:
            return extract_rtid_name(cleaned, "zombie_ref")
        except ValueError:
            return None
    return cleaned


def parse_zombie_alias(value, field_name, all_zombie_aliases=None, variant_alias_to_roll=None):
    alias = optional_zombie_alias(value)
    if not alias:
        raise ValueError(f"{field_name} must be a non-empty zombie alias or RTID")
    alias = canonicalize_zombie_alias(alias, variant_alias_to_roll)
    if all_zombie_aliases is not None and alias not in all_zombie_aliases:
        raise ValueError(f'{field_name}: "{alias}" was not found in ZombieTypes aliases')
    return alias


def collect_zombie_aliases_from_entries(raw_entries, value_keys=None):
    aliases = set()
    if not isinstance(raw_entries, list):
        return aliases

    if value_keys is None:
        value_keys = ("Type", "type", "zombie_name", "type_name")

    for raw_entry in raw_entries:
        if isinstance(raw_entry, str):
            alias = optional_zombie_alias(raw_entry)
            if alias:
                aliases.add(alias)
            continue
        if not isinstance(raw_entry, dict):
            continue
        for key in value_keys:
            alias = optional_zombie_alias(raw_entry.get(key))
            if alias:
                aliases.add(alias)
                break

    return aliases


def prepare_weighted_zombie_pool(
    raw_pool,
    field_name,
    all_zombie_aliases=None,
    variant_alias_to_roll=None,
    value_keys=None,
):
    if not isinstance(raw_pool, list) or len(raw_pool) == 0:
        raise ValueError(f"{field_name} must be a non-empty array")

    if value_keys is None:
        value_keys = ("zombie_name", "type_name", "type", "Type")

    prepared = []
    for idx, raw_entry in enumerate(raw_pool):
        entry_label = f"{field_name}[{idx}]"
        if isinstance(raw_entry, str):
            alias = parse_zombie_alias(
                raw_entry,
                entry_label,
                all_zombie_aliases,
                variant_alias_to_roll=variant_alias_to_roll,
            )
            prepared.append({"alias": alias, "weight": 1.0})
            continue
        if not isinstance(raw_entry, dict):
            raise ValueError(f"{entry_label} must be a string or object")

        raw_alias = None
        for key in value_keys:
            if key in raw_entry:
                raw_alias = raw_entry.get(key)
                break
        alias = parse_zombie_alias(
            raw_alias,
            f"{entry_label}.zombie_name",
            all_zombie_aliases,
            variant_alias_to_roll=variant_alias_to_roll,
        )
        weight = as_number(raw_entry.get("weight", 1), f"{entry_label}.weight")
        if weight < 0:
            raise ValueError(f"{entry_label}.weight cannot be negative")
        prepared.append({"alias": alias, "weight": weight})

    return prepared


def pick_weighted_entry(entries, field_name):
    if not isinstance(entries, list) or len(entries) == 0:
        raise ValueError(f"{field_name} must contain at least one entry")

    total_weight = sum(entry["weight"] for entry in entries)
    if total_weight <= 0:
        return random.choice(entries)

    roll = random.uniform(0.0, total_weight)
    running = 0.0
    for entry in entries:
        running += entry["weight"]
        if roll <= running:
            return entry
    return entries[-1]


def normalize_grid_positions(raw_positions, field_name):
    if not isinstance(raw_positions, list) or len(raw_positions) == 0:
        raise ValueError(f"{field_name} must be a non-empty array")

    positions = []
    for idx, raw in enumerate(raw_positions):
        if not isinstance(raw, dict):
            raise ValueError(f"{field_name}[{idx}] must be an object")
        if "mX" in raw or "mY" in raw:
            x = as_int(raw.get("mX"), f"{field_name}[{idx}].mX")
            y = as_int(raw.get("mY"), f"{field_name}[{idx}].mY")
        else:
            x, y = normalize_grid_position(raw, f"{field_name}[{idx}]")
        positions.append({"mX": x, "mY": y})
    return positions


def normalize_grid_item_pool(raw_pool, field_name):
    if not isinstance(raw_pool, list) or len(raw_pool) == 0:
        raise ValueError(f"{field_name} must be a non-empty array")

    pool = []
    for idx, raw_entry in enumerate(raw_pool):
        entry_label = f"{field_name}[{idx}]"
        if isinstance(raw_entry, str):
            pool.append({"Count": 1, "Type": normalize_grid_item_type(raw_entry, entry_label)})
            continue
        if not isinstance(raw_entry, dict):
            raise ValueError(f"{entry_label} must be a string or object")

        if "weight" in raw_entry:
            count = as_number(raw_entry.get("weight"), f"{entry_label}.weight")
            if count <= 0:
                raise ValueError(f"{entry_label}.weight must be > 0")
        else:
            count = as_int(
                raw_entry.get("Count", raw_entry.get("count", 1)),
                f"{entry_label}.count",
            )
            if count <= 0:
                raise ValueError(f"{entry_label}.count must be > 0")

        raw_type = raw_entry.get("Type", raw_entry.get("type_name", raw_entry.get("type")))
        pool.append({"Count": count, "Type": normalize_grid_item_type(raw_type, f"{entry_label}.type")})
    return pool


def normalize_grid_type_list(raw_grid_types, field_name):
    if not isinstance(raw_grid_types, list) or len(raw_grid_types) == 0:
        raise ValueError(f"{field_name} must be a non-empty array")
    return [normalize_grid_item_type(value, f"{field_name}[{idx}]") for idx, value in enumerate(raw_grid_types)]


def normalize_spawn_zombies_list(raw_zombies, field_name, all_zombie_aliases):
    if not isinstance(raw_zombies, list) or len(raw_zombies) == 0:
        raise ValueError(f"{field_name} must be a non-empty array")

    zombies = []
    for idx, raw_entry in enumerate(raw_zombies):
        entry_label = f"{field_name}[{idx}]"
        if isinstance(raw_entry, str):
            zombies.append({"Type": normalize_zombie_type(raw_entry, entry_label, all_zombie_aliases)})
            continue
        if not isinstance(raw_entry, dict):
            raise ValueError(f"{entry_label} must be a string or object")

        count = as_int(raw_entry.get("Count", raw_entry.get("count", 1)), f"{entry_label}.count")
        if count <= 0:
            raise ValueError(f"{entry_label}.count must be > 0")
        raw_type = raw_entry.get("Type", raw_entry.get("zombie_name", raw_entry.get("type_name")))
        zombie_entry = {"Type": normalize_zombie_type(raw_type, f"{entry_label}.type", all_zombie_aliases)}
        for key, value in raw_entry.items():
            if key in {"Type", "zombie_name", "type_name", "Count", "count"}:
                continue
            zombie_entry[key] = copy.deepcopy(value)
        for _ in range(count):
            zombies.append(copy.deepcopy(zombie_entry))
    return zombies


def normalize_module_rtid(value, field_name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    cleaned = value.strip()
    if cleaned.startswith("RTID("):
        return cleaned
    return f"RTID({cleaned}@LevelModules)"


def normalize_module_list(raw_modules, field_name):
    if raw_modules is None:
        return []
    if not isinstance(raw_modules, list):
        raise ValueError(f"{field_name} must be an array")
    return [
        normalize_module_rtid(value, f"{field_name}[{idx}]")
        for idx, value in enumerate(raw_modules)
    ]


def default_wave_start_message(zombie_name, fallback):
    if zombie_name in DEFAULT_AMBUSH_WAVE_MESSAGES:
        return DEFAULT_AMBUSH_WAVE_MESSAGES[zombie_name]
    return fallback


def iter_storm_event_configs(events_cfg, strict=False):
    if not isinstance(events_cfg, dict):
        return

    storm_arrays = [
        ("storm_ambushes", None),
        ("sandstorm_ambushes", "sandstorm"),
        ("snowstorm_ambushes", "snowstorm"),
    ]
    for array_name, default_storm_type in storm_arrays:
        cfgs = events_cfg.get(array_name, [])
        if not isinstance(cfgs, list):
            if strict:
                raise ValueError(f"events.{array_name} must be an array")
            continue
        for idx, cfg in enumerate(cfgs):
            if not isinstance(cfg, dict):
                if strict:
                    raise ValueError(f"events.{array_name} entries must be objects")
                continue
            normalized_cfg = cfg
            storm_type = str(cfg.get("storm_type", "")).strip()
            if not storm_type:
                if default_storm_type is None:
                    if strict:
                        raise ValueError(f"events.{array_name}[{idx}].storm_type is required")
                else:
                    normalized_cfg = dict(cfg)
                    normalized_cfg["storm_type"] = default_storm_type
            yield array_name, idx, normalized_cfg


def get_event_required_modules(events_cfg):
    modules = []

    def add_modules(raw_modules, field_name):
        for module in normalize_module_list(raw_modules, field_name):
            if module not in modules:
                modules.append(module)

    add_modules(events_cfg.get("required_modules"), "events.required_modules")

    for idx, parachute_cfg in enumerate(events_cfg.get("parachute_rains", [])):
        if not isinstance(parachute_cfg, dict) or not parachute_cfg.get("enabled", True):
            continue
        add_modules(
            parachute_cfg.get("required_modules"),
            f"events.parachute_rains[{idx}].required_modules",
        )
        direct_spider_name = str(parachute_cfg.get("spider_zombie_name", parachute_cfg.get("SpiderZombieName", ""))).strip()
        spider_pool_aliases = collect_zombie_aliases_from_entries(
            parachute_cfg.get(
                "spider_zombie_pool",
                parachute_cfg.get("SpiderZombiePool", parachute_cfg.get("zombie_pool")),
            ),
            value_keys=("SpiderZombieName", "spider_zombie_name", "zombie_name", "type_name", "type", "Type"),
        )
        if direct_spider_name == "west_bull" or "west_bull" in spider_pool_aliases:
            add_modules(
                DEFAULT_STAMPEDE_MODULES,
                f"events.parachute_rains[{idx}].auto_required_modules",
            )

    event_arrays = [
        "imp_ambushes",
        "storm_ambushes",
        "sandstorm_ambushes",
        "snowstorm_ambushes",
        "portal_spawns",
        "grid_spawns",
        "frost_winds",
        "low_tides",
        "necromancy_spawns",
        "dino_ambushes",
        "tide_changes",
    ]
    for array_name in event_arrays:
        cfgs = events_cfg.get(array_name, [])
        if not isinstance(cfgs, list):
            continue
        for idx, cfg in enumerate(cfgs):
            if not isinstance(cfg, dict) or not cfg.get("enabled", True):
                continue
            add_modules(
                cfg.get("required_modules"),
                f"events.{array_name}[{idx}].required_modules",
            )

    for single_name in ["market", "raidpty", "Parrotrousle", "sun_crash"]:
        cfg = events_cfg.get(single_name, {})
        if not isinstance(cfg, dict) or not cfg.get("enabled"):
            continue
        add_modules(
            cfg.get("required_modules"),
            f"events.{single_name}.required_modules",
        )

    return modules


def build_initial_tide_object(tide_cfg):
    if tide_cfg is None:
        return None
    if not isinstance(tide_cfg, dict):
        raise ValueError("initial_tide must be an object")
    if not tide_cfg.get("enabled", False):
        return None

    alias = str(tide_cfg.get("alias", "InitialTide")).strip() or "InitialTide"
    module_rtid = str(tide_cfg.get("module_rtid", f"RTID({alias}@CurrentLevel)")).strip()
    starting_wave_location = as_int(
        tide_cfg.get(
            "starting_wave_location",
            tide_cfg.get("starting_dry_lane_count", 4),
        ),
        "initial_tide.starting_wave_location",
    )
    if starting_wave_location < 1 or starting_wave_location > 8:
        raise ValueError("initial_tide.starting_wave_location must be between 1 and 8")

    tide_object = {
        "aliases": [alias],
        "objclass": "TideProperties",
        "objdata": {
            "StartingWaveLocation": starting_wave_location,
            "ShowTideMarker": bool(tide_cfg.get("show_tide_marker", True)),
        },
    }
    return {"module_rtid": module_rtid, "object": tide_object}


def resolve_tide_change_amount(tide_cfg, field_prefix):
    if "change_amount" in tide_cfg:
        change_amount = as_int(tide_cfg.get("change_amount"), f"{field_prefix}.change_amount")
    elif "change_amount_range" in tide_cfg:
        low, high = parse_int_range(
            tide_cfg.get("change_amount_range"),
            f"{field_prefix}.change_amount_range",
        )
        change_amount = random.randint(low, high)
    elif "dry_lane_count" in tide_cfg:
        dry_lane_count = as_int(tide_cfg.get("dry_lane_count"), f"{field_prefix}.dry_lane_count")
        change_amount = 9 - dry_lane_count
    else:
        low, high = parse_int_range(
            tide_cfg.get("dry_lane_count_range", [3, 5]),
            f"{field_prefix}.dry_lane_count_range",
        )
        dry_lane_count = random.randint(low, high)
        change_amount = 9 - dry_lane_count

    if change_amount < 0 or change_amount > 8:
        raise ValueError(f"{field_prefix} resolved to an invalid ChangeAmount {change_amount}")
    return change_amount


def build_tide_change_event(wave, ambush_count, tide_cfg, existing_aliases):
    alias_prefix = str(tide_cfg.get("alias_prefix", "tide")).strip() or "tide"
    event_name = str(tide_cfg.get("event_name", "tide")).strip() or "tide"
    alias = make_unique_alias(f"{alias_prefix}{wave}_{ambush_count}_{event_name}", existing_aliases)

    event_object = {
        "aliases": [alias],
        "objclass": "TidalChangeWaveActionProps",
        "objdata": {
            "TidalChange": {
                "ChangeAmount": resolve_tide_change_amount(tide_cfg, "events.tide_changes[]"),
                "ChangeType": str(tide_cfg.get("change_type", "absolute")),
            }
        },
    }
    return event_object, f"RTID({alias}@.)"


def get_wave_entry_alias(entry):
    if not isinstance(entry, dict):
        return None
    type_value = entry.get("Type")
    if not isinstance(type_value, str) or not type_value.strip():
        return None
    try:
        return extract_rtid_name(type_value, "wave_zombie.Type")
    except ValueError:
        return None


def get_wave_entry_row(entry):
    if not isinstance(entry, dict) or "Row" not in entry:
        return None
    try:
        return as_int(entry.get("Row"), "wave_zombie.Row")
    except ValueError:
        return None


def set_wave_entry_row(entry, row):
    if isinstance(entry, dict) and "Row" in entry:
        entry["Row"] = str(row)


def get_active_jam_names(active_jam):
    if active_jam is None:
        return set()
    if isinstance(active_jam, str):
        cleaned = active_jam.strip()
        return {cleaned} if cleaned else set()
    if isinstance(active_jam, (list, tuple, set)):
        names = set()
        for jam_name in active_jam:
            if isinstance(jam_name, str):
                cleaned = jam_name.strip()
                if cleaned:
                    names.add(cleaned)
        return names
    return set()


def wave_row_to_dino_row(row):
    if row is None:
        return None
    if row == 0:
        return 0
    return row - 1


def collect_wave_dino_support_rows(zombies_list):
    rows_by_alias = {}
    any_rows = set()

    if not isinstance(zombies_list, list):
        return rows_by_alias, any_rows

    for zombie in zombies_list:
        alias = get_wave_entry_alias(zombie)
        row = wave_row_to_dino_row(get_wave_entry_row(zombie))
        if alias is None or row is None or row < 0:
            continue
        alias_key = alias.casefold()
        any_rows.add(row)
        rows_by_alias.setdefault(alias_key, set()).add(row)

    return rows_by_alias, any_rows


def get_dino_action_configs(dino_cfg):
    actions = dino_cfg.get("actions", dino_cfg.get("dinos"))
    if actions is None:
        actions = [dino_cfg]
    if not isinstance(actions, list) or len(actions) == 0:
        raise ValueError("events.dino_ambushes[].actions must be a non-empty array")
    return actions


def get_dino_action_type(action_cfg, field_name):
    if isinstance(action_cfg, str):
        dino_type = action_cfg.strip()
    elif isinstance(action_cfg, dict):
        dino_type = str(
            action_cfg.get(
                "dino_type",
                action_cfg.get("DinoType", action_cfg.get("type", action_cfg.get("type_name", ""))),
            )
        ).strip()
    else:
        raise ValueError(f"{field_name} must be a string or object")

    if not dino_type:
        raise ValueError(f"{field_name}.dino_type is required")
    return dino_type


def get_dino_action_row(action_cfg, field_name):
    if not isinstance(action_cfg, dict):
        return None

    if "dino_row" not in action_cfg and "DinoRow" not in action_cfg and "row" not in action_cfg:
        return None

    row = as_int(
        action_cfg.get("dino_row", action_cfg.get("DinoRow", action_cfg.get("row"))),
        f"{field_name}.dino_row",
    )
    if row < 0:
        raise ValueError(f"{field_name}.dino_row must be >= 0")
    return row


def get_dino_required_rows(dino_type, wave_rows_by_alias, any_rows):
    dino_key = str(dino_type).strip().casefold()
    if dino_key == "ptero":
        rows = set()
        for zombie_alias in DINO_PTERO_SUPPORT_ZOMBIES:
            rows.update(wave_rows_by_alias.get(zombie_alias, set()))
        return rows
    if dino_key == "stego":
        return set(any_rows)
    return None


def can_spawn_dino_action(action_cfg, field_name, wave_rows_by_alias, any_rows):
    dino_type = get_dino_action_type(action_cfg, field_name)
    required_rows = get_dino_required_rows(dino_type, wave_rows_by_alias, any_rows)
    requested_row = get_dino_action_row(action_cfg, field_name)

    if required_rows is None:
        return True
    if requested_row is not None:
        return requested_row in required_rows
    return len(required_rows) > 0


def dino_event_has_spawnable_actions(dino_cfg, wave_zombies):
    wave_rows_by_alias, any_rows = collect_wave_dino_support_rows(wave_zombies)
    for idx, action_cfg in enumerate(get_dino_action_configs(dino_cfg)):
        if can_spawn_dino_action(
            action_cfg,
            f"events.dino_ambushes[].actions[{idx}]",
            wave_rows_by_alias,
            any_rows,
        ):
            return True
    return False


def move_wave_entry(entries, entry, target_index):
    current_index = None
    for idx, candidate in enumerate(entries):
        if candidate is entry:
            current_index = idx
            break
    if current_index is None:
        return

    item = entries.pop(current_index)
    if current_index < target_index:
        target_index -= 1
    target_index = max(0, min(target_index, len(entries)))
    entries.insert(target_index, item)


def apply_future_protector_layout(zombies_list, spawn_row_range):
    blocked_aliases = {
        "future_protector",
        "eighties_glitter",
        "eighties_glitter_8bit",
        "eighties_breakdancer",
        "eighties_breakdancer_8bit",
    }
    reserved_ids = set()

    for protector in list(zombies_list):
        if get_wave_entry_alias(protector) != "future_protector":
            continue
        protector_row = get_wave_entry_row(protector)
        if protector_row is None:
            continue

        target_rows = [
            row
            for row in [protector_row - 1, protector_row, protector_row + 1]
            if spawn_row_range[0] <= row <= spawn_row_range[1]
        ]
        if not target_rows:
            continue

        chosen = []
        for candidate in zombies_list:
            if candidate is protector or id(candidate) in reserved_ids:
                continue
            alias = get_wave_entry_alias(candidate)
            if alias in blocked_aliases:
                continue
            chosen.append(candidate)
            reserved_ids.add(id(candidate))
            if len(chosen) >= len(target_rows):
                break

        for row, candidate in zip(target_rows, chosen):
            set_wave_entry_row(candidate, row)
            protector_index = zombies_list.index(protector)
            move_wave_entry(zombies_list, candidate, protector_index + 1)


def apply_glitter_layout(zombies_list, spawn_row_range, active_jam):
    glitter_styles = {
        "eighties_glitter": "jam_pop",
        "eighties_glitter_8bit": "jam_8bit",
    }
    active_jam_names = get_active_jam_names(active_jam)
    blocked_aliases = set(glitter_styles) | {
        "eighties_breakdancer",
        "eighties_breakdancer_8bit",
        "future_protector",
    }
    reserved_ids = set()

    for glitter in list(zombies_list):
        glitter_alias = get_wave_entry_alias(glitter)
        if glitter_styles.get(glitter_alias) not in active_jam_names:
            continue
        glitter_row = get_wave_entry_row(glitter)
        if glitter_row is None:
            continue

        chosen = []
        for candidate in zombies_list:
            if candidate is glitter or id(candidate) in reserved_ids:
                continue
            alias = get_wave_entry_alias(candidate)
            if alias in blocked_aliases:
                continue
            chosen.append(candidate)
            reserved_ids.add(id(candidate))

        for candidate in chosen:
            set_wave_entry_row(candidate, glitter_row)
            glitter_index = zombies_list.index(glitter)
            move_wave_entry(zombies_list, candidate, glitter_index + 1)


def apply_breakdancer_layout(zombies_list, spawn_row_range, active_jam):
    breakdancer_styles = {
        "eighties_breakdancer": "jam_rap",
        "eighties_breakdancer_8bit": "jam_8bit",
    }
    active_jam_names = get_active_jam_names(active_jam)
    blocked_aliases = set(breakdancer_styles) | {
        "eighties_glitter",
        "eighties_glitter_8bit",
        "future_protector",
    }
    # Allow breakdancers to be companions to other breakdancers
    companion_blocked = blocked_aliases - set(breakdancer_styles)

    # Collect all breakdancers that match the active jam
    breakdancers = []
    for zombie in zombies_list:
        alias = get_wave_entry_alias(zombie)
        if breakdancer_styles.get(alias) in active_jam_names:
            row = get_wave_entry_row(zombie)
            if row is not None:
                breakdancers.append((zombie, row))

    if not breakdancers:
        return

    # Collect eligible companions (all zombies not in companion_blocked, and not breakdancers themselves? Wait, user wants to allow)
    # User says allow breakdancers in front, so remove breakdancers from blocked for companions
    eligible_companions = [z for z in zombies_list if get_wave_entry_alias(z) not in companion_blocked]

    # Remove breakdancers from eligible if we don't want them as companions, but user says allow
    # To allow, don't remove

    # Shuffle to randomize
    random.shuffle(eligible_companions)

    # Assign companions to breakdancers, each getting 1-5
    companion_index = 0
    for dancer, dancer_row in breakdancers:
        remaining = len(eligible_companions) - companion_index
        if remaining <= 0:
            num_companions = 0
        else:
            num_companions = random.randint(1, min(5, remaining))
        assigned = []
        for _ in range(num_companions):
            companion = eligible_companions[companion_index]
            companion_index += 1
            assigned.append(companion)

        # Move assigned to dancer's row and position
        for companion in assigned:
            set_wave_entry_row(companion, dancer_row)
            dancer_index = zombies_list.index(dancer)
            move_wave_entry(zombies_list, companion, dancer_index)


def apply_wave_layout_rules(zombies_list, spawn_row_range, active_jam):
    if not zombies_list or any("Row" not in zombie for zombie in zombies_list):
        return
    apply_future_protector_layout(zombies_list, spawn_row_range)
    if get_active_jam_names(active_jam):
        apply_glitter_layout(zombies_list, spawn_row_range, active_jam)
        apply_breakdancer_layout(zombies_list, spawn_row_range, active_jam)


def build_jam_notification_event(wave, jam_name, jam_cfg, existing_aliases):
    alias_prefix = str(jam_cfg.get("alias_prefix", "jam")).strip() or "jam"
    alias = make_unique_alias(f"{alias_prefix}{wave}_{jam_name}", existing_aliases)
    objdata = {
        "NotificationEvents": [jam_name],
    }
    
    # Randomize MusicType between MiniGame_A, MiniGame_B, or nothing (omit field)
    
    event_object = {
        "aliases": [alias],
        "objclass": "SpawnZombiesJitteredWaveActionProps",
        "objdata": objdata,
    }
    return event_object, f"RTID({alias}@.)"


def build_jam_state(jam_cfg, wave_count, stage_module, zombie_jam_styles):
    if jam_cfg is None:
        return {"active_by_wave": {}, "segment_starts": {}, "preferred_pick_chance": 0.0, "off_jam_suppression_chance": 0.0}
    if not isinstance(jam_cfg, dict):
        raise ValueError("jams must be an object")
    if not jam_cfg.get("enabled", False):
        return {"active_by_wave": {}, "segment_starts": {}, "preferred_pick_chance": 0.0, "off_jam_suppression_chance": 0.0}

    supported_stages = normalize_module_list(
        jam_cfg.get("supported_stage_modules", DEFAULT_JAM_STAGE_MODULES),
        "jams.supported_stage_modules",
    )
    if supported_stages and stage_module not in supported_stages:
        raise ValueError(
            "jams.enabled is true, but the current StageModule does not support jams: "
            f"{stage_module or '<missing>'}"
        )

    available_from_pool = sorted(set(zombie_jam_styles.values()))
    configured_jams = jam_cfg.get("available_jams")
    if configured_jams is None:
        available_jams = available_from_pool
    else:
        available_jams = normalize_string_list(configured_jams, "jams.available_jams")
        available_jams = [jam for jam in available_jams if jam in available_from_pool]
    if not available_jams:
        return {"active_by_wave": {}, "segment_starts": {}, "preferred_pick_chance": 0.0, "off_jam_suppression_chance": 0.0}

    if bool(jam_cfg.get("all_active", False)):
        start_wave = as_int(jam_cfg.get("start_wave", 1), "jams.start_wave")
        if start_wave < 1 or start_wave > wave_count:
            raise ValueError("jams.start_wave must be inside the level wave range")
        active_by_wave = {
            wave: available_jams[:]
            for wave in range(start_wave, wave_count + 1)
        }
        return {
            "active_by_wave": active_by_wave,
            "segment_starts": {},
            "preferred_pick_chance": 0.0,
            "off_jam_suppression_chance": 0.0,
        }

    preferred_pick_chance = as_number(
        jam_cfg.get("preferred_pick_chance", 0.8),
        "jams.preferred_pick_chance",
    )
    off_jam_suppression_chance = as_number(
        jam_cfg.get("off_jam_suppression_chance", 0.7),
        "jams.off_jam_suppression_chance",
    )
    preferred_pick_chance = max(0.0, min(1.0, preferred_pick_chance))
    off_jam_suppression_chance = max(0.0, min(1.0, off_jam_suppression_chance))

    schedule = []
    explicit_schedule = jam_cfg.get("schedule")
    if explicit_schedule is not None:
        if not isinstance(explicit_schedule, list):
            raise ValueError("jams.schedule must be an array")
        for idx, raw_segment in enumerate(explicit_schedule):
            if not isinstance(raw_segment, dict):
                raise ValueError(f"jams.schedule[{idx}] must be an object")
            jam_name = str(raw_segment.get("jam", "")).strip()
            if jam_name not in available_jams:
                raise ValueError(f'jams.schedule[{idx}].jam "{jam_name}" is not active in this zombie pool')
            start_wave = as_int(raw_segment.get("start_wave"), f"jams.schedule[{idx}].start_wave")
            end_wave = as_int(raw_segment.get("end_wave", start_wave), f"jams.schedule[{idx}].end_wave")
            if start_wave < 1 or end_wave > wave_count or end_wave < start_wave:
                raise ValueError(f"jams.schedule[{idx}] has an invalid wave range")
            schedule.append({"jam": jam_name, "start_wave": start_wave, "end_wave": end_wave})
    else:
        start_wave = as_int(jam_cfg.get("start_wave", 2), "jams.start_wave")
        if start_wave < 1 or start_wave > wave_count:
            raise ValueError("jams.start_wave must be inside the level wave range")
        segment_min, segment_max = parse_int_range(
            jam_cfg.get("segment_length_range", [2, 4]),
            "jams.segment_length_range",
        )
        gap_min, gap_max = parse_int_range(
            jam_cfg.get("gap_wave_range", [1, 2]),
            "jams.gap_wave_range",
        )
        allow_repeat = bool(jam_cfg.get("allow_repeat", False))
        jam_weights = jam_cfg.get("weights", {})
        if jam_weights is not None and not isinstance(jam_weights, dict):
            raise ValueError("jams.weights must be an object")

        current_wave = start_wave
        previous_jam = None
        while current_wave <= wave_count:
            candidate_jams = available_jams[:]
            if not allow_repeat and previous_jam in candidate_jams and len(candidate_jams) > 1:
                candidate_jams = [jam for jam in candidate_jams if jam != previous_jam]

            weighted = []
            for jam_name in candidate_jams:
                weight = as_number(
                    jam_weights.get(jam_name, 1),
                    f"jams.weights.{jam_name}",
                )
                if weight > 0:
                    weighted.append({"jam": jam_name, "weight": weight})
            if not weighted:
                break

            chosen_jam = pick_weighted_dict(weighted, "jams.weights")["jam"]
            segment_length = random.randint(segment_min, segment_max)
            end_wave = min(wave_count, current_wave + segment_length - 1)
            schedule.append({"jam": chosen_jam, "start_wave": current_wave, "end_wave": end_wave})
            previous_jam = chosen_jam
            current_wave = end_wave + 1 + random.randint(gap_min, gap_max)

    active_by_wave = {}
    segment_starts = {}
    for segment in sorted(schedule, key=lambda item: item["start_wave"]):
        for wave in range(segment["start_wave"], segment["end_wave"] + 1):
            active_by_wave[wave] = segment["jam"]
        segment_starts[segment["start_wave"]] = segment["jam"]

    return {
        "active_by_wave": active_by_wave,
        "segment_starts": segment_starts,
        "preferred_pick_chance": preferred_pick_chance,
        "off_jam_suppression_chance": off_jam_suppression_chance,
    }


def apply_jam_candidate_bias(valid_candidates, active_jam, jam_state, zombie_jam_styles):
    active_jam_names = get_active_jam_names(active_jam)
    if not active_jam_names or active_jam_names == {"jam_ballad"}:
        return valid_candidates
    if len(active_jam_names) != 1:
        return valid_candidates
    active_jam_name = next(iter(active_jam_names))

    non_off_jam = [
        zombie_name
        for zombie_name in valid_candidates
        if zombie_jam_styles.get(zombie_name) in {None, active_jam_name, JAM_ALL_STYLE}
    ]
    if (
        non_off_jam
        and len(non_off_jam) < len(valid_candidates)
        and random.random() < jam_state.get("off_jam_suppression_chance", 0.0)
    ):
        valid_candidates = non_off_jam

    jam_matches = [
        zombie_name
        for zombie_name in valid_candidates
        if zombie_jam_styles.get(zombie_name) in {active_jam_name, JAM_ALL_STYLE}
    ]
    if jam_matches and random.random() < jam_state.get("preferred_pick_chance", 0.0):
        return jam_matches

    return valid_candidates


def build_grid_spawn_event(
    wave,
    ambush_count,
    grid_cfg,
    existing_aliases,
    wave_points_remaining,
    generation_context=None,
):
    if generation_context is None:
        generation_context = {}

    alias_prefix = str(grid_cfg.get("alias_prefix", "GridSpawn"))
    event_name = str(grid_cfg.get("event_name", "grid_spawn")).strip() or "grid_spawn"
    alias = make_unique_alias(f"{alias_prefix}{wave}_{ambush_count}_{event_name}", existing_aliases)

    pool_source = str(grid_cfg.get("grid_pool_source", "")).strip()
    if pool_source:
        generated_grid_pools = generation_context.get("generated_grid_pools", {})
        if pool_source not in generated_grid_pools:
            raise ValueError(
                f'events.grid_spawns[].grid_pool_source "{pool_source}" was not generated'
            )
        pool = copy.deepcopy(generated_grid_pools[pool_source])
    else:
        raw_pool = grid_cfg.get("grid_pool", grid_cfg.get("GravestonePool"))
        pool = normalize_grid_item_pool(raw_pool, "events.grid_spawns[].grid_pool")

    raw_positions = grid_cfg.get("positions", grid_cfg.get("SpawnPositionsPool"))
    if raw_positions is not None:
        spawn_positions = normalize_grid_positions(raw_positions, "events.grid_spawns[].positions")
    else:
        spawn_x_range = parse_int_range(
            grid_cfg.get("spawn_x_range", [0, 8]),
            "events.grid_spawns[].spawn_x_range",
        )
        spawn_y_range = parse_int_range(
            grid_cfg.get("spawn_y_range", [0, 4]),
            "events.grid_spawns[].spawn_y_range",
        )
        all_positions = [
            {"mX": x, "mY": y}
            for x in range(spawn_x_range[0], spawn_x_range[1] + 1)
            for y in range(spawn_y_range[0], spawn_y_range[1] + 1)
        ]
        position_count_range = parse_int_range(
            grid_cfg.get("position_count_range", [len(pool), len(pool)]),
            "events.grid_spawns[].position_count_range",
        )
        position_count = random.randint(*position_count_range)
        unique_positions = bool(grid_cfg.get("unique_positions", True))
        if unique_positions and position_count > len(all_positions):
            raise ValueError(
                "events.grid_spawns[] requested more unique positions than the configured spawn area allows"
            )
        if unique_positions:
            spawn_positions = random.sample(all_positions, position_count)
        else:
            spawn_positions = [random.choice(all_positions) for _ in range(position_count)]

    event_object = {
        "aliases": [alias],
        "objclass": "SpawnGravestonesWaveActionProps",
        "objdata": {
            "GravestonePool": pool,
            "SpawnPositionsPool": spawn_positions,
            "SpawnEffectAnimID": str(grid_cfg.get("spawn_effect", grid_cfg.get("SpawnEffectAnimID", ""))),
            "SpawnSoundID": str(grid_cfg.get("spawn_sound_id", grid_cfg.get("SpawnSoundID", ""))),
            "DisplacePlants": bool(grid_cfg.get("displace_plants", grid_cfg.get("DisplacePlants", True))),
            "RandomPlacement": bool(grid_cfg.get("random_placement", grid_cfg.get("RandomPlacement", True))),
            "ShakeScreen": bool(grid_cfg.get("shake_screen", grid_cfg.get("ShakeScreen", False))),
            "GridClassesToDestroy": copy.deepcopy(
                grid_cfg.get("grid_classes_to_destroy", grid_cfg.get("GridClassesToDestroy", []))
            ),
        },
    }

    consume = bool(grid_cfg.get("consume_wave_points", True))
    if consume:
        portal_costs = generation_context.get("portal_costs", {})
        use_portal_costs = bool(grid_cfg.get("use_portal_costs", bool(pool_source and portal_costs)))
        if use_portal_costs and portal_costs and pool_source:
            # Compute weighted-average portal cost across the pool, then multiply by
            # the number of positions spawned.  Each pool entry has a "Count" weight;
            # we weight each portal's cost accordingly so the budget deduction matches
            # the expected value of whatever the game engine randomly picks.
            total_weight = 0.0
            weighted_cost_sum = 0.0
            for pool_entry in pool:
                rtid = pool_entry.get("Type", "")
                # RTID format: "RTID(alias@.)" — extract alias
                if rtid.startswith("RTID(") and "@" in rtid:
                    entry_alias = rtid.split("RTID(")[1].split("@")[0]
                else:
                    entry_alias = rtid
                entry_cost = portal_costs.get(entry_alias, 0.0)
                entry_weight = float(pool_entry.get("Count", 1))
                total_weight += entry_weight
                weighted_cost_sum += entry_cost * entry_weight
            avg_portal_cost = (weighted_cost_sum / total_weight) if total_weight > 0 else 0.0
            wave_points_remaining -= len(spawn_positions) * avg_portal_cost
        else:
            point_cost = as_number(grid_cfg.get("point_cost", 0), "grid_spawns[].point_cost")
            if point_cost > 0:
                wave_points_remaining -= len(spawn_positions) * point_cost

    return event_object, f"RTID({alias}@.)", wave_points_remaining


def build_frost_wind_event(wave, ambush_count, frost_cfg, existing_aliases, wave_points_remaining):
    if not frost_cfg.get("enabled", False):
        return None, None, wave_points_remaining

    raw_rows = frost_cfg.get("rows", [])
    if not isinstance(raw_rows, list) or len(raw_rows) == 0:
        raise ValueError("frost_cfg.rows must be a non-empty list")
    rows = []
    for idx, row_value in enumerate(raw_rows):
        normalized_row = as_int(row_value, f"frost_cfg.rows[{idx}]")
        if normalized_row not in rows:
            rows.append(normalized_row)

    if "lane_count_range" in frost_cfg:
        lane_count_range = parse_int_range(
            frost_cfg.get("lane_count_range"),
            "frost_cfg.lane_count_range",
        )
    elif "row_count_range" in frost_cfg:
        lane_count_range = parse_int_range(
            frost_cfg.get("row_count_range"),
            "frost_cfg.row_count_range",
        )
    else:
        lane_count_range = (len(rows), len(rows))

    min_lane_count, max_lane_count = lane_count_range
    if min_lane_count < 0:
        raise ValueError("frost lane_count_range minimum cannot be negative")
    max_lane_count = min(max_lane_count, len(rows))
    min_lane_count = min(min_lane_count, len(rows))
    if max_lane_count < min_lane_count:
        raise ValueError("frost lane_count_range maximum cannot be lower than minimum after row limits")

    point_cost_per_lane = as_number(
        frost_cfg.get("point_cost_per_lane", frost_cfg.get("point_cost", 0)),
        "frost_cfg.point_cost_per_lane",
    )
    if point_cost_per_lane < 0:
        raise ValueError("frost_cfg.point_cost_per_lane cannot be negative")
    consume_wave_points = bool(frost_cfg.get("consume_wave_points", point_cost_per_lane > 0))
    enforce_budget = bool(frost_cfg.get("enforce_budget", point_cost_per_lane > 0))
    allow_partial_budget = bool(frost_cfg.get("allow_partial_budget", True))

    affordable_lane_count = max_lane_count
    if enforce_budget and point_cost_per_lane > 0:
        affordable_lane_count = min(
            affordable_lane_count,
            int(wave_points_remaining // point_cost_per_lane),
        )

    if affordable_lane_count <= 0:
        return None, None, wave_points_remaining

    if affordable_lane_count < min_lane_count:
        if not allow_partial_budget:
            return None, None, wave_points_remaining
        lane_count = affordable_lane_count
    else:
        lane_count = random.randint(min_lane_count, affordable_lane_count)

    if lane_count <= 0:
        return None, None, wave_points_remaining

    if lane_count >= len(rows):
        rows = sorted(rows)
    else:
        rows = sorted(random.sample(rows, lane_count))

    pattern = frost_cfg.get("pattern", "split").lower()

    winds = []

    # -----------------------------
    # PATTERN: SPLIT (default)
    # -----------------------------
    if pattern == "split":
        mid = len(rows) // 2

        for i, row in enumerate(rows):
            direction = "left" if i < mid else "right"
            winds.append({
                "Direction": direction,
                "Row": str(row)
            })

    # -----------------------------
    # PATTERN: LEFT ONLY
    # -----------------------------
    elif pattern == "left":
        for row in rows:
            winds.append({"Direction": "left", "Row": str(row)})

    # -----------------------------
    # PATTERN: RIGHT ONLY
    # -----------------------------
    elif pattern == "right":
        for row in rows:
            winds.append({"Direction": "right", "Row": str(row)})

    # -----------------------------
    # PATTERN: ALTERNATE
    # -----------------------------
    elif pattern == "alternate":
        for i, row in enumerate(rows):
            direction = "left" if i % 2 == 0 else "right"
            winds.append({
                "Direction": direction,
                "Row": str(row)
            })

    # -----------------------------
    # PATTERN: RANDOM
    # -----------------------------
    elif pattern == "random":
        for row in rows:
            winds.append({
                "Direction": random.choice(["left", "right"]),
                "Row": str(row)
            })

    else:
        raise ValueError(f"Unknown frost pattern: {pattern}")

    # -----------------------------
    # BUILD ALIAS (frost_L...R...)
    # -----------------------------
    left_rows = []
    right_rows = []

    for w in winds:
        if w["Direction"] == "left":
            left_rows.append(w["Row"])
        else:
            right_rows.append(w["Row"])

    left_part = "L" + "".join(left_rows) if left_rows else ""
    right_part = "R" + "".join(right_rows) if right_rows else ""

    alias = make_unique_alias(
        f"frost_{left_part}{right_part}",
        existing_aliases
    )

    # -----------------------------
    # FINAL EVENT
    # -----------------------------
    event_object = {
        "aliases": [alias],
        "objclass": "FrostWindWaveActionProps",
        "objdata": {
            "Winds": winds
        }
    }

    if consume_wave_points and point_cost_per_lane > 0:
        wave_points_remaining = max(0.0, wave_points_remaining - (len(winds) * point_cost_per_lane))

    return event_object, f"RTID({alias}@.)", wave_points_remaining

def build_low_tide_events(
    wave,
    ambush_count,
    tide_cfg,
    wave_points_remaining,
    all_zombie_aliases,
    all_zombie_costs,
    existing_aliases,
    allow_flag_zombies=True,
    zombie_variant_groups=None,
    variant_alias_to_roll=None,
    last_tide_end=4,
):
    alias_prefix = str(tide_cfg.get("alias_prefix", "LowTide"))
    event_name = str(tide_cfg.get("event_name", "low_tide")).strip() or "low_tide"

    column_start = last_tide_end
    column_end = 7 if last_tide_end >= 7 else random.randint(last_tide_end + 1, 7)

    objects = []
    refs = []
    remaining = wave_points_remaining

    zombie_pool = tide_cfg.get("zombie_pool")
    if zombie_pool is not None:
        cleaned_pool = unique_zombie_pool(
            zombie_pool,
            "events.low_tides[].zombie_pool",
            variant_alias_to_roll=variant_alias_to_roll,
        )
        validated_pool = []
        for zombie_name in cleaned_pool:
            if zombie_name not in all_zombie_aliases:
                raise ValueError(f'events.low_tides[].zombie_pool contains "{zombie_name}" which was not found in ZombieTypes')
            if not allow_flag_zombies and is_flag_zombie_alias(zombie_name):
                continue
            validated_pool.append(zombie_name)
        cleaned_pool = validated_pool
        if len(cleaned_pool) == 0:
            return objects, refs, remaining, 7 if last_tide_end >= 7 else random.randint(last_tide_end + 1, 7)

        # Select zombies like sandstorm
        use_wave_points_budget = bool(tide_cfg.get("use_wave_points_budget", True))
        consume_wave_points = bool(tide_cfg.get("consume_wave_points", use_wave_points_budget))
        enforce_budget = bool(tide_cfg.get("enforce_budget", use_wave_points_budget))
        zombie_choice_greediness = as_number(tide_cfg.get("zombie_choice_greediness", 0.5), "low_tide.zombie_choice_greediness")
        points_budget = None
        if use_wave_points_budget:
            ratio_range = parse_float_range(tide_cfg.get("points_budget_ratio_range", [0.2, 0.6]), "low_tide.points_budget_ratio_range")
            points_budget = max(0.0, remaining * random.uniform(*ratio_range))

        allow_duplicate_zombies = bool(tide_cfg.get("allow_duplicate_zombies", True))
        zombies_per_spawner_range = parse_int_range(tide_cfg.get("zombies_per_spawner_range", [1, 2]), "low_tide.zombies_per_spawner_range")
        zombie_count = random.randint(*zombies_per_spawner_range)
        if not allow_duplicate_zombies and zombie_count > len(cleaned_pool):
            zombie_count = len(cleaned_pool)

        picked_rolls = []
        used_in_spawner = set()
        budget_remaining = points_budget
        while len(picked_rolls) < zombie_count:
            candidates = cleaned_pool
            if not allow_duplicate_zombies:
                candidates = [z for z in cleaned_pool if z not in used_in_spawner]
            if len(candidates) == 0:
                break
            if enforce_budget and budget_remaining is not None:
                affordable = [z for z in candidates if all_zombie_costs.get(z, 0.0) <= (budget_remaining + 1e-9)]
                if len(affordable) == 0:
                    break
                candidates = sorted(affordable, key=lambda name: all_zombie_costs[name])
            else:
                candidates = list(candidates)
            if len(candidates) == 1:
                zombie_name = candidates[0]
            elif zombie_choice_greediness >= 0.5:
                choice_count = max(1, int(len(candidates) * zombie_choice_greediness))
                zombie_name = random.choice(candidates[len(candidates) - choice_count :])
            else:
                choice_count = max(1, int(len(candidates) * (1 - zombie_choice_greediness)))
                zombie_name = random.choice(candidates[:choice_count])
            picked_rolls.append(zombie_name)
            used_in_spawner.add(zombie_name)
            if budget_remaining is not None and enforce_budget:
                budget_remaining -= all_zombie_costs.get(zombie_name, 0.0)
                budget_remaining = max(0.0, budget_remaining)

        if len(picked_rolls) == 0:
            return objects, refs, remaining, 7 if last_tide_end >= 7 else random.randint(last_tide_end + 1, 7)

        alias = make_unique_alias(f"{alias_prefix}{wave}_{event_name}", existing_aliases)
        picked_zombies = [
            pick_zombie_variant_alias(zombie_name, zombie_variant_groups)
            for zombie_name in picked_rolls
        ]
        # Group by zombie type
        from collections import Counter
        zombie_counts = Counter(picked_rolls)
        first = True
        for zombie_name, count in zombie_counts.items():
            zombie_alias = pick_zombie_variant_alias(zombie_name, zombie_variant_groups)
            alias = make_unique_alias(f"{alias_prefix}{wave}_{event_name}_{zombie_name.replace('_', '')}", existing_aliases)
            event_object = {
                "aliases": [alias],
                "objclass": "BeachStageEventZombieSpawnerProps",
                "objdata": {
                    "ColumnStart": column_start,
                    "ColumnEnd": column_end,
                    "ZombieCount": count,
                    "GroupSize": as_int(tide_cfg.get("group_size", 1), "events.low_tides[].group_size"),
                    "TimeBetweenGroups": str(tide_cfg.get("time_between_groups", "0.05")),
                    "ZombieName": zombie_alias,
                },
            }
            if first:
                event_object["objdata"]["WaveStartMessage"] = str(tide_cfg.get("wave_start_message", "Low Tide!"))
                first = False
            objects.append(event_object)
            refs.append(f"RTID({alias}@.)")
        points_spent = sum(all_zombie_costs.get(z, 0.0) for z in picked_rolls)
        if consume_wave_points:
            remaining = max(0.0, remaining - points_spent)
        return objects, refs, remaining, column_end

    # Variants logic
    variants = tide_cfg.get("variants")
    if variants is None:
        zombie_names = tide_cfg.get("zombie_names")
        if zombie_names is not None:
            if not isinstance(zombie_names, list) or len(zombie_names) == 0:
                raise ValueError("events.low_tides[].zombie_names must be a non-empty array")
            variants = [{"zombie_name": zombie_name} for zombie_name in zombie_names]
        else:
            variants = [{"zombie_name": tide_cfg.get("zombie_name")}]
    if not isinstance(variants, list) or len(variants) == 0:
        raise ValueError("events.low_tides[] must define zombie_name, zombie_names, or variants")

    count_mode = str(tide_cfg.get("count_mode", "fixed")).strip().lower()
    all_zombies = []
    for idx, variant in enumerate(variants):
        if not isinstance(variant, dict):
            raise ValueError(f"events.low_tides[].variants[{idx}] must be an object")
        zombie_name = str(variant.get("zombie_name", "")).strip()
        if not zombie_name:
            raise ValueError(f"events.low_tides[].variants[{idx}].zombie_name is required")
        if zombie_name not in all_zombie_aliases:
            raise ValueError(
                f'events.low_tides[].variants[{idx}].zombie_name "{zombie_name}" not found in ZombieTypes'
            )
        if not allow_flag_zombies and is_flag_zombie_alias(zombie_name):
            continue

        count = 0
        point_cost = None
        if count_mode == "fixed":
            count = as_int(
                variant.get("zombie_count", tide_cfg.get("zombie_count", 1)),
                f"events.low_tides[].variants[{idx}].zombie_count",
            )
        elif count_mode == "range":
            count_range = parse_int_range(
                variant.get("zombie_count_range", tide_cfg.get("zombie_count_range", [1, 2])),
                f"events.low_tides[].variants[{idx}].zombie_count_range",
            )
            count = random.randint(*count_range)
        elif count_mode == "points_based":
            point_cost = variant.get("point_cost", tide_cfg.get("point_cost", all_zombie_costs.get(zombie_name)))
            if point_cost is None:
                raise ValueError(
                    f'events.low_tides[].variants[{idx}] missing point cost and no zombie cost found for "{zombie_name}"'
                )
            point_cost = as_number(point_cost, f"events.low_tides[].variants[{idx}].point_cost")
            min_count = as_int(variant.get("min_count", tide_cfg.get("min_count", 1)), f"events.low_tides[].variants[{idx}].min_count")
            max_count = as_int(variant.get("max_count", tide_cfg.get("max_count", 4)), f"events.low_tides[].variants[{idx}].max_count")
            if max_count < min_count:
                raise ValueError("events.low_tides[].max_count cannot be less than min_count")
            affordable = int(remaining // point_cost)
            max_allowed = min(max_count, affordable)
            if max_allowed <= 0:
                continue
            if max_allowed < min_count:
                count = max_allowed
            else:
                count = random.randint(min_count, max_allowed)
        else:
            raise ValueError(
                "events.low_tides[].count_mode must be 'fixed', 'range', or 'points_based'"
            )

        if count <= 0:
            continue

        all_zombies.extend([zombie_name] * count)

        if count_mode == "points_based" and bool(tide_cfg.get("consume_wave_points", True)):
            remaining = max(0.0, remaining - (count * point_cost))

    if all_zombies:
        alias = make_unique_alias(f"{alias_prefix}{wave}_{event_name}", existing_aliases)
        zombies_list = [{"Type": f"RTID({z}@ZombieTypes)"} for z in all_zombies]
        event_object = {
            "aliases": [alias],
            "objclass": "BeachStageEventZombieSpawnerProps",
            "objdata": {
                "ColumnStart": column_start,
                "ColumnEnd": column_end,
                "Zombies": zombies_list,
                "GroupSize": as_int(tide_cfg.get("group_size", 1), "events.low_tides[].group_size"),
                "TimeBetweenGroups": str(tide_cfg.get("time_between_groups", "0.05")),
                "WaveStartMessage": str(tide_cfg.get("wave_start_message", "Low Tide!")),
            },
        }
        objects.append(event_object)
        refs.append(f"RTID({alias}@.)")

    return objects, refs, remaining, column_end


def build_grid_item_spawner_event(
    wave,
    ambush_count,
    spawner_cfg,
    all_zombie_aliases,
    existing_aliases,
    wave_points_remaining=None,
    all_zombie_costs=None,
    allow_flag_zombies=True,
    zombie_variant_groups=None,
    variant_alias_to_roll=None,
):
    alias_prefix = str(spawner_cfg.get("alias_prefix", "GridSpawner"))
    event_name = str(spawner_cfg.get("event_name", "grid_spawner")).strip() or "grid_spawner"
    alias = make_unique_alias(f"{alias_prefix}{wave}_{ambush_count}_{event_name}", existing_aliases)
    remaining = wave_points_remaining

    grid_types = normalize_grid_type_list(
        spawner_cfg.get("grid_types", spawner_cfg.get("GridTypes")),
        "events.necromancy_spawns[].grid_types",
    )
    raw_zombies = spawner_cfg.get("zombies", spawner_cfg.get("Zombies"))
    raw_zombie_pool = spawner_cfg.get("zombie_pool", spawner_cfg.get("ZombiePool"))
    zombies = []
    points_spent = 0.0

    if raw_zombies is not None:
        zombies = normalize_spawn_zombies_list(
            raw_zombies,
            "events.necromancy_spawns[].zombies",
            all_zombie_aliases,
        )
    elif raw_zombie_pool is not None:
        if all_zombie_costs is None:
            raise ValueError("events.necromancy_spawns[].zombie_pool requires zombie costs to be available")

        prepared_pool = prepare_weighted_zombie_pool(
            raw_zombie_pool,
            "events.necromancy_spawns[].zombie_pool",
            all_zombie_aliases=all_zombie_aliases,
            variant_alias_to_roll=variant_alias_to_roll,
        )
        if not allow_flag_zombies:
            prepared_pool = [entry for entry in prepared_pool if not is_flag_zombie_alias(entry["alias"])]
        if len(prepared_pool) == 0:
            return [], [], remaining

        use_wave_points_budget = bool(spawner_cfg.get("use_wave_points_budget", False))
        consume_wave_points = bool(spawner_cfg.get("consume_wave_points", use_wave_points_budget))
        enforce_budget = bool(spawner_cfg.get("enforce_budget", use_wave_points_budget))

        points_budget = None
        if use_wave_points_budget:
            base_remaining = max(0.0, wave_points_remaining or 0.0)
            ratio_range = parse_float_range(
                spawner_cfg.get("points_budget_ratio_range", [0.2, 0.6]),
                "events.necromancy_spawns[].points_budget_ratio_range",
            )
            points_budget = max(0.0, base_remaining * random.uniform(*ratio_range))
        elif "points_budget_range" in spawner_cfg:
            absolute_range = parse_float_range(
                spawner_cfg.get("points_budget_range"),
                "events.necromancy_spawns[].points_budget_range",
            )
            points_budget = max(0.0, random.uniform(*absolute_range))

        if "zombie_count" in spawner_cfg or "ZombieCount" in spawner_cfg:
            target_count = as_int(
                spawner_cfg.get("zombie_count", spawner_cfg.get("ZombieCount")),
                "events.necromancy_spawns[].zombie_count",
            )
        else:
            count_range = parse_int_range(
                spawner_cfg.get("zombie_count_range", spawner_cfg.get("ZombieCountRange", [1, 1])),
                "events.necromancy_spawns[].zombie_count_range",
            )
            target_count = random.randint(*count_range)

        allow_duplicate_zombies = bool(spawner_cfg.get("allow_duplicate_zombies", True))
        if target_count <= 0:
            return [], [], remaining

        budget_remaining = points_budget
        selected_aliases = []
        used_aliases = set()
        while len(selected_aliases) < target_count:
            candidates = prepared_pool
            if not allow_duplicate_zombies:
                candidates = [entry for entry in prepared_pool if entry["alias"] not in used_aliases]
            if len(candidates) == 0:
                break
            if enforce_budget and budget_remaining is not None:
                affordable = []
                for entry in candidates:
                    zombie_cost = all_zombie_costs.get(entry["alias"], 0.0)
                    if zombie_cost <= 0 or zombie_cost <= (budget_remaining + 1e-9):
                        affordable.append(entry)
                if len(affordable) == 0:
                    break
                candidates = affordable

            chosen = pick_weighted_entry(candidates, "events.necromancy_spawns[].zombie_pool")
            selected_aliases.append(pick_zombie_variant_alias(chosen["alias"], zombie_variant_groups))
            used_aliases.add(chosen["alias"])
            zombie_cost = all_zombie_costs.get(chosen["alias"], 0.0)
            points_spent += zombie_cost
            if budget_remaining is not None and enforce_budget:
                budget_remaining = max(0.0, budget_remaining - zombie_cost)

        if len(selected_aliases) == 0:
            return [], [], remaining

        zombies = [{"Type": f"RTID({alias_name}@ZombieTypes)"} for alias_name in selected_aliases]
        if consume_wave_points and wave_points_remaining is not None:
            remaining = max(0.0, wave_points_remaining - points_spent)
    else:
        raise ValueError("events.necromancy_spawns[] must define zombies/Zombies or zombie_pool/ZombiePool")

    if not allow_flag_zombies:
        zombies = [entry for entry in zombies if not is_flag_zombie_reference(entry.get("Type"))]
        if len(zombies) == 0:
            return [], [], remaining

    event_object = {
        "aliases": [alias],
        "objclass": "SpawnZombiesFromGridItemSpawnerProps",
        "objdata": {
            "WaveStartMessage": str(spawner_cfg.get("wave_start_message", spawner_cfg.get("WaveStartMessage", "Necromancy!"))),
            "ZombieSpawnWaitTime": spawner_cfg.get("zombie_spawn_wait_time", spawner_cfg.get("ZombieSpawnWaitTime", 0)),
            "SuppressActionIfNoGridItemsFound": bool(
                spawner_cfg.get(
                    "suppress_if_no_grid_items_found",
                    spawner_cfg.get("SuppressActionIfNoGridItemsFound", False),
                )
            ),
            "AdditionalPlantfood": str(
                spawner_cfg.get("additional_plantfood", spawner_cfg.get("AdditionalPlantfood", "0"))
            ),
            "GridTypes": grid_types,
            "Zombies": zombies,
        },
    }

    if event_name == "jurassic_panic_effects":
        # Pick random lanes from template config (default 1–3)
        raw_lane_range = spawner_cfg.get("lane_count_range", [1, 3])
        lane_min, lane_max = parse_int_range(raw_lane_range, "events.necromancy_spawns[].lane_count_range")
        lane_max = min(lane_max, 5)
        num_lanes = random.randint(lane_min, lane_max)
        chosen_rows = sorted(random.sample(range(5), num_lanes))

        spawn_positions = [
            {"mX": x, "mY": y} for y in chosen_rows for x in range(9)
        ]

        fling_alias = make_unique_alias(f"{alias_prefix}{wave}_{ambush_count}_jurassic_panic_fling", existing_aliases)
        fling_obj = {
            "aliases": [fling_alias],
            "objclass": "SpawnGravestonesWaveActionProps",
            "objdata": {
                "GravestonePool": [{"Count": 45, "Type": "RTID(dino_stampede_shuffler@GridItemTypes)"}],
                "SpawnPositionsPool": spawn_positions,
                "DisplacePlants": True,
                "RandomPlacement": False,
                "ShakeScreen": True,
                "GridClassesToDestroy": [],
            },
        }
        # One idiot per chosen lane so the game knows how many lanes to activate
        idiot_count = len(chosen_rows)
        event_object["objdata"]["GridTypes"] = [
            "RTID(dino_stampede_damager@GridItemTypes)",
            "RTID(dino_stampede_damager2@GridItemTypes)",
            "RTID(dino_stampede_damager3@GridItemTypes)",
            "RTID(dino_stampede_damager4@GridItemTypes)",
            "RTID(dino_stampede_damager5@GridItemTypes)",
        ]
        event_object["objdata"]["Zombies"] = [
            {"Type": "RTID(idiot@ZombieTypes)"} for _ in range(idiot_count)
        ]
        return [fling_obj, event_object], [f"RTID({fling_alias}@.)", f"RTID({alias}@.)"], remaining

    return [event_object], [f"RTID({alias}@.)"], remaining


def apply_dino_row_pressure(zombies_list, dino_row, is_ptero, zombie_rtid, fraction=0.40):
    """Reassign a fraction of eligible zombies' rows to dino_row.

    For ptero (is_ptero=True): only zombies whose type is in DINO_PTERO_SUPPORT_ZOMBIES
    are eligible for reassignment; the rest are left untouched.
    For other dinos: any zombie is eligible.
    The fraction cap ensures we never fill the *entire* wave into one row.
    """
    # Build reverse map: RTID string -> alias
    rtid_to_alias = {v: k for k, v in zombie_rtid.items()}

    eligible_indices = []
    for i, z in enumerate(zombies_list):
        if "Row" not in z:
            continue  # planks mode — no row to reassign
        alias = rtid_to_alias.get(z.get("Type", ""), "")
        if is_ptero:
            if alias in DINO_PTERO_SUPPORT_ZOMBIES:
                eligible_indices.append(i)
        else:
            eligible_indices.append(i)

    if not eligible_indices:
        return

    # Pick a random subset — at most `fraction` of ALL zombies, capped so we don't
    # dominate the wave.
    max_to_move = max(1, int(len(zombies_list) * fraction))
    count_to_move = random.randint(1, min(len(eligible_indices), max_to_move))
    chosen = random.sample(eligible_indices, count_to_move)
    for i in chosen:
        zombies_list[i]["Row"] = str(dino_row)


def build_dino_events(wave, ambush_count, dino_cfg, existing_aliases, wave_points_remaining, wave_zombies):
    alias_prefix = str(dino_cfg.get("alias_prefix", "Dino"))
    event_name = str(dino_cfg.get("event_name", "dino")).strip() or "dino"

    actions = get_dino_action_configs(dino_cfg)
    wave_rows_by_alias, any_rows = collect_wave_dino_support_rows(wave_zombies)

    objects = []
    refs = []
    main_action_count = 0

    def pick_weighted_pool_entry(pool, label, type_field="type_name"):
        weighted = []
        for pool_idx, entry in enumerate(pool):
            entry_label = f"{label}[{pool_idx}]"
            if isinstance(entry, str):
                weighted.append((entry, 1.0))
                continue
            if not isinstance(entry, dict):
                raise ValueError(f"{entry_label} must be a string or object")
            entry_name = str(entry.get(type_field, entry.get("type", entry.get("dino_type", entry.get("DinoType", ""))))).strip()
            if not entry_name:
                raise ValueError(f"{entry_label}.{type_field} is required")
            entry_weight = as_number(entry.get("weight", 1), f"{entry_label}.weight")
            if entry_weight < 0:
                raise ValueError(f"{entry_label}.weight cannot be negative")
            weighted.append((entry, entry_weight))

        if len(weighted) == 0:
            raise ValueError(f"{label} must contain at least one pool entry")

        total_weight = sum(weight for _, weight in weighted)
        if total_weight <= 0:
            return random.choice([entry for entry, _ in weighted])

        roll = random.uniform(0.0, total_weight)
        running = 0.0
        for entry, weight in weighted:
            running += weight
            if roll <= running:
                return entry
        return weighted[-1][0]

    def resolve_dino_row(action_cfg, field_name, dino_type):
        requested_row = get_dino_action_row(action_cfg, field_name)
        required_rows = get_dino_required_rows(dino_type, wave_rows_by_alias, any_rows)
        if required_rows is None:
            if requested_row is not None:
                return requested_row
            return random.randint(0, 4)
        if requested_row is not None:
            if requested_row in required_rows:
                return requested_row
            return None
        if len(required_rows) == 0:
            return None
        return random.choice(sorted(required_rows))

    selection_mode = str(dino_cfg.get("selection_mode", "")).strip().casefold()
    use_weighted_selection = selection_mode in {"weighted", "pool", "random_pool"}
    if selection_mode in {"all", "spawn_all"}:
        use_weighted_selection = False
    elif "dino_count" in dino_cfg or "dino_count_range" in dino_cfg:
        use_weighted_selection = True

    actions_to_spawn = actions
    if use_weighted_selection:
        spawnable_actions = [
            action_cfg
            for idx, action_cfg in enumerate(actions)
            if can_spawn_dino_action(
                action_cfg,
                f"events.dino_ambushes[].actions[{idx}]",
                wave_rows_by_alias,
                any_rows,
            )
        ]
        if len(spawnable_actions) == 0:
            return objects, refs, wave_points_remaining

        if "dino_count" in dino_cfg:
            dino_count_range = (
                as_int(dino_cfg.get("dino_count"), "events.dino_ambushes[].dino_count"),
                as_int(dino_cfg.get("dino_count"), "events.dino_ambushes[].dino_count"),
            )
        else:
            dino_count_range = parse_int_range(
                dino_cfg.get("dino_count_range", [1, 1]),
                "events.dino_ambushes[].dino_count_range",
            )

        allow_duplicate_dinos = bool(dino_cfg.get("allow_duplicate_dinos", False))
        max_count = dino_count_range[1]
        if not allow_duplicate_dinos:
            max_count = min(max_count, len(spawnable_actions))
        if max_count <= 0:
            return objects, refs, wave_points_remaining

        if max_count < dino_count_range[0]:
            target_count = max_count
        else:
            target_count = random.randint(dino_count_range[0], max_count)
        actions_to_spawn = []
        selection_pool = spawnable_actions[:]
        while len(actions_to_spawn) < target_count and selection_pool:
            chosen_action = pick_weighted_pool_entry(
                selection_pool,
                "events.dino_ambushes[].dinos",
                type_field="dino_type",
            )
            actions_to_spawn.append(chosen_action)
            if not allow_duplicate_dinos:
                selection_pool.remove(chosen_action)

    for idx, action_cfg in enumerate(actions_to_spawn):
        dino_type = get_dino_action_type(action_cfg, f"events.dino_ambushes[].actions[{idx}]")
        dino_row = resolve_dino_row(
            action_cfg,
            f"events.dino_ambushes[].actions[{idx}]",
            dino_type,
        )
        if dino_row is None:
            continue
        alias_suffix = f"{dino_type[0].upper()}{dino_row + 1}"
        alias = make_unique_alias(f"{alias_prefix}{wave}_{event_name}_{alias_suffix}", existing_aliases)
        event_object = {
            "aliases": [alias],
            "objclass": "DinoWaveActionProps",
            "objdata": {
                "DinoRow": dino_row,
                "DinoType": dino_type,
            },
        }
        objects.append(event_object)
        refs.append(f"RTID({alias}@.)")
        main_action_count += 1

        same_row_pool = action_cfg.get("same_row_pool") if isinstance(action_cfg, dict) else None
        if same_row_pool is None:
            same_row_pool = action_cfg.get("same_lane_pool") if isinstance(action_cfg, dict) else None
        if same_row_pool is not None:
            if not isinstance(same_row_pool, list) or len(same_row_pool) == 0:
                raise ValueError("events.dino_ambushes[].actions[].same_row_pool must be a non-empty array")

            same_row_point_cost = as_number(
                action_cfg.get("same_row_point_cost", action_cfg.get("same_lane_point_cost", dino_cfg.get("point_cost", 1))),
                "events.dino_ambushes[].actions[].same_row_point_cost",
            )
            if same_row_point_cost <= 0:
                raise ValueError("events.dino_ambushes[].actions[].same_row_point_cost must be > 0")

            same_row_count_range = parse_int_range(
                action_cfg.get("same_row_count_range", action_cfg.get("same_lane_count_range", [1, 1])),
                "events.dino_ambushes[].actions[].same_row_count_range",
            )
            affordable = int(wave_points_remaining // same_row_point_cost)
            max_allowed = min(same_row_count_range[1], affordable)
            if max_allowed >= same_row_count_range[0]:
                extra_count = random.randint(same_row_count_range[0], max_allowed)
                for extra_idx in range(extra_count):
                    extra_dino_type = pick_weighted_pool_entry(
                        same_row_pool,
                        f"events.dino_ambushes[].actions[{idx}].same_row_pool",
                    )
                    if not isinstance(extra_dino_type, str):
                        extra_dino_type = get_dino_action_type(
                            extra_dino_type,
                            f"events.dino_ambushes[].actions[{idx}].same_row_pool[{extra_idx}]",
                        )
                    extra_alias_suffix = f"{extra_dino_type[0].upper()}{dino_row + 1}SR{extra_idx + 1}"
                    extra_alias = make_unique_alias(
                        f"{alias_prefix}{wave}_{event_name}_{extra_alias_suffix}",
                        existing_aliases,
                    )
                    extra_event_object = {
                        "aliases": [extra_alias],
                        "objclass": "DinoWaveActionProps",
                        "objdata": {
                            "DinoRow": dino_row,
                            "DinoType": extra_dino_type,
                        },
                    }
                    objects.append(extra_event_object)
                    refs.append(f"RTID({extra_alias}@.)")
                wave_points_remaining -= extra_count * same_row_point_cost

    point_cost = as_number(dino_cfg.get("point_cost", 0), "dino_ambushes[].point_cost")
    consume = bool(dino_cfg.get("consume_wave_points", True))
    if point_cost > 0 and consume:
        wave_points_remaining -= main_action_count * point_cost

    return objects, refs, wave_points_remaining


def build_market_event(wave, ambush_count, market_cfg):
    alias_prefix = str(market_cfg.get("alias_prefix", "GridSpawn"))
    alias = f"{alias_prefix}{wave}_{ambush_count}"

    special_spawn_chance = as_number(
        market_cfg.get("special_grid_spawn_chance", 0.5),
        "events.market.special_grid_spawn_chance",
    )

    if random.random() < special_spawn_chance:
        special_items = market_cfg.get("special_grid_items", [])
        if not isinstance(special_items, list) or len(special_items) == 0:
            raise ValueError("events.market.special_grid_items must be a non-empty array")

        pool = [
            {"Count": 1, "Type": f"RTID({item}@GridItemTypes)"}
            for item in special_items
        ]
        special_x_range = parse_int_range(
            market_cfg.get("special_item_spawn_x_range", [3, 8]),
            "events.market.special_item_spawn_x_range",
        )
        special_y_range = parse_int_range(
            market_cfg.get("special_item_spawn_y_range", [0, 4]),
            "events.market.special_item_spawn_y_range",
        )
        spawn_positions = [
            {"mX": random.randint(*special_x_range), "mY": random.randint(*special_y_range)}
            for _ in special_items
        ]
        spawn_effect = str(
            market_cfg.get(
                "special_spawn_effect",
                "POPANIM_EFFECTS_TOMBSTONE_DARK_SPAWN_EFFECT",
            )
        )
    else:
        default_item = str(market_cfg.get("default_grid_item_type", "marketcardbox"))
        default_count_range = parse_int_range(
            market_cfg.get("default_grid_item_count_range", [1, 10]),
            "events.market.default_grid_item_count_range",
        )
        pool = [
            {
                "Count": random.randint(*default_count_range),
                "Type": f"RTID({default_item}@GridItemTypes)",
            }
        ]
        default_x_range = parse_int_range(
            market_cfg.get("default_item_spawn_x_range", [2, 8]),
            "events.market.default_item_spawn_x_range",
        )
        default_y_range = parse_int_range(
            market_cfg.get("default_item_spawn_y_range", [0, 4]),
            "events.market.default_item_spawn_y_range",
        )
        spawn_positions = [
            {"mX": random.randint(*default_x_range), "mY": random.randint(*default_y_range)}
            for _ in pool
        ]
        spawn_effect = str(market_cfg.get("default_spawn_effect", ""))

    event_object = {
        "aliases": [alias],
        "objclass": "SpawnGravestonesWaveActionProps",
        "objdata": {
            "GravestonePool": pool,
            "SpawnPositionsPool": spawn_positions,
            "SpawnEffectAnimID": spawn_effect,
            "SpawnSoundID": str(
                market_cfg.get("spawn_sound_id", "Play_Zomb_Egypt_TombRaiser_Grave_Rise")
            ),
            "DisplacePlants": bool(market_cfg.get("displace_plants", True)),
            "RandomPlacement": bool(market_cfg.get("random_placement", True)),
            "ShakeScreen": bool(market_cfg.get("shake_screen", False)),
            "GridClassesToDestroy": copy.deepcopy(
                market_cfg.get("grid_classes_to_destroy", [])
            ),
        },
    }

    return event_object, f"RTID({alias}@.)"


def build_sun_crash_events(wave, ambush_count, sun_cfg, sun_crash_state):
    msg_alias_prefix = str(sun_cfg.get("message_alias_prefix", "SunMsg"))
    crash_alias_prefix = str(sun_cfg.get("crash_alias_prefix", "SunCrash"))
    msg_alias = f"{msg_alias_prefix}{wave}_{ambush_count}"
    crash_alias = f"{crash_alias_prefix}{wave}_{ambush_count}"

    if not sun_crash_state["triggered"]:
        first_range = parse_float_range(
            sun_cfg.get("first_multiplier_range", [0.15, 0.8]),
            "events.sun_crash.first_multiplier_range",
        )
        multiplier = round(random.uniform(*first_range), 2)
        additive = 0
        set_new_multiplier = bool(sun_cfg.get("set_new_multiplier", True))
        set_new_additive = False
        sun_crash_state["triggered"] = True
    else:
        bad_chance = as_number(
            sun_cfg.get("repeat_bad_chance", 0.4),
            "events.sun_crash.repeat_bad_chance",
        )
        if random.random() < bad_chance:
            bad_range = parse_float_range(
                sun_cfg.get("repeat_bad_multiplier_range", [1.2, 2.75]),
                "events.sun_crash.repeat_bad_multiplier_range",
            )
            multiplier = round(random.uniform(*bad_range), 2)
            additive = 0
            set_new_multiplier = bool(sun_cfg.get("set_new_multiplier", True))
            set_new_additive = False
        else:
            good_mult_range = parse_float_range(
                sun_cfg.get("repeat_good_multiplier_range", [0.5, 0.85]),
                "events.sun_crash.repeat_good_multiplier_range",
            )
            good_add_range = parse_int_range(
                sun_cfg.get("repeat_good_additive_range", [5, 50]),
                "events.sun_crash.repeat_good_additive_range",
            )
            multiplier = round(random.uniform(*good_mult_range), 2)
            additive = random.randint(*good_add_range)
            set_new_multiplier = bool(sun_cfg.get("set_new_multiplier", True))
            set_new_additive = bool(sun_cfg.get("set_new_additive", True))

    message_obj = {
        "aliases": [msg_alias],
        "objclass": "SpawnZombiesFromGridItemSpawnerProps",
        "objdata": {
            "WaveStartMessage": str(sun_cfg.get("wave_start_message", "Sunconomy Crash!")),
            "ZombieSpawnWaitTime": 0,
            "SuppressActionIfNoGridItemsFound": False,
            "AdditionalPlantfood": "0",
            "GridTypes": [],
            "Zombies": [],
        },
    }
    crash_obj = {
        "aliases": [crash_alias],
        "objclass": "CapitalistWaveActionProperties",
        "objdata": {
            "PlantTypes": [],
            "NewCosts": [],
            "SetNewMultiplier": set_new_multiplier,
            "SetNewAdditive": set_new_additive,
            "NewMultiplier": multiplier,
            "NewAdditive": additive,
        },
    }

    refs = [f"RTID({msg_alias}@.)", f"RTID({crash_alias}@.)"]
    return [message_obj, crash_obj], refs

def build_raidpty_events(wave, ambush_count, raidpty_cfg, wave_points_remaining):
    raidpty_alias_prefix = str(raidpty_cfg.get("raidpty_alias_prefix", "RaidingParty"))
    raidpty_alias = f"{raidpty_alias_prefix}{wave}_{ambush_count}"

    swashbuckler_cost = as_number(
        raidpty_cfg.get("swashbuckler_point_cost", 1.5),
        "events.raidpty.swashbuckler_point_cost",
    )
    if swashbuckler_cost <= 0:
        raise ValueError("events.raidpty.swashbuckler_point_cost must be > 0")

    min_count = as_int(raidpty_cfg.get("min_swashbucklers", 2), "events.raidpty.min_swashbucklers")
    max_count = as_int(raidpty_cfg.get("max_swashbucklers", 20), "events.raidpty.max_swashbucklers")
    if max_count < min_count:
        raise ValueError("events.raidpty.max_swashbucklers cannot be less than min_swashbucklers")

    affordable = int(wave_points_remaining // swashbuckler_cost)
    if affordable <= 0:
        return [], [], wave_points_remaining

    max_allowed = min(max_count, affordable)
    if max_allowed < min_count:
        count = max_allowed
    else:
        count = random.randint(min_count, max_allowed)

    time_min, time_max = parse_float_range(
        raidpty_cfg.get("time_between_groups_range", [0.25, 4.0]),
        "events.raidpty.time_between_groups_range",
    )
    group_size = as_int(raidpty_cfg.get("group_size", 1), "events.raidpty.group_size")

    raidptyobj = {
        "aliases": [raidpty_alias],
        "objclass": "RaidingPartyZombieSpawnerProps",
        "objdata": {
            "SwashbucklerCount": count,
            "GroupSize": group_size,
            "TimeBetweenGroups": round(random.uniform(time_min, time_max), 3),
        },
    }

    new_remaining = max(0.0, wave_points_remaining - (count * swashbuckler_cost))
    refs = [f"RTID({raidpty_alias}@.)"]
    return [raidptyobj], refs, new_remaining


def build_Parrotrousle_events(wave, ambush_count, Parrotrousle_cfg, wave_points_remaining):
    parrotrousle_alias_prefix = str(
        Parrotrousle_cfg.get("parrotrousle_alias_prefix", "Parrotrousle")
    )
    Parrotrousle_alias = f"{parrotrousle_alias_prefix}{wave}_{ambush_count}"

    parrot_cost = as_number(
        Parrotrousle_cfg.get("parrot_point_cost", 3.0),
        "events.Parrotrousle.parrot_point_cost",
    )
    if parrot_cost <= 0:
        raise ValueError("events.Parrotrousle.parrot_point_cost must be > 0")

    min_parrots = as_int(Parrotrousle_cfg.get("min_parrots", 1), "events.Parrotrousle.min_parrots")
    max_parrots = as_int(Parrotrousle_cfg.get("max_parrots", 10), "events.Parrotrousle.max_parrots")
    if max_parrots < min_parrots:
        raise ValueError("events.Parrotrousle.max_parrots cannot be less than min_parrots")

    affordable = int(wave_points_remaining // parrot_cost)
    if affordable <= 0:
        return [], [], wave_points_remaining

    max_allowed = min(max_parrots, affordable)
    if max_allowed < min_parrots:
        numbparrots = max_allowed
    else:
        numbparrots = random.randint(min_parrots, max_allowed)

    grid_types = Parrotrousle_cfg.get("grid_types", ["RTID(crater@GridItemTypes)"])
    if not isinstance(grid_types, list):
        raise ValueError("events.Parrotrousle.grid_types must be an array")

    Parrotrousleobj = {
        "aliases": [Parrotrousle_alias],
        "objclass": "SpawnZombiesFromGridItemSpawnerProps",
        "objdata": {
            "WaveStartMessage": str(Parrotrousle_cfg.get("wave_start_message", "Parrotrousle!")),
            "ZombieSpawnWaitTime": as_number(
                Parrotrousle_cfg.get("zombie_spawn_wait_time", 0),
                "events.Parrotrousle.zombie_spawn_wait_time",
            ),
            "SuppressActionIfNoGridItemsFound": bool(
                Parrotrousle_cfg.get("suppress_if_no_grid_items_found", False)
            ),
            "AdditionalPlantfood": str(Parrotrousle_cfg.get("additional_plantfood", "0")),
            "GridTypes": grid_types,
            "Zombies": [{"Type": f"RTID(parrotrousle_{numbparrots}@ZombieTypes)"}],
        },
    }

    new_remaining = max(0.0, wave_points_remaining - (numbparrots * parrot_cost))
    refs = [f"RTID({Parrotrousle_alias}@.)"]
    return [Parrotrousleobj], refs, new_remaining

def build_parachute_rain_event(
    wave,
    ambush_count,
    parachute_cfg,
    wave_points_remaining,
    all_zombie_costs,
    all_zombie_aliases,
    existing_aliases,
    allow_flag_zombies=True,
    zombie_variant_groups=None,
    variant_alias_to_roll=None,
):
    alias_prefix = str(parachute_cfg.get("alias_prefix", "ParaRain"))
    spider_pool = parachute_cfg.get(
        "spider_zombie_pool",
        parachute_cfg.get("SpiderZombiePool", parachute_cfg.get("zombie_pool")),
    )
    if spider_pool is not None:
        prepared_pool = prepare_weighted_zombie_pool(
            spider_pool,
            "events.parachute_rains[].spider_zombie_pool",
            all_zombie_aliases=all_zombie_aliases,
            variant_alias_to_roll=variant_alias_to_roll,
            value_keys=("SpiderZombieName", "spider_zombie_name", "zombie_name", "type_name", "type", "Type"),
        )
        if not allow_flag_zombies:
            prepared_pool = [entry for entry in prepared_pool if not is_flag_zombie_alias(entry["alias"])]
        if len(prepared_pool) == 0:
            return None, wave_points_remaining
        spider_roll_name = pick_weighted_entry(
            prepared_pool,
            "events.parachute_rains[].spider_zombie_pool",
        )["alias"]
    else:
        spider_roll_name = parse_zombie_alias(
            parachute_cfg.get("spider_zombie_name", parachute_cfg.get("SpiderZombieName", "")),
            "events.parachute_rains[].spider_zombie_name",
            all_zombie_aliases=all_zombie_aliases,
            variant_alias_to_roll=variant_alias_to_roll,
        )
        if not allow_flag_zombies and is_flag_zombie_alias(spider_roll_name):
            return None, wave_points_remaining

    spider_zombie_name = pick_zombie_variant_alias(spider_roll_name, zombie_variant_groups)
    event_name = str(parachute_cfg.get("event_name", spider_roll_name)).strip() or spider_roll_name
    base_alias = f"{alias_prefix}{wave}_{event_name}"
    event_alias = make_unique_alias(base_alias, existing_aliases)
    is_stampede = spider_roll_name == "west_bull"

    default_cost = all_zombie_costs.get(spider_roll_name, all_zombie_costs.get(spider_zombie_name))
    point_cost = parachute_cfg.get("point_cost", parachute_cfg.get("PointCost", default_cost))
    if point_cost is None:
        raise ValueError(
            f'events.parachute_rains[{event_name}] missing point cost and no zombie cost found for "{spider_roll_name}"'
        )
    point_cost = as_number(point_cost, "events.parachute_rains[].point_cost")
    if point_cost <= 0:
        raise ValueError("events.parachute_rains[].point_cost must be > 0")

    count_mode = str(parachute_cfg.get("count_mode", parachute_cfg.get("CountMode", "points_based"))).strip().lower()
    enforce_points_budget = bool(parachute_cfg.get("enforce_points_budget", parachute_cfg.get("EnforcePointsBudget", True)))
    count = 0

    if "spider_count" in parachute_cfg or "SpiderCount" in parachute_cfg:
        count = as_int(
            parachute_cfg.get("spider_count", parachute_cfg.get("SpiderCount")),
            "events.parachute_rains[].spider_count",
        )
    elif count_mode == "points_based":
        min_count = as_int(parachute_cfg.get("min_count", 1), "events.parachute_rains[].min_count")
        max_count = as_int(parachute_cfg.get("max_count", 4), "events.parachute_rains[].max_count")
        if max_count < min_count:
            raise ValueError("events.parachute_rains[].max_count cannot be less than min_count")
        affordable = int(wave_points_remaining // point_cost)
        max_allowed = min(max_count, affordable)
        if max_allowed <= 0:
            return None, wave_points_remaining
        if max_allowed < min_count:
            count = max_allowed
        else:
            count = random.randint(min_count, max_allowed)
    elif count_mode == "range":
        count_range = parse_int_range(
            parachute_cfg.get("count_range", [1, 3]),
            "events.parachute_rains[].count_range",
        )
        count = random.randint(*count_range)
    elif count_mode == "fixed":
        count = as_int(parachute_cfg.get("fixed_count", parachute_cfg.get("FixedCount", 1)), "events.parachute_rains[].fixed_count")
    else:
        raise ValueError(
            f"Unknown events.parachute_rains[].count_mode: {count_mode}"
        )

    if enforce_points_budget:
        affordable = int(wave_points_remaining // point_cost)
        count = min(count, affordable)
    if count <= 0:
        return None, wave_points_remaining

    if "column_start_range" in parachute_cfg:
        start_min, start_max = parse_int_range(
            parachute_cfg.get("column_start_range"),
            "events.parachute_rains[].column_start_range",
        )
        column_start = random.randint(start_min, start_max)
    else:
        default_start = 9 if is_stampede else 5
        column_start = as_int(
            parachute_cfg.get("column_start", parachute_cfg.get("ColumnStart", default_start)),
            "events.parachute_rains[].column_start",
        )

    if "column_end_range" in parachute_cfg:
        end_min, end_max = parse_int_range(
            parachute_cfg.get("column_end_range"),
            "events.parachute_rains[].column_end_range",
        )
        column_end = random.randint(end_min, end_max)
    else:
        default_end = 10 if is_stampede else 7
        column_end = as_int(
            parachute_cfg.get("column_end", parachute_cfg.get("ColumnEnd", default_end)),
            "events.parachute_rains[].column_end",
        )

    if column_end < column_start:
        column_start, column_end = column_end, column_start

    event_object = {
        "aliases": [event_alias],
        "objclass": "ParachuteRainZombieSpawnerProps",
        "objdata": {
            "ColumnStart": column_start,
            "ColumnEnd": column_end,
            "GroupSize": as_int(
                parachute_cfg.get("group_size", parachute_cfg.get("GroupSize", 1)),
                "events.parachute_rains[].group_size",
            ),
            "TimeBetweenGroups": str(parachute_cfg.get("time_between_groups", parachute_cfg.get("TimeBetweenGroups", "0.2"))),
            "ZombieFallTime": str(parachute_cfg.get("zombie_fall_time", parachute_cfg.get("ZombieFallTime", "1.5"))),
            "SpiderZombieName": spider_zombie_name,
            "SpiderCount": count,
            "WaveStartMessage": str(
                parachute_cfg.get(
                    "wave_start_message",
                    parachute_cfg.get(
                        "WaveStartMessage",
                        default_wave_start_message(spider_roll_name, "Parachute Rain!"),
                    ),
                )
            ),
        },
    }

    consume_wave_points = bool(parachute_cfg.get("consume_wave_points", parachute_cfg.get("ConsumeWavePoints", True)))
    if consume_wave_points:
        new_remaining = max(0.0, wave_points_remaining - (count * point_cost))
    else:
        new_remaining = wave_points_remaining

    return event_object, new_remaining

def build_imp_ambush_event(
    wave,
    imp_cfg,
    imp_points_remaining,
    allow_flag_zombies=True,
    all_zombie_aliases=None,
    zombie_variant_groups=None,
    variant_alias_to_roll=None,
):
    event_name = str(imp_cfg.get("event_name", "imp_ambush"))
    zombie_pool = imp_cfg.get("zombie_pool")
    if zombie_pool is not None:
        cleaned_pool = unique_zombie_pool(
            zombie_pool,
            "events.imp_ambushes[].zombie_pool",
            variant_alias_to_roll=variant_alias_to_roll,
        )
        if all_zombie_aliases is not None:
            missing = [zombie_name for zombie_name in cleaned_pool if zombie_name not in all_zombie_aliases]
            if missing:
                raise ValueError(
                    "events.imp_ambushes[].zombie_pool contains aliases missing from ZombieTypes: "
                    + ", ".join(sorted(set(missing)))
                )
        spider_zombie_name = pick_zombie_variant_alias(random.choice(cleaned_pool), zombie_variant_groups)
    else:
        spider_zombie_name = str(imp_cfg.get("spider_zombie_name", "")).strip()
        if not spider_zombie_name:
            raise ValueError(
                f"events.imp_ambushes[{event_name}].spider_zombie_name is required"
            )
    if not allow_flag_zombies and is_flag_zombie_alias(spider_zombie_name):
        return None, imp_points_remaining

    spider_mode = str(imp_cfg.get("spider_count_mode", "points_based")).strip().lower()
    spider_count = 0

    # Set column_start early for cost calculation
    if "column_start_range" in imp_cfg:
        column_start_range = parse_int_range(
            imp_cfg.get("column_start_range", [0, 8]),
            "imp_ambush.column_start_range",
        )
        column_start = random.randint(*column_start_range)
    else:
        column_start = as_int(imp_cfg.get("column_start", 4), "imp_ambush.column_start")

    # Set column_end
    if "column_end_range" in imp_cfg:
        column_end_range = parse_int_range(
            imp_cfg.get("column_end_range", [0, 8]),
            "imp_ambush.column_end_range",
        )
        column_end = random.randint(*column_end_range)
    else:
        column_end = as_int(imp_cfg.get("column_end", 8), "imp_ambush.column_end")
    if column_end < column_start:
        column_start, column_end = column_end, column_start

    # Set point_cost based on column_start if not specified
    if 'point_cost' not in imp_cfg:
        if column_start in [2, 3]:
            point_cost = 2.0
        elif column_start == 4:
            point_cost = 1.5
        else:
            point_cost = 1.0
    else:
        point_cost = as_number(imp_cfg.get("point_cost"), "imp_ambush.point_cost")

    if spider_mode == "points_based":
        min_count = as_int(imp_cfg.get("min_count", 1), "imp_ambush.min_count")
        max_count = as_int(imp_cfg.get("max_count", 6), "imp_ambush.max_count")
        if max_count < min_count:
            raise ValueError("imp_ambush.max_count cannot be less than min_count")

        if 'point_cost' not in imp_cfg:
            if column_start in [2, 3]:
                default_cost = 2
            elif column_start == 4:
                default_cost = 1.5
            else:
                default_cost = 1
        else:
            default_cost = 1
        point_cost = as_number(imp_cfg.get("point_cost", default_cost), "imp_ambush.point_cost")
        if point_cost <= 0:
            raise ValueError("imp_ambush.point_cost must be > 0 for points_based mode")

        affordable = int(imp_points_remaining // point_cost)
        max_allowed = min(max_count, affordable)
        if max_allowed <= 0:
            return None, imp_points_remaining

        if max_allowed < min_count:
            spider_count = max_allowed
        else:
            spider_count = random.randint(min_count, max_allowed)
    elif spider_mode == "range":
        count_range = parse_int_range(
            imp_cfg.get("count_range", [1, 1]),
            "imp_ambush.count_range",
        )
        spider_count = random.randint(*count_range)
    elif spider_mode == "fixed":
        spider_count = as_int(imp_cfg.get("fixed_count", 1), "imp_ambush.fixed_count")
    else:
        raise ValueError(f"Unknown imp_ambush spider_count_mode: {spider_mode}")

    if "zombies_per_spawner_range" in imp_cfg:
        count_range = parse_int_range(imp_cfg.get("zombies_per_spawner_range"), "imp_ambushes[].zombies_per_spawner_range")
        spider_count = random.randint(*count_range)

    if spider_count <= 0:
        return None, imp_points_remaining

    point_cost = as_number(imp_cfg.get("point_cost", point_cost), "imp_ambushes[].point_cost")
    consume = bool(imp_cfg.get("consume_wave_points", True))
    if point_cost > 0 and consume:
        affordable = int(imp_points_remaining // point_cost)
        spider_count = min(spider_count, affordable)
        if spider_count <= 0:
            return None, imp_points_remaining
        imp_points_remaining -= spider_count * point_cost

    alias_prefix = str(imp_cfg.get("alias_prefix", "SpidRain"))
    alias = f"{alias_prefix}{wave}_{event_name}"

    event_object = {
        "aliases": [alias],
        "objclass": "SpiderRainZombieSpawnerProps",
        "objdata": {
            "ColumnStart": column_start,
            "ColumnEnd": column_end,
            "GroupSize": as_int(imp_cfg.get("group_size", 1), "imp_ambush.group_size"),
            "TimeBetweenGroups": str(imp_cfg.get("time_between_groups", "0.5")),
            "ZombieFallTime": str(imp_cfg.get("zombie_fall_time", "2")),
            "SpiderZombieName": spider_zombie_name,
            "SpiderCount": spider_count,
            "WaveStartMessage": str(
                imp_cfg.get(
                    "wave_start_message",
                    default_wave_start_message(spider_zombie_name, ""),
                )
            ),
        },
    }

    return event_object, imp_points_remaining


def build_sandstorm_ambush_events(
    wave,
    storm_cfg,
    selected_pool,
    all_zombie_aliases,
    existing_aliases,
    zombie_costs,
    wave_points_remaining,
    allow_flag_zombies=True,
    zombie_variant_groups=None,
    variant_alias_to_roll=None,
):
    storm_type = str(storm_cfg.get("storm_type", "sandstorm")).strip() or "sandstorm"
    default_alias_prefix = "".join(part.capitalize() for part in storm_type.split("_")) or "Storm"
    alias_prefix = str(storm_cfg.get("alias_prefix", default_alias_prefix))
    additional_pf = storm_cfg.get("additional_plantfood", storm_cfg.get("AdditionalPlantfood", "0"))
    time_between_groups = as_number(
        storm_cfg.get("time_between_groups", storm_cfg.get("TimeBetweenGroups", 0.5)),
        "sandstorm.time_between_groups",
    )
    group_size = as_int(storm_cfg.get("group_size", storm_cfg.get("GroupSize", 1)), "sandstorm.group_size")
    include_ambush_index = bool(storm_cfg.get("include_ambush_index_in_alias", False))

    def validate_zombie_alias(zombie_alias, field_name):
        if zombie_alias not in all_zombie_aliases:
            raise ValueError(
                f'{field_name}: "{zombie_alias}" was not found in ZombieTypes aliases'
            )

    def make_storm_object(column, zombies, ambush_index=None):
        base_alias = f"{alias_prefix}{wave}_C{column}"
        if include_ambush_index and ambush_index is not None:
            base_alias = f"{alias_prefix}{wave}_A{ambush_index}_C{column}"
        alias = make_unique_alias(base_alias, existing_aliases)
        zombies_list = [{"Type": f"RTID({z}@ZombieTypes)"} for z in zombies]
        return {
            "aliases": [alias],
            "objclass": "StormZombieSpawnerProps",
            "objdata": {
                "AdditionalPlantfood": str(additional_pf),
                "Type": storm_type,
                "ColumnStart": column,
                "ColumnEnd": column,
                "TimeBetweenGroups": time_between_groups,
                "GroupSize": group_size,
                "Zombies": zombies_list,
            },
        }, f"RTID({alias}@.)"

    objects = []
    refs = []
    points_spent = 0.0

    use_wave_points_budget = bool(storm_cfg.get("use_wave_points_budget", False))
    consume_wave_points = bool(storm_cfg.get("consume_wave_points", use_wave_points_budget))
    enforce_budget = bool(storm_cfg.get("enforce_budget", use_wave_points_budget))
    zombie_choice_greediness = as_number(
        storm_cfg.get("zombie_choice_greediness", 0.5),
        "sandstorm.zombie_choice_greediness",
    )
    zombie_choice_greediness = max(0.0, min(1.0, zombie_choice_greediness))

    points_budget = None
    if use_wave_points_budget:
        ratio_range = parse_float_range(
            storm_cfg.get("points_budget_ratio_range", [0.2, 0.6]),
            "sandstorm.points_budget_ratio_range",
        )
        points_budget = max(0.0, wave_points_remaining * random.uniform(*ratio_range))

        if "points_budget_range" in storm_cfg:
            absolute_range = parse_float_range(
                storm_cfg.get("points_budget_range"),
                "sandstorm.points_budget_range",
            )
            points_budget = min(points_budget, random.uniform(*absolute_range))

        points_budget = max(0.0, points_budget)
    elif "points_budget_range" in storm_cfg:
        absolute_range = parse_float_range(
            storm_cfg.get("points_budget_range"),
            "sandstorm.points_budget_range",
        )
        points_budget = max(0.0, random.uniform(*absolute_range))

    explicit_spawners = storm_cfg.get("spawners")
    if explicit_spawners is not None:
        if not isinstance(explicit_spawners, list) or len(explicit_spawners) == 0:
            raise ValueError("sandstorm.spawners must be a non-empty array")
        remaining_budget = points_budget
        for idx, spawner in enumerate(explicit_spawners, 1):
            if not isinstance(spawner, dict):
                raise ValueError("sandstorm.spawners entries must be objects")
            column = as_int(spawner.get("column"), f"sandstorm.spawners[{idx}].column")
            zombies = spawner.get("zombies", spawner.get("Zombies", []))
            if not isinstance(zombies, list) or len(zombies) == 0:
                raise ValueError(f"sandstorm.spawners[{idx}].zombies must be non-empty")
            cleaned_zombies = []
            for z_idx, zombie_entry in enumerate(zombies):
                if isinstance(zombie_entry, str):
                    zombie_name = parse_zombie_alias(
                        zombie_entry,
                        f"sandstorm.spawners[{idx}].zombies[{z_idx}]",
                        all_zombie_aliases=all_zombie_aliases,
                        variant_alias_to_roll=variant_alias_to_roll,
                    )
                elif isinstance(zombie_entry, dict):
                    zombie_name = parse_zombie_alias(
                        zombie_entry.get("Type", zombie_entry.get("zombie_name", zombie_entry.get("type_name", zombie_entry.get("type")))),
                        f"sandstorm.spawners[{idx}].zombies[{z_idx}]",
                        all_zombie_aliases=all_zombie_aliases,
                        variant_alias_to_roll=variant_alias_to_roll,
                    )
                else:
                    raise ValueError(
                        f"sandstorm.spawners[{idx}].zombies[{z_idx}] must be a non-empty string or object"
                    )
                validate_zombie_alias(
                    zombie_name, f"sandstorm.spawners[{idx}].zombies[{z_idx}]"
                )
                if not allow_flag_zombies and is_flag_zombie_alias(zombie_name):
                    continue
                if enforce_budget and remaining_budget is not None:
                    zombie_cost = zombie_costs.get(zombie_name, 0.0)
                    if zombie_cost > 0 and zombie_cost <= (remaining_budget + 1e-9):
                        cleaned_zombies.append(zombie_name)
                        remaining_budget -= zombie_cost
                    elif zombie_cost <= 0:
                        cleaned_zombies.append(zombie_name)
                else:
                    cleaned_zombies.append(zombie_name)

            if len(cleaned_zombies) == 0:
                continue

            obj, ref = make_storm_object(column, cleaned_zombies, ambush_index=idx)
            objects.append(obj)
            refs.append(ref)
            for zombie_name in cleaned_zombies:
                points_spent += zombie_costs.get(zombie_name, 0.0)

        if consume_wave_points:
            wave_points_remaining = max(0.0, wave_points_remaining - points_spent)
        return objects, refs, wave_points_remaining

    columns = storm_cfg.get("columns")
    if columns is None:
        column_range = parse_int_range(
            storm_cfg.get("column_range", [3, 8]),
            "sandstorm.column_range",
        )
        columns = list(range(column_range[0], column_range[1] + 1))
    else:
        if not isinstance(columns, list) or len(columns) == 0:
            raise ValueError("sandstorm.columns must be a non-empty array")
        normalized_columns = []
        for idx, value in enumerate(columns):
            normalized_columns.append(as_int(value, f"sandstorm.columns[{idx}]"))
        columns = normalized_columns

    spawner_count_range = parse_int_range(
        storm_cfg.get("spawners_per_trigger_range", [1, 1]),
        "sandstorm.spawners_per_trigger_range",
    )
    spawner_count = random.randint(*spawner_count_range)

    unique_columns = bool(storm_cfg.get("unique_columns_per_trigger", True))
    if unique_columns:
        if spawner_count > len(columns):
            raise ValueError(
                "sandstorm.spawners_per_trigger_range max is greater than available unique columns"
            )
        picked_columns = random.sample(columns, spawner_count)
    else:
        picked_columns = [random.choice(columns) for _ in range(spawner_count)]

    zombies_per_spawner_range = parse_int_range(
        storm_cfg.get("zombies_per_spawner_range", [1, 2]),
        "sandstorm.zombies_per_spawner_range",
    )

    zombie_pool = storm_cfg.get("zombie_pool", storm_cfg.get("ZombiePool"))
    if zombie_pool is None:
        zombie_pool = selected_pool
    cleaned_pool = unique_zombie_pool(
        zombie_pool,
        "sandstorm.zombie_pool",
        variant_alias_to_roll=variant_alias_to_roll,
    )

    validated_pool = []
    for idx, zombie_name in enumerate(cleaned_pool):
        validate_zombie_alias(zombie_name, f"sandstorm.zombie_pool[{idx}]")
        if not allow_flag_zombies and is_flag_zombie_alias(zombie_name):
            continue
        validated_pool.append(zombie_name)
    cleaned_pool = validated_pool

    if len(cleaned_pool) == 0:
        return objects, refs, wave_points_remaining

    allow_duplicate_zombies = bool(storm_cfg.get("allow_duplicate_zombies", True))
    remaining_budget = points_budget

    def pick_zombie_with_budget(pool, used_in_spawner):
        candidates = pool
        if not allow_duplicate_zombies:
            candidates = [z for z in pool if z not in used_in_spawner]
        if len(candidates) == 0:
            return None

        if enforce_budget and remaining_budget is not None:
            affordable = [
                z for z in candidates if zombie_costs.get(z, 0.0) > 0 and zombie_costs[z] <= (remaining_budget + 1e-9)
            ]
            if len(affordable) == 0:
                return None
            candidates = sorted(affordable, key=lambda name: zombie_costs[name])
        else:
            candidates = list(candidates)

        if len(candidates) == 1:
            return candidates[0]

        if zombie_choice_greediness >= 0.5:
            choice_count = max(1, int(len(candidates) * zombie_choice_greediness))
            return random.choice(candidates[len(candidates) - choice_count :])
        choice_count = max(1, int(len(candidates) * (1 - zombie_choice_greediness)))
        return random.choice(candidates[:choice_count])

    for spawner_idx, column in enumerate(picked_columns, 1):
        zombie_count = random.randint(*zombies_per_spawner_range)
        if not allow_duplicate_zombies and zombie_count > len(cleaned_pool):
            raise ValueError(
                "sandstorm.zombies_per_spawner_range max is greater than zombie_pool size while duplicates are disabled"
            )

        min_per_spawner = zombies_per_spawner_range[0]
        picked_rolls = []
        used_in_spawner = set()

        while len(picked_rolls) < zombie_count:
            zombie_name = pick_zombie_with_budget(cleaned_pool, used_in_spawner)
            if zombie_name is None:
                break
            picked_rolls.append(zombie_name)
            used_in_spawner.add(zombie_name)
            if remaining_budget is not None and enforce_budget:
                remaining_budget -= zombie_costs.get(zombie_name, 0.0)
                remaining_budget = max(0.0, remaining_budget)

        if len(picked_rolls) < min_per_spawner:
            continue

        picked_zombies = [
            pick_zombie_variant_alias(zombie_name, zombie_variant_groups)
            for zombie_name in picked_rolls
        ]
        obj, ref = make_storm_object(column, picked_zombies, ambush_index=spawner_idx)
        objects.append(obj)
        refs.append(ref)
        for zombie_name in picked_rolls:
            points_spent += zombie_costs.get(zombie_name, 0.0)

    if consume_wave_points:
        wave_points_remaining = max(0.0, wave_points_remaining - points_spent)

    return objects, refs, wave_points_remaining


def normalize_grid_position(raw_position, field_name):
    if not isinstance(raw_position, dict):
        raise ValueError(f"{field_name} must be an object with x/y or GridX/GridY")
    if "x" in raw_position:
        x_value = raw_position.get("x")
    else:
        x_value = raw_position.get("GridX")
    if "y" in raw_position:
        y_value = raw_position.get("y")
    else:
        y_value = raw_position.get("GridY")

    x = as_int(x_value, f"{field_name}.x")
    y = as_int(y_value, f"{field_name}.y")
    return x, y


def build_initial_grid_item_object(initial_cfg, generation_context=None):
    if not isinstance(initial_cfg, dict):
        raise ValueError("initial_grid_items must be an object")
    if not initial_cfg.get("enabled", False):
        return None
    if generation_context is None:
        generation_context = {}

    alias = str(initial_cfg.get("alias", "GI"))
    allow_overlap = bool(initial_cfg.get("allow_overlap", False))
    module_rtid = str(initial_cfg.get("module_rtid", f"RTID({alias}@CurrentLevel)"))

    global_x_range = parse_int_range(
        initial_cfg.get("x_range", [0, 8]),
        "initial_grid_items.x_range",
    )
    global_y_range = parse_int_range(
        initial_cfg.get("y_range", [0, 4]),
        "initial_grid_items.y_range",
    )
    expected_pattern_rows = list(range(global_y_range[0], global_y_range[1] + 1))
    plank_rows = set(generation_context.get("plank_rows", []))

    column_region_ranges = {
        "back": (0, 4),
        "middle": (3, 5),
        "front": (5, 8),
    }
    raw_column_regions = initial_cfg.get("column_regions")
    if raw_column_regions is not None:
        if not isinstance(raw_column_regions, dict):
            raise ValueError("initial_grid_items.column_regions must be an object")
        column_region_ranges = {}
        for region_name, raw_range in raw_column_regions.items():
            region_key = str(region_name).strip().lower()
            if not region_key:
                raise ValueError("initial_grid_items.column_regions keys must be non-empty strings")
            column_region_ranges[region_key] = parse_int_range(
                raw_range,
                f"initial_grid_items.column_regions[{region_name!r}]",
            )

    minimum_nonzero_total_count = initial_cfg.get("minimum_nonzero_total_count")
    if minimum_nonzero_total_count is not None:
        minimum_nonzero_total_count = as_int(
            minimum_nonzero_total_count,
            "initial_grid_items.minimum_nonzero_total_count",
        )
        if minimum_nonzero_total_count < 0:
            raise ValueError("initial_grid_items.minimum_nonzero_total_count cannot be negative")

    raw_disallowed_totals = initial_cfg.get("disallowed_total_counts", [])
    if not isinstance(raw_disallowed_totals, list):
        raise ValueError("initial_grid_items.disallowed_total_counts must be an array")
    disallowed_total_counts = {
        as_int(value, f"initial_grid_items.disallowed_total_counts[{idx}]")
        for idx, value in enumerate(raw_disallowed_totals)
    }

    occupied = set()
    placements = []
    pool_entries = initial_cfg.get("pool")

    def normalize_total_count(target_total, count_range):
        valid_totals = []
        for total in range(count_range[0], count_range[1] + 1):
            if total in disallowed_total_counts:
                continue
            if minimum_nonzero_total_count is not None and 0 < total < minimum_nonzero_total_count:
                continue
            valid_totals.append(total)

        if not valid_totals:
            raise ValueError("initial_grid_items total_count rules leave no valid totals")

        if target_total in valid_totals:
            return target_total
        if target_total > 0:
            higher = [total for total in valid_totals if total >= target_total]
            if higher:
                return higher[0]
        return valid_totals[0]

    def resolve_candidate_rows(entry, entry_label):
        entry_y_range = parse_int_range(
            entry.get("y_range", list(global_y_range)),
            f"{entry_label}.y_range",
        )
        allowed_rows = set(range(entry_y_range[0], entry_y_range[1] + 1))

        raw_allowed_rows = entry.get("allowed_rows")
        if raw_allowed_rows is not None:
            allowed_rows &= {
                as_int(value, f"{entry_label}.allowed_rows[{idx}]")
                for idx, value in enumerate(normalize_int_list(raw_allowed_rows, f"{entry_label}.allowed_rows"))
            }

        raw_forbidden_rows = entry.get("forbidden_rows", entry.get("disallowed_rows"))
        if raw_forbidden_rows is not None:
            forbidden_rows = {
                as_int(value, f"{entry_label}.forbidden_rows[{idx}]")
                for idx, value in enumerate(normalize_int_list(raw_forbidden_rows, f"{entry_label}.forbidden_rows"))
            }
            allowed_rows -= forbidden_rows

        if bool(entry.get("requires_planks", False)):
            allowed_rows &= plank_rows

        return sorted(allowed_rows)

    def resolve_candidate_columns(entry, entry_label):
        entry_x_range = parse_int_range(
            entry.get("x_range", list(global_x_range)),
            f"{entry_label}.x_range",
        )
        allowed_columns = set(range(entry_x_range[0], entry_x_range[1] + 1))

        raw_columns = entry.get("columns")
        if raw_columns is not None:
            explicit_columns = {
                as_int(value, f"{entry_label}.columns[{idx}]")
                for idx, value in enumerate(normalize_int_list(raw_columns, f"{entry_label}.columns"))
            }
            allowed_columns &= explicit_columns

        raw_regions = entry.get("column_regions")
        if raw_regions is not None:
            region_names = normalize_string_list(raw_regions, f"{entry_label}.column_regions")
            region_columns = set()
            for region_name in region_names:
                region_range = column_region_ranges.get(region_name.lower())
                if region_range is None:
                    raise ValueError(f"{entry_label}.column_regions includes unknown region {region_name!r}")
                region_columns.update(range(region_range[0], region_range[1] + 1))
            allowed_columns &= region_columns

        return sorted(allowed_columns)

    def prepare_type_options(entry, entry_label):
        raw_type_options = entry.get("type_options")
        type_name = str(entry.get("type_name", "")).strip()
        if raw_type_options is not None:
            if type_name:
                raise ValueError(f"{entry_label} cannot define both type_name and type_options")
            if not isinstance(raw_type_options, list) or len(raw_type_options) == 0:
                raise ValueError(f"{entry_label}.type_options must be a non-empty array")
            options = []
            for opt_idx, option in enumerate(raw_type_options):
                if not isinstance(option, dict):
                    raise ValueError(f"{entry_label}.type_options[{opt_idx}] must be an object")
                option_name = str(option.get("type_name", "")).strip()
                if not option_name:
                    raise ValueError(f"{entry_label}.type_options[{opt_idx}].type_name is required")
                option_weight = as_number(
                    option.get("weight", 1),
                    f"{entry_label}.type_options[{opt_idx}].weight",
                )
                if option_weight < 0:
                    raise ValueError(f"{entry_label}.type_options[{opt_idx}].weight cannot be negative")
                options.append({"type_name": option_name, "weight": option_weight})
            return options

        if not type_name:
            raise ValueError(f"{entry_label}.type_name is required")
        return [{"type_name": type_name, "weight": 1.0}]

    def make_candidate_cell(x, y, type_name=None):
        cell = {"x": x, "y": y}
        if type_name is not None:
            normalized_type_name = str(type_name).strip()
            if not normalized_type_name:
                raise ValueError("candidate cell type_name must be a non-empty string")
            cell["type_name"] = normalized_type_name
        return cell

    def build_candidates(entry, entry_label):
        placement_mode = str(entry.get("placement_mode", "random_cells")).strip().lower()
        candidate_rows = resolve_candidate_rows(entry, entry_label)
        candidate_columns = resolve_candidate_columns(entry, entry_label)
        if len(candidate_rows) == 0 or len(candidate_columns) == 0:
            raise ValueError(f"{entry_label} produced no candidate rows/columns")

        raw_row_type_names = entry.get("row_type_names")
        row_type_names = {}
        if raw_row_type_names is not None:
            if placement_mode != "pattern_columns":
                raise ValueError(f"{entry_label}.row_type_names is only supported with placement_mode=pattern_columns")
            if not isinstance(raw_row_type_names, dict) or len(raw_row_type_names) == 0:
                raise ValueError(f"{entry_label}.row_type_names must be a non-empty object")
            for raw_row, raw_type_name in raw_row_type_names.items():
                row_value = as_int(raw_row, f"{entry_label}.row_type_names[{raw_row!r}]")
                if row_value not in expected_pattern_rows:
                    raise ValueError(
                        f"{entry_label}.row_type_names[{raw_row!r}] row must be within initial_grid_items.y_range"
                    )
                type_name = str(raw_type_name).strip()
                if not type_name:
                    raise ValueError(f"{entry_label}.row_type_names[{raw_row!r}] must be a non-empty string")
                row_type_names[row_value] = type_name

        if placement_mode == "pattern_columns":
            patterns = entry.get("patterns")
            if not isinstance(patterns, list) or len(patterns) == 0:
                raise ValueError(f"{entry_label}.patterns must be a non-empty array")
            if entry.get("positions") is not None:
                raise ValueError(f"{entry_label}.positions is not supported with placement_mode=pattern_columns")

            candidates = []
            for column in candidate_columns:
                for pattern_idx, pattern in enumerate(patterns):
                    if not isinstance(pattern, str) or not pattern:
                        raise ValueError(f"{entry_label}.patterns[{pattern_idx}] must be a non-empty string")
                    if len(pattern) != len(expected_pattern_rows):
                        raise ValueError(
                            f"{entry_label}.patterns[{pattern_idx}] must be {len(expected_pattern_rows)} characters long"
                        )

                    cells = []
                    for row_offset, flag in enumerate(pattern):
                        if flag not in {"0", "1"}:
                            raise ValueError(
                                f"{entry_label}.patterns[{pattern_idx}] must contain only '0' and '1'"
                            )
                        if flag == "1":
                            row_value = expected_pattern_rows[row_offset]
                            if row_value in candidate_rows:
                                cells.append(
                                    make_candidate_cell(
                                        column,
                                        row_value,
                                        row_type_names.get(row_value),
                                    )
                                )
                    if cells:
                        candidates.append({"cells": cells, "column": column})
            if len(candidates) == 0:
                raise ValueError(f"{entry_label} produced no pattern placement candidates")
            return placement_mode, candidates

        raw_positions = entry.get("positions")
        candidates = []
        if raw_positions is not None:
            if not isinstance(raw_positions, list) or len(raw_positions) == 0:
                raise ValueError(f"{entry_label}.positions must be a non-empty array")
            for p_idx, raw in enumerate(raw_positions):
                x, y = normalize_grid_position(raw, f"{entry_label}.positions[{p_idx}]")
                if x in candidate_columns and y in candidate_rows:
                    candidates.append({"cells": [make_candidate_cell(x, y)], "column": x})
        else:
            for x in candidate_columns:
                for y in candidate_rows:
                    candidates.append({"cells": [make_candidate_cell(x, y)], "column": x})
        if len(candidates) == 0:
            raise ValueError(f"{entry_label} produced no candidate cells")
        return placement_mode, candidates

    def pick_weighted_entry(entries):
        total_weight = sum(e["weight"] for e in entries)
        if total_weight <= 0:
            return random.choice(entries)
        roll = random.uniform(0.0, total_weight)
        running = 0.0
        for entry in entries:
            running += entry["weight"]
            if roll <= running:
                return entry
        return entries[-1]

    def prepare_slider_type_options(entry, entry_label):
        if entry.get("type_name") or entry.get("type_options") is not None:
            raise ValueError(
                f"{entry_label} should use up_type_name/down_type_name instead of type_name/type_options "
                "when placement_mode=slider_cells"
            )

        up_type_name = str(entry.get("up_type_name", "")).strip()
        down_type_name = str(entry.get("down_type_name", "")).strip()
        if not up_type_name:
            raise ValueError(f"{entry_label}.up_type_name is required for placement_mode=slider_cells")
        if not down_type_name:
            raise ValueError(f"{entry_label}.down_type_name is required for placement_mode=slider_cells")

        up_weight = as_number(entry.get("up_weight", 1), f"{entry_label}.up_weight")
        down_weight = as_number(entry.get("down_weight", 1), f"{entry_label}.down_weight")
        if up_weight < 0:
            raise ValueError(f"{entry_label}.up_weight cannot be negative")
        if down_weight < 0:
            raise ValueError(f"{entry_label}.down_weight cannot be negative")

        return [
            {"type_name": up_type_name, "weight": up_weight, "direction": "up"},
            {"type_name": down_type_name, "weight": down_weight, "direction": "down"},
        ]

    def get_slider_direction(type_name, slider_type_options):
        for option in slider_type_options:
            if option["type_name"] == type_name:
                return option["direction"]
        return None

    def is_slider_row_valid(direction, row_value):
        if direction == "up":
            return row_value > global_y_range[0]
        if direction == "down":
            return row_value < global_y_range[1]
        return False

    def extract_slider_states(raw_placements, slider_type_options):
        slider_states = []
        for placement in raw_placements:
            if not isinstance(placement, dict):
                continue
            type_name = str(placement.get("TypeName", "")).strip()
            direction = get_slider_direction(type_name, slider_type_options)
            if direction is None:
                continue
            slider_states.append(
                {
                    "x": as_int(placement.get("GridX"), "InitialGridItemPlacements[].GridX"),
                    "y": as_int(placement.get("GridY"), "InitialGridItemPlacements[].GridY"),
                    "type_name": type_name,
                    "direction": direction,
                }
            )
        return slider_states

    def validate_slider_states(slider_states):
        sliders_by_row = {}
        for slider_state in slider_states:
            if not is_slider_row_valid(slider_state["direction"], slider_state["y"]):
                return False
            sliders_by_row.setdefault(slider_state["y"], []).append(slider_state)

        for row_value, row_sliders in sliders_by_row.items():
            ordered_row_sliders = sorted(row_sliders, key=lambda state: state["x"], reverse=True)
            for right_slider, left_slider in zip(ordered_row_sliders, ordered_row_sliders[1:]):
                enabled = False
                for candidate_slider in slider_states:
                    if not (left_slider["x"] < candidate_slider["x"] < right_slider["x"]):
                        continue
                    if candidate_slider["direction"] == "up" and candidate_slider["y"] == row_value + 1:
                        enabled = True
                        break
                    if candidate_slider["direction"] == "down" and candidate_slider["y"] == row_value - 1:
                        enabled = True
                        break
                if not enabled:
                    return False

        return True

    def place_slider_cells(entry, entry_label, count, candidates):
        if bool(entry.get("allow_overlap", allow_overlap)):
            raise ValueError(f"{entry_label}.allow_overlap is not supported with placement_mode=slider_cells")

        slider_type_options = prepare_slider_type_options(entry, entry_label)
        max_attempts = as_int(entry.get("max_attempts", 1000), f"{entry_label}.max_attempts")
        if max_attempts <= 0:
            raise ValueError(f"{entry_label}.max_attempts must be > 0")

        base_candidates = []
        for candidate in candidates:
            if len(candidate["cells"]) != 1:
                raise ValueError(f"{entry_label} placement_mode=slider_cells only supports single-cell candidates")
            cell = candidate["cells"][0]
            if (cell["x"], cell["y"]) in occupied:
                continue
            base_candidates.append(candidate)

        if count > len(base_candidates):
            raise ValueError(
                f"{entry_label} cannot place {count} slider(s) in the available cells without overlap"
            )

        existing_slider_states = extract_slider_states(placements, slider_type_options)

        for _ in range(max_attempts):
            trial_slider_states = []
            selected_candidates = random.sample(base_candidates, count)
            for candidate in selected_candidates:
                cell = candidate["cells"][0]
                valid_type_options = [
                    option
                    for option in slider_type_options
                    if is_slider_row_valid(option["direction"], cell["y"])
                ]
                if len(valid_type_options) == 0:
                    trial_slider_states = []
                    break
                chosen_type = pick_weighted_entry(valid_type_options)
                trial_slider_states.append(
                    {
                        "x": cell["x"],
                        "y": cell["y"],
                        "type_name": chosen_type["type_name"],
                        "direction": chosen_type["direction"],
                    }
                )

            if len(trial_slider_states) != count:
                continue

            if not validate_slider_states(existing_slider_states + trial_slider_states):
                continue

            for slider_state in trial_slider_states:
                placements.append(
                    {
                        "GridX": slider_state["x"],
                        "GridY": slider_state["y"],
                        "TypeName": slider_state["type_name"],
                    }
                )
                occupied.add((slider_state["x"], slider_state["y"]))
            return

        raise ValueError(
            f"{entry_label} could not generate a valid slider layout after {max_attempts} attempt(s)"
        )

    if isinstance(pool_entries, list) and len(pool_entries) > 0:
        total_count_range = parse_int_range(
            initial_cfg.get("total_count_range", [1, 1]),
            "initial_grid_items.total_count_range",
        )
        target_total = normalize_total_count(random.randint(*total_count_range), total_count_range)

        prepared_entries = []
        min_total = 0
        for idx, entry in enumerate(pool_entries):
            if not isinstance(entry, dict):
                raise ValueError("initial_grid_items.pool entries must be objects")
            entry_label = f"initial_grid_items.pool[{idx}]"

            if "count_range" in entry:
                count_range = parse_int_range(entry.get("count_range"), f"{entry_label}.count_range")
                min_count = count_range[0]
                max_count = count_range[1]
            else:
                min_count = as_int(entry.get("min_count", 0), f"{entry_label}.min_count")
                max_count = as_int(
                    entry.get("max_count", total_count_range[1]),
                    f"{entry_label}.max_count",
                )
            if min_count < 0:
                raise ValueError(f"{entry_label}.min_count cannot be negative")
            if max_count < min_count:
                raise ValueError(f"{entry_label}.max_count cannot be less than min_count")

            weight = as_number(entry.get("weight", 1), f"{entry_label}.weight")
            if weight < 0:
                raise ValueError(f"{entry_label}.weight cannot be negative")

            entry_overlap = bool(entry.get("allow_overlap", allow_overlap))
            placement_mode, candidates = build_candidates(entry, entry_label)
            type_options = prepare_type_options(entry, entry_label)
            unique_pattern_columns = bool(entry.get("unique_pattern_columns", True))

            prepared_entries.append(
                {
                    "type_options": type_options,
                    "min_count": min_count,
                    "max_count": max_count,
                    "weight": weight,
                    "allow_overlap": entry_overlap,
                    "placement_mode": placement_mode,
                    "unique_pattern_columns": unique_pattern_columns,
                    "used_columns": set(),
                    "candidates": candidates,
                    "placed_count": 0,
                }
            )
            min_total += min_count

        if target_total < min_total:
            raise ValueError(
                "initial_grid_items.total_count_range minimum cannot be lower than sum of pool min_count values"
            )

        def place_one(entry):
            def is_available(candidate):
                if (
                    entry["placement_mode"] == "pattern_columns"
                    and entry["unique_pattern_columns"]
                    and candidate["column"] in entry["used_columns"]
                ):
                    return False
                if entry["allow_overlap"]:
                    return True
                return all((cell["x"], cell["y"]) not in occupied for cell in candidate["cells"])

            available = [candidate for candidate in entry["candidates"] if is_available(candidate)]
            if len(available) == 0:
                return False

            candidate = random.choice(available)
            type_name = pick_weighted_entry(entry["type_options"])["type_name"]
            for cell in candidate["cells"]:
                placements.append(
                    {
                        "GridX": cell["x"],
                        "GridY": cell["y"],
                        "TypeName": cell.get("type_name", type_name),
                    }
                )
                if not entry["allow_overlap"]:
                    occupied.add((cell["x"], cell["y"]))
            if entry["placement_mode"] == "pattern_columns" and entry["unique_pattern_columns"]:
                entry["used_columns"].add(candidate["column"])
            entry["placed_count"] += 1
            return True

        # Mandatory minimum placements per type.
        for idx, entry in enumerate(prepared_entries):
            for _ in range(entry["min_count"]):
                if not place_one(entry):
                    raise ValueError(
                        f"initial_grid_items.pool[{idx}] could not place required min_count without overlap"
                    )

        remaining = target_total - len(placements)

        while remaining > 0:
            eligible = [
                entry
                for entry in prepared_entries
                if entry["placed_count"] < entry["max_count"]
            ]
            if len(eligible) == 0:
                raise ValueError(
                    "initial_grid_items pool cannot satisfy total_count_range with the provided max_count values"
                )

            ordered = sorted(eligible, key=lambda e: e["weight"], reverse=True)
            placed = False
            for _ in range(len(ordered)):
                entry = pick_weighted_entry(ordered)
                if place_one(entry):
                    placed = True
                    break
                ordered = [e for e in ordered if e is not entry]
                if len(ordered) == 0:
                    break

            if not placed:
                raise ValueError(
                    "initial_grid_items pool could not place more items without overlap; reduce total_count_range or widen position ranges"
                )
            remaining -= 1

    else:
        type_entries = initial_cfg.get("types", [])
        if not isinstance(type_entries, list) or len(type_entries) == 0:
            raise ValueError(
                "Provide initial_grid_items.pool for random pool mode or initial_grid_items.types for fixed-per-type mode"
            )

        # Subset selection: each type entry may define an optional "weight" (default 1.0)
        # and "required" (default false). Required types are always included. Optional types
        # are each independently included with probability proportional to their weight
        # (weight >= 1 means ~always included, weight 0 means never, values in between are
        # fractional probabilities clamped to [0, 1]).  This produces varied combinations
        # per level rather than using every type every time.
        active_indices = set()
        for _pre_idx, _pre_entry in enumerate(type_entries):
            if not isinstance(_pre_entry, dict):
                continue  # will be caught properly in the main loop below
            if bool(_pre_entry.get("required", False)):
                active_indices.add(_pre_idx)
                continue
            _weight = _pre_entry.get("weight", 1.0)
            try:
                _weight = float(_weight)
            except (TypeError, ValueError):
                _weight = 1.0
            _prob = max(0.0, min(1.0, _weight))
            if random.random() < _prob:
                active_indices.add(_pre_idx)
        # Always keep at least one type active to avoid generating nothing.
        if not active_indices:
            active_indices.add(random.randrange(len(type_entries)))

        for idx, entry in enumerate(type_entries):
            if idx not in active_indices:
                continue
            if not isinstance(entry, dict):
                raise ValueError("initial_grid_items.types entries must be objects")

            count_range = parse_int_range(
                entry.get("count_range", [1, 1]),
                f"initial_grid_items.types[{idx}].count_range",
            )
            count = random.randint(*count_range)
            raw_disallowed = entry.get("disallowed_counts", [])
            if raw_disallowed:
                disallowed_counts = set(
                    as_int(v, f"initial_grid_items.types[{idx}].disallowed_counts[{i}]")
                    for i, v in enumerate(raw_disallowed)
                )
                if count in disallowed_counts:
                    allowed = [c for c in range(count_range[0], count_range[1] + 1) if c not in disallowed_counts]
                    if allowed:
                        count = min(allowed, key=lambda x: abs(x - count))
                    else:
                        count = 0
            if count <= 0:
                continue

            entry_overlap = bool(entry.get("allow_overlap", allow_overlap))
            entry_label = f"initial_grid_items.types[{idx}]"
            placement_mode, candidates = build_candidates(entry, entry_label)
            if placement_mode == "slider_cells":
                place_slider_cells(entry, entry_label, count, candidates)
                continue
            type_options = prepare_type_options(entry, entry_label)
            unique_pattern_columns = bool(entry.get("unique_pattern_columns", True))
            used_columns = set()

            def is_available(candidate):
                if (
                    placement_mode == "pattern_columns"
                    and unique_pattern_columns
                    and candidate["column"] in used_columns
                ):
                    return False
                if entry_overlap:
                    return True
                return all((cell["x"], cell["y"]) not in occupied for cell in candidate["cells"])

            for _ in range(count):
                available = [candidate for candidate in candidates if is_available(candidate)]
                if len(available) == 0:
                    raise ValueError(
                        f"{entry_label} cannot place {count} item(s) without overlap or column reuse limits"
                    )
                candidate = random.choice(available)
                type_name = pick_weighted_entry(type_options)["type_name"]
                for cell in candidate["cells"]:
                    placements.append(
                        {
                            "GridX": cell["x"],
                            "GridY": cell["y"],
                            "TypeName": cell.get("type_name", type_name),
                        }
                    )
                    if not entry_overlap:
                        occupied.add((cell["x"], cell["y"]))
                if placement_mode == "pattern_columns" and unique_pattern_columns:
                    used_columns.add(candidate["column"])

    return {
        "module_rtid": module_rtid,
        "object": {
            "aliases": [alias],
            "objclass": "InitialGridItemProperties",
            "objdata": {"InitialGridItemPlacements": placements},
        },
    }


def build_initial_zombie_object(
    initial_cfg,
    generation_context=None,
    all_zombie_aliases=None,
    zombie_costs=None,
    variant_alias_to_roll=None,
):
    if not isinstance(initial_cfg, dict):
        raise ValueError("initial_zombies must be an object")
    if not initial_cfg.get("enabled", False):
        return None

    if generation_context is None:
        generation_context = {}
    if all_zombie_aliases is None:
        all_zombie_aliases = set()
    if zombie_costs is None:
        zombie_costs = {}

    alias = str(initial_cfg.get("alias", "IZP"))
    blocked_cells = {
        (as_int(cell[0], "initial_zombies.blocked_cells.x"), as_int(cell[1], "initial_zombies.blocked_cells.y"))
        for cell in generation_context.get("blocked_cells", set())
    }

    if "min_x" in initial_cfg or "max_x" in initial_cfg:
        global_x_range = (
            as_int(initial_cfg.get("min_x", 0), "initial_zombies.min_x"),
            as_int(initial_cfg.get("max_x", 8), "initial_zombies.max_x"),
        )
        if global_x_range[0] > global_x_range[1]:
            raise ValueError("initial_zombies.min_x cannot be greater than initial_zombies.max_x")
    else:
        global_x_range = parse_int_range(
            initial_cfg.get("x_range", [0, 8]),
            "initial_zombies.x_range",
        )

    global_y_range = parse_int_range(
        initial_cfg.get("y_range", [0, 4]),
        "initial_zombies.y_range",
    )
    plank_rows = set(generation_context.get("plank_rows", []))

    column_region_ranges = {
        "back": (0, 4),
        "middle": (3, 5),
        "front": (5, 8),
    }
    raw_column_regions = initial_cfg.get("column_regions")
    if raw_column_regions is not None:
        if not isinstance(raw_column_regions, dict):
            raise ValueError("initial_zombies.column_regions must be an object")
        column_region_ranges = {}
        for region_name, raw_range in raw_column_regions.items():
            region_key = str(region_name).strip().lower()
            if not region_key:
                raise ValueError("initial_zombies.column_regions keys must be non-empty strings")
            column_region_ranges[region_key] = parse_int_range(
                raw_range,
                f"initial_zombies.column_regions[{region_name!r}]",
            )

    minimum_nonzero_total_count = initial_cfg.get("minimum_nonzero_total_count")
    if minimum_nonzero_total_count is not None:
        minimum_nonzero_total_count = as_int(
            minimum_nonzero_total_count,
            "initial_zombies.minimum_nonzero_total_count",
        )
        if minimum_nonzero_total_count < 0:
            raise ValueError("initial_zombies.minimum_nonzero_total_count cannot be negative")

    raw_disallowed_totals = initial_cfg.get("disallowed_total_counts", [])
    if not isinstance(raw_disallowed_totals, list):
        raise ValueError("initial_zombies.disallowed_total_counts must be an array")
    disallowed_total_counts = {
        as_int(value, f"initial_zombies.disallowed_total_counts[{idx}]")
        for idx, value in enumerate(raw_disallowed_totals)
    }

    def choose_total_count(count_range, max_allowed_total):
        valid_totals = []
        for total in range(count_range[0], count_range[1] + 1):
            if total in disallowed_total_counts:
                continue
            if minimum_nonzero_total_count is not None and 0 < total < minimum_nonzero_total_count:
                continue
            if total > max_allowed_total:
                continue
            valid_totals.append(total)

        if not valid_totals:
            raise ValueError("initial_zombies total_count rules leave no valid totals")

        target_total = random.randint(*count_range)
        if target_total in valid_totals:
            return target_total

        lower = [total for total in valid_totals if total <= target_total]
        if lower:
            return max(lower)

        higher = [total for total in valid_totals if total >= target_total]
        if higher:
            return higher[0]
        return valid_totals[0]

    def resolve_candidate_rows():
        allowed_rows = set(range(global_y_range[0], global_y_range[1] + 1))

        raw_allowed_rows = initial_cfg.get("allowed_rows")
        if raw_allowed_rows is not None:
            allowed_rows &= {
                as_int(value, f"initial_zombies.allowed_rows[{idx}]")
                for idx, value in enumerate(
                    normalize_int_list(raw_allowed_rows, "initial_zombies.allowed_rows")
                )
            }

        raw_forbidden_rows = initial_cfg.get("forbidden_rows", initial_cfg.get("disallowed_rows"))
        if raw_forbidden_rows is not None:
            forbidden_rows = {
                as_int(value, f"initial_zombies.forbidden_rows[{idx}]")
                for idx, value in enumerate(
                    normalize_int_list(raw_forbidden_rows, "initial_zombies.forbidden_rows")
                )
            }
            allowed_rows -= forbidden_rows

        if bool(initial_cfg.get("requires_planks", False)):
            allowed_rows &= plank_rows

        return sorted(allowed_rows)

    def resolve_candidate_columns():
        allowed_columns = set(range(global_x_range[0], global_x_range[1] + 1))

        raw_columns = initial_cfg.get("columns")
        if raw_columns is not None:
            explicit_columns = {
                as_int(value, f"initial_zombies.columns[{idx}]")
                for idx, value in enumerate(normalize_int_list(raw_columns, "initial_zombies.columns"))
            }
            allowed_columns &= explicit_columns

        raw_regions = initial_cfg.get("column_regions")
        if raw_regions is not None:
            region_names = normalize_string_list(raw_regions, "initial_zombies.column_regions")
            region_columns = set()
            for region_name in region_names:
                region_range = column_region_ranges.get(region_name.lower())
                if region_range is None:
                    raise ValueError(f"initial_zombies.column_regions includes unknown region {region_name!r}")
                region_columns.update(range(region_range[0], region_range[1] + 1))
            allowed_columns &= region_columns

        return sorted(allowed_columns)

    def build_candidate_cells():
        candidate_rows = resolve_candidate_rows()
        candidate_columns = resolve_candidate_columns()
        if len(candidate_rows) == 0 or len(candidate_columns) == 0:
            raise ValueError("initial_zombies produced no candidate rows/columns")

        raw_positions = initial_cfg.get("positions")
        cells = []
        if raw_positions is not None:
            if not isinstance(raw_positions, list) or len(raw_positions) == 0:
                raise ValueError("initial_zombies.positions must be a non-empty array")
            for idx, raw_position in enumerate(raw_positions):
                x, y = normalize_grid_position(raw_position, f"initial_zombies.positions[{idx}]")
                if x in candidate_columns and y in candidate_rows:
                    cells.append((x, y))
        else:
            for x in candidate_columns:
                for y in candidate_rows:
                    cells.append((x, y))

        filtered_cells = [cell for cell in cells if cell not in blocked_cells]
        if len(filtered_cells) == 0:
            raise ValueError("initial_zombies produced no available cells after blocking grid items")
        return filtered_cells

    def prepare_initial_zombie_pool(raw_pool):
        if raw_pool is None:
            raw_pool = generation_context.get("default_zombie_pool", [])
        if not isinstance(raw_pool, list) or len(raw_pool) == 0:
            raise ValueError("initial_zombies.pool must be a non-empty array")

        global_condition = str(initial_cfg.get("condition", initial_cfg.get("Condition", ""))).strip()
        prepared_pool = []
        for idx, raw_entry in enumerate(raw_pool):
            entry_label = f"initial_zombies.pool[{idx}]"
            if isinstance(raw_entry, str):
                alias_name = parse_zombie_alias(
                    raw_entry,
                    entry_label,
                    all_zombie_aliases,
                    variant_alias_to_roll=variant_alias_to_roll,
                )
                prepared_pool.append(
                    {"alias": alias_name, "weight": 1.0, "condition": global_condition}
                )
                continue
            if not isinstance(raw_entry, dict):
                raise ValueError(f"{entry_label} must be a string or object")

            raw_alias = raw_entry.get(
                "zombie_name",
                raw_entry.get("type_name", raw_entry.get("type", raw_entry.get("Type"))),
            )
            alias_name = parse_zombie_alias(
                raw_alias,
                f"{entry_label}.zombie_name",
                all_zombie_aliases,
                variant_alias_to_roll=variant_alias_to_roll,
            )
            weight = as_number(raw_entry.get("weight", 1), f"{entry_label}.weight")
            if weight < 0:
                raise ValueError(f"{entry_label}.weight cannot be negative")
            condition = str(
                raw_entry.get("condition", raw_entry.get("Condition", global_condition))
            ).strip()
            prepared_pool.append(
                {"alias": alias_name, "weight": weight, "condition": condition}
            )

        return prepared_pool

    raw_pool = initial_cfg.get("pool", initial_cfg.get("zombie_pool"))
    prepared_pool = prepare_initial_zombie_pool(raw_pool)
    if len(prepared_pool) == 0:
        return None

    missing_costs = sorted({entry["alias"] for entry in prepared_pool if entry["alias"] not in zombie_costs})
    if missing_costs:
        raise ValueError(
            "initial_zombies missing cost data for: " + ", ".join(missing_costs)
        )

    candidate_cells = build_candidate_cells()
    allow_duplicate_zombies = bool(initial_cfg.get("allow_duplicate_zombies", True))
    total_count_range = parse_int_range(
        initial_cfg.get("total_count_range", [1, 1]),
        "initial_zombies.total_count_range",
    )
    max_allowed_total = len(candidate_cells)
    if not allow_duplicate_zombies:
        max_allowed_total = min(max_allowed_total, len(prepared_pool))
    target_total = choose_total_count(total_count_range, max_allowed_total)
    if target_total <= 0:
        return None

    cost_x_power = as_number(initial_cfg.get("cost_x_power", 3.0), "initial_zombies.cost_x_power")
    if cost_x_power <= 0:
        raise ValueError("initial_zombies.cost_x_power must be > 0")
    min_position_weight = as_number(
        initial_cfg.get("min_position_weight", 0.15),
        "initial_zombies.min_position_weight",
    )
    if min_position_weight < 0 or min_position_weight > 1:
        raise ValueError("initial_zombies.min_position_weight must be between 0 and 1")

    pool_costs = [zombie_costs[entry["alias"]] for entry in prepared_pool]
    min_cost = min(pool_costs)
    max_cost = max(pool_costs)
    x_span = max(1, global_x_range[1] - global_x_range[0])

    def get_position_weight(cell_x, zombie_alias):
        if max_cost <= min_cost:
            return 1.0

        cost_ratio = (zombie_costs[zombie_alias] - min_cost) / (max_cost - min_cost)
        x_ratio = (cell_x - global_x_range[0]) / x_span
        closeness = max(0.0, 1.0 - abs(x_ratio - cost_ratio))
        return min_position_weight + ((closeness ** cost_x_power) * (1.0 - min_position_weight))

    occupied = set(blocked_cells)
    placements = []
    available_pool = prepared_pool[:]

    for placement_idx in range(target_total):
        available_cells = [cell for cell in candidate_cells if cell not in occupied]
        if len(available_cells) == 0:
            raise ValueError(
                "initial_zombies could not place all requested zombies without overlapping blocked cells"
            )

        weighted_choices = []
        for pool_idx, zombie_entry in enumerate(available_pool):
            for cell_idx, (cell_x, cell_y) in enumerate(available_cells):
                combined_weight = zombie_entry["weight"] * get_position_weight(cell_x, zombie_entry["alias"])
                weighted_choices.append(
                    {
                        "weight": combined_weight,
                        "pool_idx": pool_idx,
                        "cell_idx": cell_idx,
                    }
                )

        chosen = pick_weighted_entry(weighted_choices, f"initial_zombies placement {placement_idx + 1}")
        zombie_entry = available_pool[chosen["pool_idx"]]
        cell_x, cell_y = available_cells[chosen["cell_idx"]]
        placement = {
            "GridX": cell_x,
            "GridY": cell_y,
            "TypeName": zombie_entry["alias"],
        }
        if zombie_entry["condition"]:
            placement["Condition"] = zombie_entry["condition"]
        placements.append(placement)
        occupied.add((cell_x, cell_y))

        if not allow_duplicate_zombies:
            del available_pool[chosen["pool_idx"]]

    return {
        "object": {
            "aliases": [alias],
            "objclass": "InitialZombieProperties",
            "objdata": {"InitialZombiePlacements": placements},
        },
        "occupied_cells": {(placement["GridX"], placement["GridY"]) for placement in placements},
    }


def unique_zombie_pool(raw_pool, field_name="zombie_pool", variant_alias_to_roll=None):
    if not isinstance(raw_pool, list):
        raise ValueError(f"{field_name} must be an array of zombie aliases")

    unique_pool = []
    seen = set()
    for idx, zombie_alias in enumerate(raw_pool):
        if not isinstance(zombie_alias, str) or not zombie_alias.strip():
            raise ValueError(f"{field_name}[{idx}] must be a non-empty string")
        cleaned = canonicalize_zombie_alias(zombie_alias, variant_alias_to_roll)
        if cleaned in seen:
            continue
        unique_pool.append(cleaned)
        seen.add(cleaned)

    if not unique_pool:
        raise ValueError(f"{field_name} cannot be empty")

    return unique_pool


def build_level(template):
    seed_value = template.get("random_seed")
    if seed_value is not None:
        random.seed(seed_value)

    level_name = str(template.get("level_name", "DIE"))
    output_file = Path(str(template.get("output_file", "death.json")))
    json_indent = template.get("json_indent", 2)
    if isinstance(json_indent, bool):
        json_indent = 1 if json_indent else None
    elif json_indent is not None:
        json_indent = as_int(json_indent, "json_indent")

    sources = template.get("zombie_sources", {})
    if not isinstance(sources, dict):
        raise ValueError("zombie_sources must be an object")
    types_file = Path(str(sources.get("types_file", DEFAULT_TYPES_PATH)))
    props_file = Path(str(sources.get("props_file", DEFAULT_PROPS_PATH)))

    wave_cfg = template.get("wave_settings", {})
    if not isinstance(wave_cfg, dict):
        raise ValueError("wave_settings must be an object")
    level_definition_template = template.get("level_definition", {})
    if not isinstance(level_definition_template, dict):
        raise ValueError("level_definition must be an object")
    stage_module = str(level_definition_template.get("StageModule", "")).strip()

    flag_interval, flag_count, wave_count = resolve_wave_structure(wave_cfg)
    starting_points = as_number(
        wave_cfg.get("starting_points", 1),
        "wave_settings.starting_points",
    )
    point_increment = as_number(
        wave_cfg.get("point_increment", 1),
        "wave_settings.point_increment",
    )
    flag_bonus = as_number(wave_cfg.get("flag_bonus", 4), "wave_settings.flag_bonus")
    greediness_range = wave_cfg.get("greediness_range")
    if greediness_range is not None:
        greediness_range = parse_float_range(
            greediness_range,
            "wave_settings.greediness_range",
        )
        greediness_range = [max(0.0, min(1.0, greediness_range[0])), max(0.0, min(1.0, greediness_range[1]))]
    else:
        greediness = as_number(wave_cfg.get("greediness", 0.5), "wave_settings.greediness")
        greediness = max(0.0, min(1.0, greediness))
    planks = bool(wave_cfg.get("planks", False))
    plankrows =[
                    0,
                    1,
                    2,
                    3,
                    4
                ]
    for i in range(3):
        try:
            plankrows.remove(random.randint(0,4))
        except:
            continue
    
    starting_sun = as_int(wave_cfg.get("starting_sun", 50), "wave_settings.starting_sun")
    spawn_row_range = parse_int_range(
        wave_cfg.get("spawn_row_range", [1, 5]),
        "wave_settings.spawn_row_range",
    )
    force_spawn_each = bool(wave_cfg.get("force_spawn_each_zombie_once", True))
    events_cfg = template.get("events", {})
    if not isinstance(events_cfg, dict):
        raise ValueError("events must be an object")

    tide_changes = {}
    for tide_cfg in events_cfg.get("tide_changes", []):
        if "wave" in tide_cfg:
            wave = as_int(tide_cfg.get("wave"), "tide_changes[].wave")
            new_location = as_int(tide_cfg.get("new_wave_location"), "tide_changes[].new_wave_location")
            tide_changes[wave] = new_location
    initial_tide_cfg = template.get("initial_tide", {})
    if "starting_wave_location_range" in initial_tide_cfg:
        low, high = parse_int_range(initial_tide_cfg["starting_wave_location_range"], "initial_tide.starting_wave_location_range")
        current_tide = random.randint(low, high)
        initial_tide_cfg["starting_wave_location"] = current_tide  # update for build_initial_tide_object
    else:
        current_tide = as_int(initial_tide_cfg.get("starting_wave_location", 4), "initial_tide.starting_wave_location")

    types_data = load_json_file(types_file, "Zombie types")
    props_data = load_json_file(props_file, "Zombie properties")
    types_objects = types_data.get("objects", [])
    props_objects = props_data.get("objects", [])
    if not isinstance(types_objects, list):
        raise ValueError(f"{types_file} must contain an 'objects' array")
    if not isinstance(props_objects, list):
        raise ValueError(f"{props_file} must contain an 'objects' array")
    all_zombie_aliases = get_zombie_type_aliases(types_objects)
    zombie_type_metadata = build_zombie_type_metadata(types_objects)

    zombie_variant_groups, variant_alias_to_roll = build_zombie_variant_groups(
        template.get("zombie_variant_groups"),
        all_zombie_aliases,
    )
    selected_pool = unique_zombie_pool(
        template.get("zombie_pool", []),
        variant_alias_to_roll=variant_alias_to_roll,
    )
    exclude_from_waves = set(
        canonicalize_zombie_alias(z, variant_alias_to_roll)
        for z in template.get("exclude_from_waves", [])
    )
    selected_pool = [z for z in selected_pool if z not in exclude_from_waves]
    selected_pool = apply_zombie_pool_dependencies(
        selected_pool,
        template.get("zombie_pool_dependencies"),
        variant_alias_to_roll=variant_alias_to_roll,
    )
    zombie_pool_basics_raw = template.get("zombie_pool_basics", [])
    zombie_pool_non_basics_raw = template.get("zombie_pool_non_basics", [])
    non_basics_per_flag = as_int(template.get("non_basics_per_flag", 0), "non_basics_per_flag")
    if non_basics_per_flag < 0:
        raise ValueError("non_basics_per_flag cannot be negative")
    non_basics_pool_mode = str(template.get("non_basics_pool_mode", "accumulate")).strip().lower() or "accumulate"
    if non_basics_pool_mode not in {"accumulate", "refresh_per_flag"}:
        raise ValueError("non_basics_pool_mode must be 'accumulate' or 'refresh_per_flag'")
    non_basics_retained_per_flag = as_int(
        template.get("non_basics_retained_per_flag", 0),
        "non_basics_retained_per_flag",
    )
    if non_basics_retained_per_flag < 0:
        raise ValueError("non_basics_retained_per_flag cannot be negative")
    if zombie_pool_basics_raw and zombie_pool_non_basics_raw:
        basics_set = set(canonicalize_zombie_alias(z, variant_alias_to_roll) for z in zombie_pool_basics_raw)
        non_basics_set = set(canonicalize_zombie_alias(z, variant_alias_to_roll) for z in zombie_pool_non_basics_raw)
        # Ensure non_basics are in selected_pool
        for zombie in non_basics_set:
            if zombie not in selected_pool:
                selected_pool.append(zombie)
    else:
        basics_set = set(selected_pool)
        non_basics_set = set()
    expanded_selected_pool = expand_zombie_roll_pool(selected_pool, zombie_variant_groups)

    weight_aliases = set(expanded_selected_pool)
    event_aliases = collect_event_zombie_aliases(events_cfg)
    initial_zombie_aliases = collect_initial_zombie_aliases(
        template.get("initial_zombies"),
        variant_alias_to_roll=variant_alias_to_roll,
    )
    weight_aliases.update(event_aliases)
    weight_aliases.update(initial_zombie_aliases)
    weight_aliases.update(exclude_from_waves)
    weight_aliases.update(
        canonicalize_zombie_alias(alias, variant_alias_to_roll)
        for alias in event_aliases
    )
    all_zombie_costs = resolve_zombie_weights(
        sorted(weight_aliases),
        types_objects,
        props_objects,
    )
    jam_style_overrides = dict(DEFAULT_JAM_STYLE_OVERRIDES)
    raw_jam_overrides = template.get("jam_style_overrides", {})
    if raw_jam_overrides is not None:
        if not isinstance(raw_jam_overrides, dict):
            raise ValueError("jam_style_overrides must be an object")
        for zombie_name, jam_style in raw_jam_overrides.items():
            if not isinstance(zombie_name, str) or not isinstance(jam_style, str):
                raise ValueError("jam_style_overrides must map zombie aliases to jam names")
            normalized_name = canonicalize_zombie_alias(zombie_name, variant_alias_to_roll)
            jam_style_overrides[normalized_name] = jam_style.strip()
    zombie_jam_styles = resolve_zombie_jam_styles(
        selected_pool,
        types_objects,
        props_objects,
        overrides=jam_style_overrides,
    )
    zombie_costs = {name: all_zombie_costs[name] for name in selected_pool}
    zombie_rtid = {name: f"RTID({name}@ZombieTypes)" for name in selected_pool}

    pool_sorted = sorted(selected_pool, key=zombie_costs.__getitem__)
    spendable_pool = [name for name in pool_sorted if zombie_costs[name] > 0]
    if not spendable_pool:
        raise ValueError("All zombie weights are <= 0. Cannot generate waves.")
    wave_companion_rules = prepare_wave_companion_rules(
        template.get("zombie_wave_rules"),
        zombie_costs,
        variant_alias_to_roll=variant_alias_to_roll,
    )

    required_zombies = selected_pool[:] if force_spawn_each else []
    random.shuffle(required_zombies)

    pf_waves = build_plantfood_waves(wave_cfg, wave_count, flag_interval)
    jam_state = build_jam_state(
        template.get("jams"),
        wave_count,
        stage_module,
        zombie_jam_styles,
    )
    available_pool = basics_set.copy()
    introduced_non_basics = set()
    active_non_basics = set()
    pending_wave_companions = {}
    aliases_cfg = template.get("aliases", {})
    if not isinstance(aliases_cfg, dict):
        raise ValueError("aliases must be an object")
    seed_bank_alias = str(aliases_cfg.get("seed_bank", "SeedBank"))
    escalation_alias = str(aliases_cfg.get("escalation", "Escalation"))
    wave_manager_module_alias = str(aliases_cfg.get("wave_manager_module", "NewWaves"))
    wave_manager_alias = str(aliases_cfg.get("wave_manager", "WaveManager"))
    wave_alias_prefix = str(aliases_cfg.get("wave_prefix", "Wave"))
    rails_alias = str(aliases_cfg.get("rails", "Rails"))

    wave_objects = []
    wave_refs = []
    wave_zombies_by_wave = []
    jam_event_objects = []
    zombies_used = set()
    wave_points = []
    existing_aliases = {seed_bank_alias, escalation_alias, wave_manager_module_alias, wave_manager_alias, rails_alias}
    generated_portal_objects, generated_portal_pool, portal_costs = build_generated_portal_objects(
        events_cfg.get("generated_portals"),
        selected_pool,
        all_zombie_aliases,
        all_zombie_costs,
        zombie_type_metadata,
        existing_aliases,
        variant_alias_to_roll=variant_alias_to_roll,
    )
    generation_context = {
        "generated_grid_pools": {
            "generated_portals": generated_portal_pool,
        },
        "portal_costs": portal_costs,
    }

    for wave in range(1, wave_count + 1):
        is_flag_wave = wave % flag_interval == 0
        active_jam = jam_state["active_by_wave"].get(wave)
        points = starting_points + (wave - 1) * point_increment
        if is_flag_wave:
            points += flag_bonus
        wave_points.append(points)

        if greediness_range is not None:
            greediness = random.uniform(greediness_range[0], greediness_range[1])
            greediness = max(0.0, min(1.0, greediness))

        remaining = points
        zombies_list = []
        wave_present = set()
        wave_counts = {}

        # Zombie introduction logic
        if is_flag_wave and non_basics_set:
            if non_basics_pool_mode == "refresh_per_flag":
                active_non_basics = refresh_non_basic_pool(
                    active_non_basics,
                    non_basics_set,
                    non_basics_per_flag,
                    non_basics_retained_per_flag,
                )
                available_pool = basics_set | active_non_basics
            else:
                candidates = list(non_basics_set - introduced_non_basics)
                if candidates:
                    num_to_add = min(non_basics_per_flag, len(candidates))
                    to_add = random.sample(candidates, num_to_add)
                    available_pool.update(to_add)
                    introduced_non_basics.update(to_add)
                active_non_basics = available_pool - basics_set

        current_spendable_pool = [name for name in available_pool if zombie_costs[name] > 0]

        for scheduled in pending_wave_companions.pop(wave, []):
            remaining, _ = add_requires_any_companions(
                scheduled["requires_any"],
                scheduled["count_range"],
                remaining,
                zombies_list,
                wave_present,
                wave_counts,
                zombie_rtid,
                spawn_row_range,
                planks,
                zombie_costs,
                allow_flag_zombies=is_flag_wave,
                allow_duplicates=scheduled["allow_duplicates"],
                zombies_used=zombies_used,
                zombie_variant_groups=zombie_variant_groups,
            )

        def can_pick_for_wave(zombie_name):
            return can_spawn_zombie_in_wave(
                zombie_name,
                remaining,
                wave_present,
                wave_counts,
                zombie_costs,
                wave_companion_rules,
                zombie_jam_styles=zombie_jam_styles,
                allow_flag_zombies=is_flag_wave,
                active_jam=active_jam,
            )

        required = pop_required_zombie(
            required_zombies,
            zombie_costs,
            remaining,
            validator=can_pick_for_wave,
        )
        if required is not None:
            remaining -= zombie_costs[required]
            append_wave_zombie(
                zombies_list,
                wave_present,
                wave_counts,
                required,
                zombie_rtid,
                spawn_row_range,
                planks,
                zombies_used=zombies_used,
                zombie_variant_groups=zombie_variant_groups,
            )
            remaining = add_required_wave_companions(
                required,
                remaining,
                zombies_list,
                wave_present,
                wave_counts,
                zombie_rtid,
                spawn_row_range,
                planks,
                zombie_costs,
                wave_companion_rules,
                allow_flag_zombies=is_flag_wave,
                zombies_used=zombies_used,
                zombie_variant_groups=zombie_variant_groups,
            )
            schedule_followup_wave_companions(
                pending_wave_companions,
                required,
                wave_companion_rules,
                wave,
                wave_count,
            )

        while remaining > 0:
            valid_candidates = [
                zombie_name
                for zombie_name in current_spendable_pool
                if can_spawn_zombie_in_wave(
                    zombie_name,
                    remaining,
                    wave_present,
                    wave_counts,
                    zombie_costs,
                    wave_companion_rules,
                    zombie_jam_styles=zombie_jam_styles,
                    allow_flag_zombies=is_flag_wave,
                    active_jam=active_jam,
                )
            ]
            if not valid_candidates:
                break
            valid_candidates = apply_jam_candidate_bias(
                valid_candidates,
                active_jam,
                jam_state,
                zombie_jam_styles,
            )
            if not valid_candidates:
                break

            zombie_name = pick_greedy_zombie(valid_candidates, zombie_costs, greediness)
            remaining -= zombie_costs[zombie_name]
            append_wave_zombie(
                zombies_list,
                wave_present,
                wave_counts,
                zombie_name,
                zombie_rtid,
                spawn_row_range,
                planks,
                zombies_used=zombies_used,
                zombie_variant_groups=zombie_variant_groups,
            )
            remaining = add_required_wave_companions(
                zombie_name,
                remaining,
                zombies_list,
                wave_present,
                wave_counts,
                zombie_rtid,
                spawn_row_range,
                planks,
                zombie_costs,
                wave_companion_rules,
                allow_flag_zombies=is_flag_wave,
                zombies_used=zombies_used,
                zombie_variant_groups=zombie_variant_groups,
            )
            schedule_followup_wave_companions(
                pending_wave_companions,
                zombie_name,
                wave_companion_rules,
                wave,
                wave_count,
            )

        apply_wave_layout_rules(zombies_list, spawn_row_range, active_jam)
        wave_zombies_by_wave.append(zombies_list)
        wave_alias = f"{wave_alias_prefix}{wave}"
        wave_objects.append(
            {
                "aliases": [wave_alias],
                "objclass": "SpawnZombiesJitteredWaveActionProps",
                "objdata": {
                    "AdditionalPlantfood": 1 if wave in pf_waves else 0,
                    "Zombies": zombies_list,
                },
            }
        )
        wave_refs.append([f"RTID({wave_alias}@.)"])
        existing_aliases.add(wave_alias)
        if wave in jam_state["segment_starts"]:
            jam_obj, jam_ref = build_jam_notification_event(
                wave,
                jam_state["segment_starts"][wave],
                template.get("jams", {}),
                existing_aliases,
            )
            jam_event_objects.append(jam_obj)
            wave_refs[-1].insert(0, jam_ref)

    ambush_chance = as_number(events_cfg.get("ambush_chance", 0), "events.ambush_chance")
    max_per_wave = as_int(events_cfg.get("max_per_wave", 0), "events.max_per_wave")
    max_per_wave = max(0, max_per_wave)

    grid_event_objects = []
    sun_crash_state = {"triggered": False}
    last_tide_end = 4

    for wave in range(1, wave_count + 1):
        is_flag_wave = wave % flag_interval == 0
        ambush_points_remaining = max(0.0, wave_points[wave - 1])
        ambush_count = 0
        current_wave_zombies = wave_zombies_by_wave[wave - 1]

        while ambush_count < max_per_wave and random.random() < ambush_chance:
            ambush_count += 1
            available = get_enabled_ambushes(events_cfg, zombies_used, current_wave_zombies)
            if not available:
                break

            chosen_event = pick_weighted_dict(available, "enabled ambushes")
            event_kind = chosen_event["kind"]
            event_cfg = chosen_event["config"]

            if event_kind == "market":
                event_obj, event_ref = build_market_event(wave, ambush_count, event_cfg)
                grid_event_objects.append(event_obj)
                wave_refs[wave - 1].append(event_ref)
                for alias in event_obj.get("aliases", []):
                    if isinstance(alias, str):
                        existing_aliases.add(alias)
            elif event_kind == "raidpty":
                event_objs, refs, ambush_points_remaining = build_raidpty_events(
                    wave, ambush_count, event_cfg, ambush_points_remaining,
                )
                grid_event_objects.extend(event_objs)
                wave_refs[wave - 1].extend(refs)
                for event_obj in event_objs:
                    for alias in event_obj.get("aliases", []):
                        if isinstance(alias, str):
                            existing_aliases.add(alias)
            elif event_kind == "Parrotrousle":
                event_objs, refs, ambush_points_remaining = build_Parrotrousle_events(
                    wave, ambush_count, event_cfg, ambush_points_remaining,
                )
                grid_event_objects.extend(event_objs)
                wave_refs[wave - 1].extend(refs)
                for event_obj in event_objs:
                    for alias in event_obj.get("aliases", []):
                        if isinstance(alias, str):
                            existing_aliases.add(alias)
            elif event_kind == "parachute_rain":
                event_obj, ambush_points_remaining = build_parachute_rain_event(
                    wave,
                    ambush_count,
                    event_cfg,
                    ambush_points_remaining,
                    all_zombie_costs,
                    all_zombie_aliases,
                    existing_aliases,
                    allow_flag_zombies=is_flag_wave,
                    zombie_variant_groups=zombie_variant_groups,
                    variant_alias_to_roll=variant_alias_to_roll,
                )
                if event_obj is not None:
                    grid_event_objects.append(event_obj)
                    wave_refs[wave - 1].append(f"RTID({event_obj['aliases'][0]}@.)")
            elif event_kind == "sun_crash":
                event_objs, refs = build_sun_crash_events(
                    wave, ambush_count, event_cfg, sun_crash_state
                )
                grid_event_objects.extend(event_objs)
                wave_refs[wave - 1].extend(refs)
                for event_obj in event_objs:
                    for alias in event_obj.get("aliases", []):
                        if isinstance(alias, str):
                            existing_aliases.add(alias)
            elif event_kind == "imp_ambush":
                event_obj, ambush_points_remaining = build_imp_ambush_event(
                    wave,
                    event_cfg,
                    ambush_points_remaining,
                    allow_flag_zombies=is_flag_wave,
                    all_zombie_aliases=all_zombie_aliases,
                    zombie_variant_groups=zombie_variant_groups,
                    variant_alias_to_roll=variant_alias_to_roll,
                )
                if event_obj is not None:
                    grid_event_objects.append(event_obj)
                    wave_refs[wave - 1].append(f"RTID({event_obj['aliases'][0]}@.)")
                    for alias in event_obj.get("aliases", []):
                        if isinstance(alias, str):
                            existing_aliases.add(alias)
            elif event_kind == "storm_ambush":
                storm_objects, storm_refs, ambush_points_remaining = build_sandstorm_ambush_events(
                    wave,
                    event_cfg,
                    selected_pool,
                    all_zombie_aliases,
                    existing_aliases,
                    all_zombie_costs,
                    ambush_points_remaining,
                    allow_flag_zombies=is_flag_wave,
                    zombie_variant_groups=zombie_variant_groups,
                    variant_alias_to_roll=variant_alias_to_roll,
                )
                grid_event_objects.extend(storm_objects)
                wave_refs[wave - 1].extend(storm_refs)
            elif event_kind == "portal_spawn":
                event_obj, event_ref, points_cost = build_portal_spawn_event(wave, ambush_count, event_cfg, portal_costs, ambush_points_remaining)
                if event_obj is not None and event_ref is not None:
                    grid_event_objects.append(event_obj)
                    wave_refs[wave - 1].append(event_ref)
                    ambush_points_remaining -= points_cost
                    for alias in event_obj.get("aliases", []):
                        if isinstance(alias, str):
                            existing_aliases.add(alias)
            elif event_kind == "grid_spawn":
                event_obj, event_ref, ambush_points_remaining = build_grid_spawn_event(
                    wave,
                    ambush_count,
                    event_cfg,
                    existing_aliases,
                    ambush_points_remaining,
                    generation_context=generation_context,
                )
                if event_obj is not None and event_ref is not None:
                    grid_event_objects.append(event_obj)
                    wave_refs[wave - 1].append(event_ref)
            elif event_kind == "frost_wind":
                event_obj, event_ref, ambush_points_remaining = build_frost_wind_event(
                    wave,
                    ambush_count,
                    event_cfg,
                    existing_aliases,
                    ambush_points_remaining,
                )
                if event_obj is not None and event_ref is not None:
                    grid_event_objects.append(event_obj)
                    wave_refs[wave - 1].append(event_ref)
            elif event_kind == "low_tide":
                event_objs, refs, ambush_points_remaining, last_tide_end = build_low_tide_events(
                    wave,
                    ambush_count,
                    event_cfg,
                    ambush_points_remaining,
                    all_zombie_aliases,
                    all_zombie_costs,
                    existing_aliases,
                    allow_flag_zombies=is_flag_wave,
                    zombie_variant_groups=zombie_variant_groups,
                    variant_alias_to_roll=variant_alias_to_roll,
                    last_tide_end=last_tide_end,
                )
                grid_event_objects.extend(event_objs)
                wave_refs[wave - 1].extend(refs)
                # Add tide change with low tide
                tide_cfgs = events_cfg.get("tide_changes", [])
                if tide_cfgs:
                    tide_cfg = pick_weighted_dict(tide_cfgs, "tide_changes")
                    if tide_cfg:
                        # Make it more intense for low tide
                        tide_cfg = copy.deepcopy(tide_cfg)
                        if random.random() < 0.7:  # 70% chance for intense pullback
                            tide_cfg["dry_lane_count_range"] = [5, 7]
                            tide_cfg["event_name"] = "intense_pullback"
                        event_obj, event_ref = build_tide_change_event(wave, ambush_count, tide_cfg, existing_aliases)
                        if event_obj and event_ref:
                            grid_event_objects.append(event_obj)
                            wave_refs[wave - 1].append(event_ref)
                            for alias in event_obj.get("aliases", []):
                                if isinstance(alias, str):
                                    existing_aliases.add(alias)
                            ambush_count += 1
            elif event_kind == "necromancy_spawn":
                objects, refs, ambush_points_remaining = build_grid_item_spawner_event(
                    wave,
                    ambush_count,
                    event_cfg,
                    all_zombie_aliases,
                    existing_aliases,
                    ambush_points_remaining,
                    all_zombie_costs,
                    allow_flag_zombies=is_flag_wave,
                    zombie_variant_groups=zombie_variant_groups,
                    variant_alias_to_roll=variant_alias_to_roll,
                )
                if objects:
                    grid_event_objects.extend(objects)
                    wave_refs[wave - 1].extend(refs)
            elif event_kind == "dino_ambush":
                event_objs, refs, ambush_points_remaining = build_dino_events(
                    wave,
                    ambush_count,
                    event_cfg,
                    existing_aliases,
                    ambush_points_remaining,
                    current_wave_zombies,
                )
                grid_event_objects.extend(event_objs)
                wave_refs[wave - 1].extend(refs)
                # Row-pressure: for each dino spawned, bias zombies in the next 3 waves
                # into the same row.  Ptero only allows DINO_PTERO_SUPPORT_ZOMBIES; others
                # allow any zombie type.  A fraction cap prevents all zombies going to one row.
                for dino_obj in event_objs:
                    objdata = dino_obj.get("objdata", {})
                    dino_row = objdata.get("DinoRow")
                    dino_type = objdata.get("DinoType", "")
                    if dino_row is None:
                        continue
                    is_ptero = "ptero" in dino_type.lower()
                    for future_wave in range(wave + 1, min(wave + 4, wave_count + 1)):
                        apply_dino_row_pressure(
                            wave_zombies_by_wave[future_wave - 1],
                            dino_row,
                            is_ptero,
                            zombie_rtid,
                        )
            elif event_kind == "tide_change":
                event_obj, event_ref = build_tide_change_event(
                    wave,
                    ambush_count,
                    event_cfg,
                    existing_aliases,
                )
                if event_obj is not None and event_ref is not None:
                    grid_event_objects.append(event_obj)
                    wave_refs[wave - 1].append(event_ref)

    level_definition = copy.deepcopy(level_definition_template)
    level_definition["Name"] = level_name
    level_definition["StartingSun"] = starting_sun

    music_choice = random.choice(["MiniGame_A", "MiniGame_B", None])
    if music_choice is not None:
        level_definition["MusicType"] = music_choice

    initial_grid_item_entry = build_initial_grid_item_object(
        template.get("initial_grid_items", {}),
        {"plank_rows": plankrows if planks else []},
    )
    initial_grid_item_cells = set()
    if initial_grid_item_entry is not None:
        for placement in initial_grid_item_entry["object"]["objdata"].get("InitialGridItemPlacements", []):
            initial_grid_item_cells.add(
                (
                    as_int(placement.get("GridX"), "InitialGridItemPlacements[].GridX"),
                    as_int(placement.get("GridY"), "InitialGridItemPlacements[].GridY"),
                )
            )
    initial_zombie_entry = build_initial_zombie_object(
        template.get("initial_zombies", {}),
        {
            "blocked_cells": initial_grid_item_cells,
            "default_zombie_pool": selected_pool,
            "plank_rows": plankrows if planks else [],
        },
        all_zombie_aliases=all_zombie_aliases,
        zombie_costs=all_zombie_costs,
        variant_alias_to_roll=variant_alias_to_roll,
    )
    initial_tide_entry = build_initial_tide_object(template.get("initial_tide"))
    required_modules = []
    for module in normalize_module_list(
        template.get("required_modules"),
        "required_modules",
    ) + get_event_required_modules(events_cfg):
        if module not in required_modules:
            required_modules.append(module)
    if initial_grid_item_entry is not None:
        modules = level_definition.get("Modules")
        if not isinstance(modules, list):
            modules = []
            level_definition["Modules"] = modules
        module_rtid = initial_grid_item_entry.get("module_rtid", "")
        if module_rtid and module_rtid not in modules:
            modules.append(module_rtid)
    if initial_tide_entry is not None or required_modules:
        modules = level_definition.get("Modules")
        if not isinstance(modules, list):
            modules = []
            level_definition["Modules"] = modules
        if initial_tide_entry is not None:
            module_rtid = initial_tide_entry.get("module_rtid", "")
            if module_rtid and module_rtid not in modules:
                modules.append(module_rtid)
        for module_rtid in required_modules:
            if module_rtid not in modules:
                modules.append(module_rtid)

    seed_bank = copy.deepcopy(template.get("seed_bank", {}))

    if not isinstance(seed_bank, dict):
        raise ValueError("seed_bank must be an object")

    escalation = copy.deepcopy(template.get("escalation", {}))
    if not isinstance(escalation, dict):
        raise ValueError("escalation must be an object")
    escalation["FlagCount"] = flag_count
    escalation["WavesPerFlag"] = flag_interval
    escalation["WaveManagerProps"] = str(
        escalation.get("WaveManagerProps", f"RTID({wave_manager_alias}@CurrentLevel)")
    )
    escalation["ZombiePool"] = [zombie_rtid[name] for name in selected_pool]

    wave_manager_module = copy.deepcopy(template.get("wave_manager_module", {}))
    if not isinstance(wave_manager_module, dict):
        raise ValueError("wave_manager_module must be an object")

    wave_manager = copy.deepcopy(template.get("wave_manager", {}))
    if not isinstance(wave_manager, dict):
        raise ValueError("wave_manager must be an object")
    wave_manager["FlagWaveInterval"] = flag_interval
    wave_manager["WaveCount"] = wave_count
    wave_manager["Waves"] = wave_refs

    railcarts = {}

    if "railcarts" in template:

        railcarts = generate_random_railcarts()

    level_objects = [
        {
            "objclass": "LevelDefinition",
            "objdata": level_definition,
        },
        {
            "aliases": [seed_bank_alias],
            "objclass": "SeedBankProperties",
            "objdata": seed_bank,
        },
        {
            "aliases": [escalation_alias],
            "objclass": "LevelEscalationModuleProperties",
            "objdata": escalation,
        },
        {
            "aliases": [wave_manager_module_alias],
            "objclass": "WaveManagerModuleProperties",
            "objdata": wave_manager_module,
        },
        {
            "aliases": [wave_manager_alias],
            "objclass": "WaveManagerProperties",
            "objdata": wave_manager,
        },
    ] + generated_portal_objects + wave_objects + jam_event_objects + grid_event_objects
    if railcarts:
        level_objects.append({
            "aliases": [rails_alias],
            "objclass": "RailcartProperties",
            "objdata": railcarts,
        })
    if planks:
        plankscode={
            "aliases": [
                "PiratePlanks"
            ],
            "objclass": "PiratePlankProperties",
            "objdata": {
                "PlankRows": plankrows
            }
        }
        level_objects.append(plankscode)
    Parrotrousle_cfg = events_cfg.get("Parrotrousle", {})
    if Parrotrousle_cfg.get("enabled"):
        prsetup={"aliases":["PIPI"],
        "objclass":"InitialGridItemProperties",
        "objdata":{
            "InitialGridItemPlacements": [
                {"GridX": 5, "GridY": 15, "TypeName":"crater"}
            ]
        }}
        level_objects.append(prsetup)



    if initial_grid_item_entry is not None:
        level_objects.append(initial_grid_item_entry["object"])
    if initial_zombie_entry is not None:
        level_objects.append(initial_zombie_entry["object"])
    if initial_tide_entry is not None:
        level_objects.append(initial_tide_entry["object"])

    if bool(template.get("append_empty_object", False)):
        level_objects.append({})

    level = {
        "#comment": str(
            template.get("comment", f"{level_name} | ELM: Ver-13.1 [RFL v1.4]")
        ),
        "#zombies": ", ".join(sorted(selected_pool)),
        "objects": level_objects,
        "version": as_int(template.get("version", 1), "version"),
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    dump_kwargs = {}
    if json_indent is None:
        dump_kwargs["separators"] = (",", ":")
    else:
        dump_kwargs["indent"] = json_indent

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(level, file, **dump_kwargs)

    print(
        f"Generated {output_file} with {wave_count} waves, "
        f"{len(grid_event_objects)} event object(s), "
        f"{len(selected_pool)} zombie type(s)."
    )


def main():
    template_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TEMPLATE_PATH
    template = load_json_file(template_path, "Level template")
    if not isinstance(template, dict):
        raise ValueError("Template root must be a JSON object")
    build_level(template)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)