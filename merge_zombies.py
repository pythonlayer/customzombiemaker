import json
import random
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ZombieType:
    name: str
    weight: float
    cost: int
    tags: set[str] = field(default_factory=set)
    requires_any: set[str] = field(default_factory=set)


@dataclass
class LevelConfig:
    num_waves: int = 16
    base_wave_cost: int = 100
    wave_cost_growth: int = 100
    flag_interval: int = 4
    flag_bonus_cost: int = 400
    greediness: float = 0.5  # 0.0 low-cost heavy, 1.0 high-cost heavy
    plantfood_interval: int = 8
    rows: int = 5
    cols: int = 9
    stage: str = "modern"
    max_initial_graves: int = 8
    seed: int | None = None
    level_name: str = "My Level"
    stage_module: str = "RTID(ModernStage@LevelModules)"


GRAVE_TYPES = [
    "gravestone_tutorial",
    "gravestone_egypt",
    "gravestone_pirate",
    "gravestone_cowboy",
    "gravestone_future",
    "gravestone_dark",
    "gravestoneSunOnDestruction",
    "gravestonePlantfoodOnDestruction",
    "gravestone_iceage",
    "gravestone_lostcity",
]

NEAT_ITEM_ZONES = {
    "bufftile_speed": "middle_front",
    "bufftile_attack": "middle_front",
    "bufftile_shield": "middle_front",
    "powertile_alpha": "back_middle",
    "powertile_beta": "back_middle",
    "powertile_gamma": "back_middle",
    "presentSunOnDestruction": "middle_front",
    "goldtile": "all",
    "surfboard": "middle",
    "speaker": "middle_front",
    "carnie_card_unactivated": "middle_front",
    "slider_up": "all",
    "slider_up_modern": "all",
    "slider_down": "all",
    "slider_down_modern": "all",
}

PATTERNS = ["00100", "10101", "01010", "10001"]

GOOD_CARDS = [
    ("carnie_card_sunify", 1 / 6),
    ("carnie_card_basic", 1 / 6),
    ("carnie_card_freeze", 1 / 6),
]
BAD_CARDS = [
    ("carnie_card_god", 0.1),
    ("carnie_card_mirror", 0.1),
    ("carnie_card_armor4", 0.1),
    ("carnie_card_armor2", 0.1),
    ("carnie_card_flag", 0.1),
]

DEFAULT_TYPES_PATH = Path("ZOMBIETYPES_UPDATED.json")
DEFAULT_PROPERTIES_PATH = Path("ZOMBIEPROPERTIES_UPDATED.json")


def wave_cost_for_index(index_1_based: int, cfg: LevelConfig) -> int:
    cost = cfg.base_wave_cost + (index_1_based - 1) * cfg.wave_cost_growth
    if cfg.flag_interval > 0 and index_1_based % cfg.flag_interval == 0:
        cost += cfg.flag_bonus_cost
    return max(0, cost)


def pick_weighted(rng: random.Random, weighted_items: list[tuple[ZombieType, float]]) -> ZombieType:
    total = sum(max(0.0, w) for _, w in weighted_items)
    if total <= 0:
        return weighted_items[0][0]
    roll = rng.random() * total
    running = 0.0
    for item, w in weighted_items:
        running += max(0.0, w)
        if roll <= running:
            return item
    return weighted_items[-1][0]


def is_requirements_met(chosen_counts: dict[str, int], z: ZombieType) -> bool:
    if not z.requires_any:
        return True
    for req in z.requires_any:
        if chosen_counts.get(req, 0) > 0:
            return True
    return False


def generate_wave(rng: random.Random, cfg: LevelConfig, zombie_pool: list[ZombieType], wave_budget: int) -> dict:
    remaining = wave_budget
    counts: dict[str, int] = {}
    if not zombie_pool:
        return {"budget": wave_budget, "spent": 0, "remaining": wave_budget, "spawns": []}

    min_cost = min(z.cost for z in zombie_pool)
    max_cost = max(z.cost for z in zombie_pool)
    spread = max(1, max_cost - min_cost)
    greed_exp = (cfg.greediness - 0.5) * 2.0  # -1..1

    while remaining >= min_cost:
        candidates = []
        for z in zombie_pool:
            if z.cost <= remaining and is_requirements_met(counts, z):
                cost_factor = 1.0 + (z.cost - min_cost) / spread
                adjusted = z.weight * (cost_factor ** greed_exp)
                candidates.append((z, adjusted))

        if not candidates:
            break

        pick = pick_weighted(rng, candidates)
        counts[pick.name] = counts.get(pick.name, 0) + 1
        remaining -= pick.cost

    spawns = [{"Type": name, "Count": count} for name, count in sorted(counts.items())]
    return {
        "budget": wave_budget,
        "spent": wave_budget - remaining,
        "remaining": remaining,
        "spawns": spawns,
    }


