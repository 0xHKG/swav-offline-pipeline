import json
import yaml
from pathlib import Path

rows = json.loads(Path('storyboard_rows.json').read_text(encoding='utf-8'))
rows_by_no = {row['row_no']: row for row in rows}

methods = {
    '1': 't2v',
    '2': 'img2vid',
    '3': 'img2vid',
    '4': 'img2vid',
    '5': 't2v',
    '6': 't2v',
    '7': 'img2vid',
    '8': 'img2vid',
    '9': 't2v',
    '10': 't2v',
    '11': 'img2vid',
    '12': 't2v',
    '13': 'img2vid',
    '14': 'img2vid',
    '15': 't2v',
    '16': 'img2vid',
    '17': 'img2vid',
    '18': 't2v',
    '19': 'img2vid',
    '20': 'img2vid',
    '21': 't2v',
    '22': 'img2vid',
    '23': 'img2vid',
    '24': 'img2vid',
    '25': 't2v',
    '26': 't2v',
    '27': 't2v',
    '28': 'img2vid',
    '29': 't2v',
    '30': 't2v',
    '31': 'img2vid',
    '32': 't2v',
    '33': 'img2vid',
    '34': 't2v',
    '35': 'img2vid',
    '36': 't2v',
    '37': 't2v',
    '38': 't2v',
    '39': 'img2vid',
    '40': 't2v',
    '41': 'img2vid',
    '42': 'img2vid',
    '43': 'img2vid',
    '44': 't2v',
    '45': 'img2vid',
    '46': 'img2vid',
    '47': 't2v',
    '48': 'img2vid',
    '49': 't2v',
    '50': 't2v',
    '51': 't2v',
    '52': 't2v',
    '53': 'img2vid',
    '54': 't2v',
}

base_durations = {
    '1': 5.0,
    '2': 6.0,
    '3': 6.5,
    '4': 6.0,
    '5': 4.5,
    '6': 5.0,
    '7': 6.5,
    '8': 6.0,
    '9': 5.0,
    '10': 5.0,
    '11': 6.5,
    '12': 5.0,
    '13': 6.0,
    '14': 6.0,
    '15': 5.0,
    '16': 6.0,
    '17': 6.0,
    '18': 5.0,
    '19': 6.5,
    '20': 6.0,
    '21': 5.0,
    '22': 6.0,
    '23': 6.0,
    '24': 6.0,
    '25': 5.0,
    '26': 5.0,
    '27': 5.0,
    '28': 6.0,
    '29': 5.0,
    '30': 5.0,
    '31': 6.0,
    '32': 5.0,
    '33': 6.0,
    '34': 5.0,
    '35': 6.0,
    '36': 5.0,
    '37': 5.0,
    '38': 5.0,
    '39': 6.0,
    '40': 5.0,
    '41': 6.0,
    '42': 6.0,
    '43': 6.5,
    '44': 5.0,
    '45': 6.0,
    '46': 6.0,
    '47': 5.0,
    '48': 6.0,
    '49': 5.0,
    '50': 5.0,
    '51': 5.0,
    '52': 5.0,
    '53': 6.5,
    '54': 5.0,
}

