#!/usr/bin/env python3
"""
Download firm-supplied media from partial_media.csv and propose curation targets.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd
from slugify import slugify

BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "partial_media.csv"
DEST_ROOT = BASE_DIR / "assets" / "source"

CHECKLIST: Dict[str, List[str]] = {
    "assets/logos/indian_navy_crest.png": ["navy", "crest"],
    "assets/venues/manekshaw_centre_facade.jpg": ["manekshaw", "centre", "facade"],
    "assets/exhibition/niio_welcome_desk.jpg": ["niio", "welcome"],
    "assets/metrics/swavlamban_counter.png": ["counter", "metric"],
    "assets/gear/aerogel_fire_proximity_suit.jpg": ["aerogel", "suit"],
    "assets/gear/caged_drone_tic.jpg": ["drone", "caged"],
    "assets/gear/dcff_torch.jpg": ["torch", "dc"],
    "assets/gear/fire_retrofit_kit.jpg": ["retrofit"],
    "assets/gear/cooling_vest.jpg": ["cooling", "vest"],
    "assets/gear/hydraulic_metal_cutter.jpg": ["hydraulic", "cutter"],
    "assets/auv/underwater_navigation_overlay.png": ["navigation", "overlay"],
    "assets/auv/swarm_comms_screen.png": ["swarm", "comms"],
    "assets/auv/rov_hull_inspection.jpg": ["rov", "hull"],
    "assets/auv/slxbt_launch.jpg": ["slxbt"],
    "assets/c4isr/encore_relay_console.jpg": ["encore"],
    "assets/c4isr/cop_dashboard.jpg": ["cop"],
    "assets/autonomy/boat_swarm_patrol.jpg": ["boat", "swarm"],
    "assets/autonomy/beach_survey_device.jpg": ["beach", "survey"],
    "assets/aviation/fod_detection_camera.jpg": ["fod"],
    "assets/aviation/gnss_ship_landing.jpg": ["gnss"],
    "assets/aviation/lightweight_elint_rpa.jpg": ["elint"],
    "assets/asw/forward_looking_sonar_display.png": ["sonar"],
    "assets/asw/adaptive_noise_spectrogram.png": ["spectrogram"],
    "assets/asw/ematt_training_deploy.jpg": ["ematt"],
    "assets/sensors/aesa_module_macro.jpg": ["aesa"],
    "assets/sensors/eoir_pod_fusion.jpg": ["eoir", "pod"],
    "assets/sensors/asic_beamforming_lab.jpg": ["asic"],
    "assets/sensors/airborne_comint_rack.jpg": ["comint"],
    "assets/positioning/celestial_navigation_unit.jpg": ["celestial"],
    "assets/positioning/depth_based_positioning_graphic.png": ["depth"],
    "assets/positioning/quantum_positioning_lab.jpg": ["quantum"],
    "assets/harbour/retractable_gangway_timelapse.jpg": ["gangway"],
    "assets/harbour/smart_shore_power.jpg": ["shore", "power"],
    "assets/logistics/hl_tethered_aerial_vehicle.jpg": ["tethered"],
    "assets/logistics/skydeck_autolaunch.jpg": ["skydeck"],
    "assets/logistics/autonomous_cargo_uav.jpg": ["cargo"],
    "assets/special_ops/board_team_briefing.jpg": ["boarding"],
    "assets/special_ops/expendable_payload_delivery.jpg": ["payload"],
    "assets/materials/hydrophobic_weapon_cover.jpg": ["hydrophobic"],
    "assets/materials/stealth_insulation_ir.jpg": ["insulation"],
    "assets/forum/exhibition_floor_titles.jpg": ["floor"],
    "assets/forum/panel_discussion.jpg": ["panel"],
    "assets/forum/niio_milestone_wall.jpg": ["milestone"],
    "assets/finale/showcase_collage.jpg": ["collage", "showcase"],
}


def ensure_tools() -> None:
    if not shutil.which("gdown"):
        print("ERROR: gdown is required but not found in PATH. Please install it inside the environment.", file=sys.stderr)
        sys.exit(1)


def is_drive_folder(url: str) -> bool:
    return "/folders/" in url


def run_gdown(url: str, dest: Path, is_folder: bool) -> subprocess.CompletedProcess:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if is_folder:
        dest.mkdir(parents=True, exist_ok=True)
        cmd = ["gdown", "--folder", url, "-O", str(dest)]
    else:
        dest.mkdir(parents=True, exist_ok=True)
        cmd = ["gdown", url, "-O", str(dest)]
    return subprocess.run(cmd, check=False, text=True)


def collect_files(root: Path) -> List[Path]:
    if not root.exists():
        return []
    return [p for p in root.rglob("*") if p.is_file()]


def match_targets(filename: str) -> List[str]:
    name = filename.lower()
    matches = []
    for target, keywords in CHECKLIST.items():
        if all(keyword in name for keyword in keywords):
            matches.append(target)
    return matches


def main() -> None:
    ensure_tools()
    if not CSV_PATH.exists():
        print(f"ERROR: {CSV_PATH} not found.", file=sys.stderr)
        sys.exit(1)

    DEST_ROOT.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(CSV_PATH, sep=";", quotechar='"')
    summary = []
    rename_plan = []
    permission_needed = []

    print("========== SWAVLAMBAN MEDIA PULL ==========")
    for _, row in df.iterrows():
        firm = str(row.get("Please enter your Firm's Name", "")).strip()
        url = str(row.iloc[-1]).strip()
        if not firm or not url or url.lower() == "nan":
            continue
        slug = slugify(firm) or "firm"
        dest = DEST_ROOT / slug
        is_folder = is_drive_folder(url)
        print(f"\n[FIRM] {firm} -> {slug}")
        print(f"  URL: {url}")
        result = run_gdown(url, dest, is_folder)
        if result.returncode != 0:
            print(f"  PERMISSION NEEDED: {url}")
            permission_needed.append(url)
            files = []
        else:
            files = collect_files(dest)
            print(f"  Downloaded assets: {len(files)}")
        summary.append((firm, slug, url, len(files)))

        for file_path in files:
            rel = file_path.relative_to(BASE_DIR)
            matches = match_targets(file_path.name)
            if matches:
                target = matches[0]
                rename_plan.append((rel, target))
            else:
                rename_plan.append((rel, "(no obvious match)"))

    print("\n========== SUMMARY ==========")
    for firm, slug, url, count in summary:
        print(f"- {firm} [{slug}]: {count} files -> {url}")

    if permission_needed:
        print("\n========== PERMISSION NEEDED ==========")
        for url in permission_needed:
            print(f"PERMISSION NEEDED: {url}")

    print("\n========== CURATION SUGGESTIONS ==========")
    for source, target in rename_plan:
        print(f"{source} -> {target}")

    print("\n# Suggested rename script")
    for source, target in rename_plan:
        if target == "(no obvious match)":
            continue
        print(f'mv \"{source}\" \"{target}\"')


if __name__ == "__main__":
    import shutil

    main()