def pick_plantfood_waves(rng: random.Random, cfg: LevelConfig) -> list[int]:
    count = cfg.num_waves // max(1, cfg.plantfood_interval)
    if count <= 0:
        return []
    population = list(range(1, cfg.num_waves + 1))
    count = min(count, len(population))
    return sorted(rng.sample(population, count))


def make_empty_occupancy(cfg: LevelConfig) -> set[tuple[int, int]]:
    return set()


def lane_allowed_for_stage(stage: str, row: int) -> bool:
    # Example pirate rule: no graves on rows without planks.
    # You can tune this map to your exact lane layouts.
    blocked_rows_by_stage = {
        "pirate": {0, 4},  # example
        "piratealtverzstage": {0, 4},
    }
    blocked = blocked_rows_by_stage.get(stage.lower(), set())
    return row not in blocked


def random_grave_count(rng: random.Random, cfg: LevelConfig) -> int:
    max_count = min(20, max(0, cfg.max_initial_graves))
    if max_count == 0:
        return 0
    # Rule: cannot be 1/2/3. Either 0 or >= 4.
    if max_count < 4:
        return 0
    if rng.random() < 0.35:
        return 0
    return rng.randint(4, max_count)


def allowed_columns_for_zone(zone: str) -> list[int]:
    back = list(range(0, 5))
    middle = list(range(3, 6))
    front = list(range(5, 9))
    if zone == "back":
        return back
    if zone == "middle":
        return middle
    if zone == "front":
        return front
    if zone == "back_middle":
        return sorted(set(back + middle))
    if zone == "middle_front":
        return sorted(set(middle + front))
    return list(range(0, 9))


def place_graves(rng: random.Random, cfg: LevelConfig, occupied: set[tuple[int, int]]) -> list[dict]:
    placements = []
    target = random_grave_count(rng, cfg)
    attempts = 0
    while len(placements) < target and attempts < target * 30:
        attempts += 1
        x = rng.randint(0, cfg.cols - 1)
        y = rng.randint(0, cfg.rows - 1)
        if (x, y) in occupied:
            continue
        if not lane_allowed_for_stage(cfg.stage, y):
            continue
        g = rng.choice(GRAVE_TYPES)
        placements.append({"GridX": x, "GridY": y, "TypeName": g})
        occupied.add((x, y))
    return placements


def slider_position_ok(item_type: str, row: int) -> bool:
    if item_type in {"slider_down", "slider_down_modern"} and row == 4:
        return False
    if item_type in {"slider_up", "slider_up_modern"} and row == 0:
        return False
    return True


def place_neat_items(
    rng: random.Random,
    cfg: LevelConfig,
    occupied: set[tuple[int, int]],
    candidate_types: list[str],
) -> list[dict]:
    placements = []
    pattern_count = rng.randint(0, 3)
    for _ in range(pattern_count):
        item_type = rng.choice(candidate_types)
        pattern = rng.choice(PATTERNS)
        zone = NEAT_ITEM_ZONES.get(item_type, "all")
        valid_cols = allowed_columns_for_zone(zone)
        valid_cols = [c for c in valid_cols if 0 <= c < cfg.cols]
        if not valid_cols:
            continue
        x = rng.choice(valid_cols)
        for y, mark in enumerate(pattern):
            if y >= cfg.rows or mark != "1":
                continue
            if not slider_position_ok(item_type, y):
                continue
            if (x, y) in occupied:
                continue
            placements.append({"GridX": x, "GridY": y, "TypeName": item_type})
            occupied.add((x, y))
    return placements


def choose_card_type(rng: random.Random) -> str:
    combined = GOOD_CARDS + BAD_CARDS
    total = sum(w for _, w in combined)
    roll = rng.random() * total
    running = 0.0
    for name, w in combined:
        running += w
        if roll <= running:
            return name
    return combined[-1][0]