prompts = {
    '1': 'formal still of Indian Navy crest over the Indian flag with view of Manekshaw Centre facade in evening light',
    '2': 'steady tracking corridor view with naval officers and sailors walking past framed photographs and exhibition signage',
    '3': 'sequence of Indian Navy assets including INS Vikrant at sea, frigate at speed, submarine diving, carrier deck operations, destroyer missile launch, and research laboratories',
    '4': 'welcoming area at the NIIO exhibition with lamp lighting ceremony and organised hall entrance',
    '5': 'simple navy blue counter graphic displaying programme metrics with minimal animation',
    '6': 'navy blue title card reading Operational Readiness: Crew Safety & Damage Control with clean typography',
    '7': 'shipboard firefighting drill with crew in aerogel suits deploying thermal drone and rugged torch inside smoke',
    '8': 'detail shots of firefighting retrofit equipment cooling vest and hydraulic cutter being prepared by sailors',
    '9': 'orderly exhibition plinths showing aerogel suits caged drone retrofit kits cooling vests and hydraulic cutter with naval personnel discussing',
    '10': 'navy blue title card reading Undersea Robotics & Subsea Enablers with clean typography',
    '11': 'autonomous underwater vehicle departing from rhb with navigation overlay showing precise bathymetry track',
    '12': 'graphic of underwater communication swarm linking multiple auvs with mission status updates on shipboard display',
    '13': 'remotely operated vehicle inspecting ship hull while diver supervises and corrosion area is tagged',
    '14': 'submarine launching slxbt with operators reviewing temperature profile and voyage data recorder display',
    '15': 'navy blue title card reading C4ISR: The Real-Time Maritime Picture with clean typography',
    '16': 'split screen showing uav convoy feed routed through encore relay vegazl throughput gauge and shipboard esm console',
    '17': 'command centre common operating picture aligning tracks classifying threat emissions and timestamping video feed',
    '18': 'navy blue title card reading Autonomy at Sea with clean typography',
    '19': 'autonomous weaponised boats forming skirmish line ahead of naval task group in open water',
    '20': 'autonomous beach survey device mapping surf zone with tablet highlighting obstacles and depth colours',
    '21': 'navy blue title card reading Aviation Safety & Ground Operations AI with clean typography',
    '22': 'airfield apron camera detecting foreign object debris with ground crew removing metallic shard',
    '23': 'nighttime helicopter approach to ship using gnss 3d guidance cues for deck landing',
    '24': 'small unmanned aircraft with lightweight elint comint pod taxiing and console showing precise geolocation fix',
    '25': 'navy blue title card reading Acoustics & ASW Enablers with clean typography',
    '26': 'forward looking sonar console visualising harbour ingress with obstructions clearly marked',
    '27': 'spectrogram comparison showing adaptive noise cancellation revealing sonar targets',
    '28': 'coxswain deploying ematt training torpedo with operators logging parameters and portable rcs measurement',
    '29': 'navy blue title card reading Sensors & Silicon with clean typography',
    '30': 'macro view of indigenous aesa radar modules cooling plate and inspection lighting',
    '31': 'electro optical infrared sensor pod under wing providing fused imagery with clear identifiers',
    '32': 'lab bench with asic beamforming radar board running test pattern observed by engineers',
    '33': 'airborne lightweight comint rack being updated before a small aircraft takes off',
    '34': 'navy blue title card reading Positioning When GNSS Is Denied with clean typography',
    '35': 'automated celestial navigation unit tracking stars and displaying position fix alongside inertial data',
    '36': 'graphic showing depth based positioning between ship and submarine with contours and pressure data',
    '37': 'laboratory quantum positioning prototype with stability plot and technicians reviewing',
    '38': 'navy blue title card reading Harbour Turn-around & Shore Systems with clean typography',
    '39': 'time lapse of smart retractable gangways shore power units and logistics trolley servicing berthed submarine',
    '40': 'navy blue title card reading Logistics & Persistent ISR with clean typography',
    '41': 'heavy lift tethered aerial vehicle holding steady overwatch above harbour entrance',
    '42': 'rooftop skydeck arm autonomously launching and recovering quadcopter charging between sorties',
    '43': 'autonomous cargo drone transporting crate from jetty to anchored ship then flying long patrol leg',
    '44': 'navy blue title card reading Special Operations & Deck-Edge Aids with clean typography',
    '45': 'boarding team preparing with smart reflex sight and programmed standoff warhead drill',
    '46': 'special operations expendable payload delivery tube deploying package from rhb with gps confirmation',
    '47': 'navy blue title card reading Materials & Protective Systems with clean typography',
    '48': 'demonstration of hydrophobic weapon cover shedding spray and stealth insulation reducing infrared signature',
    '49': 'navy blue title card reading The Working Forum with clean typography',
    '50': 'exhibition floor with capability title cards naval officers engaging innovators and taking notes',
    '51': 'panel discussion with navy leadership industry and academia identified by role',
    '52': 'quiet niio corridor showing milestone wall signed trial cards and stamped documents',
    '53': 'recap montage highlighting capability exemplars and exterior of manekshaw centre at dusk',
    '54': 'formal closing slate with bilingual slogan and niio footer on navy background',
}