def parse_rtid_alias(rtid: str) -> str | None:
    # RTID(ZombieTutorialDefault@ZombieProperties) -> ZombieTutorialDefault
    if not isinstance(rtid, str):
        return None
    if not rtid.startswith("RTID(") or "@" not in rtid:
        return None
    body = rtid[5:]
    at_index = body.find("@")
    if at_index <= 0:
        return None
    return body[:at_index]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_zombies_from_types_and_properties(
    types_path: Path = DEFAULT_TYPES_PATH,
    properties_path: Path = DEFAULT_PROPERTIES_PATH,
) -> list[ZombieType]:
    types_doc = load_json(types_path)
    props_doc = load_json(properties_path)

    property_by_alias: dict[str, dict] = {}
    for obj in props_doc.get("objects", []):
        aliases = obj.get("aliases")
        if not aliases:
            continue
        if obj.get("objclass") != "ZombiePropertySheet":
            continue
        prop_alias = aliases[0]
        property_by_alias[prop_alias] = obj.get("objdata", {})

    zombies: list[ZombieType] = []
    seen: set[str] = set()
    for obj in types_doc.get("objects", []):
        if obj.get("objclass") != "ZombieType":
            continue
        aliases = obj.get("aliases") or []
        objdata = obj.get("objdata", {})
        type_name = objdata.get("TypeName") or (aliases[0] if aliases else None)
        if not type_name or type_name in seen:
            continue

        properties_rtid = objdata.get("Properties")
        prop_alias = parse_rtid_alias(properties_rtid)
        if not prop_alias:
            continue
        prop = property_by_alias.get(prop_alias)
        if not prop:
            continue

        wave_cost = prop.get("WavePointCost")
        weight = prop.get("Weight")
        if not isinstance(wave_cost, (int, float)) or wave_cost <= 0:
            continue
        if not isinstance(weight, (int, float)) or weight <= 0:
            continue

        zombies.append(
            ZombieType(
                name=type_name,
                weight=float(weight),
                cost=int(wave_cost),
            )
        )
        seen.add(type_name)

    return zombies


def to_rtid_zombie(name: str) -> str:
    return f"RTID({name}@ZombieTypes)"


def wave_to_spawn_entries(rng: random.Random, rows: int, wave: dict) -> list[dict]:
    entries = []
    for spawn in wave["spawns"]:
        zombie_name = spawn["Type"]
        count = spawn["Count"]
        for _ in range(count):
            entries.append(
                {
                    "Row": str(rng.randint(1, rows)),
                    "Type": to_rtid_zombie(zombie_name),
                }
            )
    return entries