overlay_texts = {
    '1': [
        'SWAVLAMBAN 2025 · Manekshaw Centre · 25–26 Nov 2025',
        'STRENGTH & POWER THROUGH INNOVATION AND INDIGENISATION',
        'नवाचार एवं स्वदेशीकरण से सशक्तिकरण',
    ],
    '54': [
        'SWAVLAMBAN 2025 · Manekshaw Centre · 25–26 Nov 2025',
        'STRENGTH & POWER THROUGH INNOVATION AND INDIGENISATION',
        'नवाचार एवं स्वदेशीकरण से सशक्तिकरण',
        'Organised by the Naval Innovation & Indigenisation Organisation (NIIO)',
    ],
}

scene_order = [
    ('Opening', ['1', '2', '3', '4', '5']),
    ('Operational Readiness: Crew Safety & Damage Control', ['6', '7', '8', '9']),
    ('Undersea Robotics & Subsea Enablers', ['10', '11', '12', '13', '14']),
    ('C4ISR: The Real-Time Maritime Picture', ['15', '16', '17']),
    ('Autonomy at Sea', ['18', '19', '20']),
    ('Aviation Safety & Ground Operations AI', ['21', '22', '23', '24']),
    ('Acoustics & ASW Enablers', ['25', '26', '27', '28']),
    ('Sensors & Silicon', ['29', '30', '31', '32', '33']),
    ('Positioning When GNSS Is Denied', ['34', '35', '36', '37']),
    ('Harbour Turn-around & Shore Systems', ['38', '39']),
    ('Logistics & Persistent ISR', ['40', '41', '42', '43']),
    ('Special Operations & Deck-Edge Aids', ['44', '45', '46']),
    ('Materials & Protective Systems', ['47', '48']),
    ('The Working Forum', ['49', '50', '51', '52']),
    ('Finale', ['53', '54']),
]

def adjusted_duration(row_no: str) -> float:
    base = base_durations[row_no]
    audio = rows_by_no[row_no]['audio']
    if len(audio) > 160:
        scaled = base * len(audio) / 160.0
    else:
        scaled = base
    return round(scaled, 1)

project = {
    'title': 'Swavlamban 2025',
    'venue': 'Manekshaw Centre',
    'dates': '25–26 Nov 2025',
    'fps': 30,
    'voice': 'male',
    'resolution': '4k',
    'music_tag': 'ceremonial, dignified, 72 bpm',
}

scenes = []
for scene_name, row_nos in scene_order:
    shots = []
    for row_no in row_nos:
        row = rows_by_no[row_no]
        narration = row['audio']
        if row_no == '17':
            narration = narration.rstrip() + ' This is Strength and Power through Innovation and Indigenisation.'
        shot = {
            'row_no': int(row_no),
            'method': methods[row_no],
            'prompt': prompts[row_no],
            'duration_s': adjusted_duration(row_no),
            'narration': narration,
        }
        overlay = overlay_texts.get(row_no)
        if overlay:
            shot['overlay_text'] = overlay
        shots.append(shot)
    scenes.append({'name': scene_name, 'shots': shots})

storyboard = {
    'project': project,
    'scenes': scenes,
}

yaml_str = yaml.safe_dump(storyboard, sort_keys=False, allow_unicode=True)
Path('storyboard.swav2025.yaml').write_text(yaml_str, encoding='utf-8')
print('storyboard.swav2025.yaml written with', len(rows), 'shots')