def build_level(cfg: LevelConfig, zombie_pool: list[ZombieType]) -> dict:
    rng = random.Random(cfg.seed)
    waves = []
    for wave_idx in range(1, cfg.num_waves + 1):
        budget = wave_cost_for_index(wave_idx, cfg)
        wave = generate_wave(rng, cfg, zombie_pool, budget)
        wave["WaveIndex"] = wave_idx
        wave["IsFlag"] = cfg.flag_interval > 0 and wave_idx % cfg.flag_interval == 0
        waves.append(wave)

    occupied = make_empty_occupancy(cfg)
    initial_grid = []
    initial_grid.extend(place_graves(rng, cfg, occupied))
    initial_grid.extend(
        place_neat_items(
            rng,
            cfg,
            occupied,
            candidate_types=[
                "goldtile",
                "speaker",
                "surfboard",
                "powertile_alpha",
                "powertile_beta",
                "powertile_gamma",
                "bufftile_speed",
                "bufftile_attack",
                "bufftile_shield",
                "presentSunOnDestruction",
                "carnie_card_unactivated",
                "slider_up",
                "slider_up_modern",
                "slider_down",
                "slider_down_modern",
            ],
        )
    )

    card_preview = [choose_card_type(rng) for _ in range(8)]
    plantfood_waves = set(pick_plantfood_waves(rng, cfg))
    wave_aliases = [f"Wave{i}" for i in range(1, cfg.num_waves + 1)]
    zombie_pool_names = [z.name for z in zombie_pool]

    objects = [
        {
            "objclass": "LevelDefinition",
            "objdata": {
                "StartingSun": 50,
                "Description": "Custom Level",
                "FirstRewardParam": "moneybag",
                "NormalPresentTable": "egypt_normal_01",
                "ShinyPresentTable": "egypt_shiny_01",
                "Loot": "RTID(DefaultLoot@LevelModules)",
                "ResourceGroupNames": [
                    "DelayLoad_Background_Beach",
                    "DelayLoad_Background_Beach_Compressed",
                    "Tombstone_Dark_Special",
                    "Tombstone_Dark_Effects",
                    "Dirt_Spawn_Pirate",
                ],
                "Modules": [
                    "RTID(OffScreenZombiesCoinOverride@LevelModules)",
                    "RTID(ModernMowers@LevelModules)",
                    "RTID(StandardIntro@LevelModules)",
                    "RTID(GI@CurrentLevel)",
                    "RTID(IPP@CurrentLevel)",
                    "RTID(Rails@CurrentLevel)",
                    "RTID(SeedBank@CurrentLevel)",
                    "RTID(DefaultSunDropper@LevelModules)",
                    "RTID(Escalation@CurrentLevel)",
                    "RTID(NewWaves@CurrentLevel)",
                    "RTID(ZombiesDeadWinCon@LevelModules)",
                    "RTID(DefaultZombieWinCondition@LevelModules)",
                    "RTID(MarketRandomizerModule@LevelModules)",
                ],
                "Name": cfg.level_name,
                "StageModule": cfg.stage_module,
            },
        },
        {
            "aliases": ["SeedBank"],
            "objclass": "SeedBankProperties",
            "objdata": {
                "PresetPlantList": [],
                "PlantIncludeList": [],
                "PlantExcludeList": [],
                "SelectionMethod": "chooser",
            },
        },
        {
            "aliases": ["GI"],
            "objclass": "InitialGridItemProperties",
            "objdata": {"InitialGridItemPlacements": initial_grid},
        },
        {
            "aliases": ["IPP"],
            "objclass": "InitialPlantProperties",
            "objdata": {"InitialPlantPlacements": []},
        },
        {
            "aliases": ["Rails"],
            "objclass": "RailcartProperties",
            "objdata": {"RailcartType": "railcart_cowboy", "Railcarts": [], "Rails": []},
        },
        {
            "aliases": ["Escalation"],
            "objclass": "LevelEscalationModuleProperties",
            "objdata": {
                "FlagCount": cfg.num_waves // max(1, cfg.flag_interval),
                "WavesPerFlag": cfg.flag_interval,
                "PlantfoodToSpawnCount": len(plantfood_waves),
                "StartingPoints": cfg.base_wave_cost,
                "PointIncrementPerWave": cfg.wave_cost_growth,
                "WaveManagerProps": "RTID(WaveManager@CurrentLevel)",
                "ZombiePool": [to_rtid_zombie(name) for name in zombie_pool_names],
            },
        },
        {"aliases": ["NewWaves"], "objclass": "WaveManagerModuleProperties", "objdata": {}},
        {
            "aliases": ["WaveManager"],
            "objclass": "WaveManagerProperties",
            "objdata": {
                "FlagWaveInterval": cfg.flag_interval,
                "WaveCount": cfg.num_waves,
                "SuppressFlagZombie": False,
                "Waves": [[f"RTID({alias}@.)"] for alias in wave_aliases],
            },
        },
    ]

    for i, wave in enumerate(waves, start=1):
        objects.append(
            {
                "aliases": [f"Wave{i}"],
                "objclass": "SpawnZombiesJitteredWaveActionProps",
                "objdata": {
                    "AdditionalPlantfood": 1 if i in plantfood_waves else 0,
                    "Zombies": wave_to_spawn_entries(rng, cfg.rows, wave),
                },
            }
        )

    return {
        "#comment": "My Level | Randomizer",
        "#zombies": ", ".join(zombie_pool_names),
        "objects": objects + [{}],
        "version": 1,
        "_debug": {
            "Config": {
                "num_waves": cfg.num_waves,
                "base_wave_cost": cfg.base_wave_cost,
                "wave_cost_growth": cfg.wave_cost_growth,
                "flag_interval": cfg.flag_interval,
                "flag_bonus_cost": cfg.flag_bonus_cost,
                "greediness": cfg.greediness,
                "stage": cfg.stage,
                "seed": cfg.seed,
            },
            "WavesBudget": waves,
            "CardPreview": card_preview,
        },
    }


if __name__ == "__main__":
    config = LevelConfig(
        num_waves=16,
        base_wave_cost=1,
        wave_cost_growth=1,
        flag_interval=4,
        flag_bonus_cost=4,
        greediness=0.5,
        plantfood_interval=8,
        stage="pirate",
        max_initial_graves=8,
        seed=42,
    )
    zombies = load_zombies_from_types_and_properties()
    if not zombies:
        raise RuntimeError(
            "No zombies loaded from ZOMBIETYPES_UPDATED.json + ZOMBIEPROPERTIES_UPDATED.json."
        )
    level = build_level(config, zombies)
    print(json.dumps(level, indent=2))
