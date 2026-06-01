import os
import csv
import xml.etree.ElementTree as ET
from html import escape

# Paths
USED_DATASETS_DIR = r"C:\Users\rayan\Documents\dev\odoo_world_cup\used_datasets"
CSV_TOURNAMENTS = os.path.join(USED_DATASETS_DIR, "dataset 0 worldcup-master", "worldcup-master", "data-csv", "tournaments.csv")
CSV_TEAMS = os.path.join(USED_DATASETS_DIR, "dataset 0 worldcup-master", "worldcup-master", "data-csv", "teams.csv")
CSV_STADIUMS = os.path.join(USED_DATASETS_DIR, "dataset 0 worldcup-master", "worldcup-master", "data-csv", "stadiums.csv")
CSV_MATCHES = os.path.join(USED_DATASETS_DIR, "dataset 0 worldcup-master", "worldcup-master", "data-csv", "matches.csv")
CSV_LPI = os.path.join(USED_DATASETS_DIR, "WB_LPI(World Bank _ Logistics Performance Index (LPI)).csv")

OUTPUT_DIR = r"C:\Users\rayan\Documents\dev\odoo_world_cup\custom_modules\wc_data\data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Helper for XML generation
def clean_xml_string(val):
    if not val:
        return ""
    # Remove bad characters that break XML parsing
    val = val.replace('\x00', '')
    return escape(val)

# Country mapping helper
def map_country(country_name):
    if not country_name:
        return 'other'
    country_lower = country_name.strip().lower()
    
    mapping = {
        'uruguay': 'uruguay',
        'italy': 'italy',
        'france': 'france',
        'brazil': 'brazil',
        'switzerland': 'switzerland',
        'sweden': 'sweden',
        'chile': 'chile',
        'england': 'england',
        'mexico': 'mexico',
        'germany': 'germany',
        'west germany': 'germany',
        'argentina': 'argentina',
        'usa': 'usa',
        'united states': 'usa',
        'korea': 'korea',
        'south korea': 'korea',
        'korea republic': 'korea',
        'japan': 'japan',
        'south africa': 'south_africa',
        'russia': 'russia',
        'qatar': 'qatar',
        'spain': 'spain',
        'morocco': 'morocco',
        'portugal': 'portugal'
    }
    
    for key, val in mapping.items():
        if key in country_lower:
            return val
    return 'other'

# Match phase mapping helper
def map_phase(stage_name):
    if not stage_name:
        return 'group'
    stage_lower = stage_name.strip().lower()
    
    if 'group' in stage_lower:
        return 'group'
    elif 'round of 16' in stage_lower or 'eighth' in stage_lower or '1/8' in stage_lower:
        return 'round16'
    elif 'quarter' in stage_lower or '1/4' in stage_lower:
        return 'quarter'
    elif 'semi' in stage_lower or '1/2' in stage_lower:
        return 'semi'
    elif 'third' in stage_lower or '3rd' in stage_lower:
        return 'third'
    elif 'final' in stage_lower:
        return 'final'
    return 'group'

# Step 1: Parse LPI data
print("Step 1: Parsing World Bank LPI data...")
lpi_data = {}
if os.path.exists(CSV_LPI):
    with open(CSV_LPI, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('INDICATOR') == 'LPI_OVR':
                code = row.get('REF_AREA')
                year = int(row.get('TIME_PERIOD', 0))
                try:
                    val = float(row.get('OBS_VALUE', 0))
                except ValueError:
                    val = 0.0
                
                # We want the latest available year
                if code not in lpi_data or lpi_data[code]['year'] < year:
                    lpi_data[code] = {'score': val, 'year': year}

# Compute ranks from LPI data
sorted_lpi = sorted([(code, info['score']) for code, info in lpi_data.items()], key=lambda x: x[1], reverse=True)
lpi_ranks = {code: rank + 1 for rank, (code, score) in enumerate(sorted_lpi)}
print(f"Loaded LPI data for {len(lpi_data)} countries.")

# Step 2: Parse Teams and create team_data.xml
print("Step 2: Parsing teams...")
teams_list = []
team_codes = set()
with open(CSV_TEAMS, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        code = row.get('team_code')
        name = row.get('team_name')
        confed = row.get('confederation_code')
        
        # Avoid duplicate team entries
        if code in team_codes or not code:
            continue
        team_codes.add(code)
        
        lpi_info = lpi_data.get(code, {'score': 0.0})
        rank = lpi_ranks.get(code, 0)
        
        teams_list.append({
            'code': code,
            'name': name,
            'confed': confed,
            'lpi_score': lpi_info['score'],
            'lpi_rank': rank
        })

print(f"Parsed {len(teams_list)} teams. Generating team_data.xml...")
xml_teams = []
xml_teams.append('<?xml version="1.0" encoding="UTF-8"?>')
xml_teams.append('<odoo>')
xml_teams.append('    <data noupdate="1">')

for team in teams_list:
    xml_teams.append(f'        <record id="team_{team["code"]}" model="wc.team">')
    xml_teams.append(f'            <field name="name">{clean_xml_string(team["name"])}</field>')
    xml_teams.append(f'            <field name="code_fifa">{clean_xml_string(team["code"])}</field>')
    if team['confed'] in ['CAF', 'UEFA', 'CONMEBOL', 'CONCACAF', 'AFC', 'OFC']:
        xml_teams.append(f'            <field name="confederation">{team["confed"]}</field>')
    if team['lpi_score'] > 0:
        xml_teams.append(f'            <field name="lpi_score">{team["lpi_score"]:.2f}</field>')
        xml_teams.append(f'            <field name="lpi_rank">{team["lpi_rank"]}</field>')
    xml_teams.append('        </record>')

xml_teams.append('    </data>')
xml_teams.append('</odoo>')

with open(os.path.join(OUTPUT_DIR, "team_data.xml"), "w", encoding="utf-8") as f:
    f.write("\n".join(xml_teams))
print("team_data.xml generated.")

# Step 3: Parse Stadiums and generate stadium_historical_data.xml
print("Step 3: Parsing stadiums...")
stadiums_list = []
stadium_ids = set()
with open(CSV_STADIUMS, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        sid = row.get('stadium_id')
        name = row.get('stadium_name')
        city = row.get('city_name')
        country = row.get('country_name')
        try:
            capacity = int(row.get('stadium_capacity', 0))
        except ValueError:
            capacity = 0
            
        if sid in stadium_ids or not sid:
            continue
        stadium_ids.add(sid)
        
        stadiums_list.append({
            'id': sid.replace('-', '_'),
            'name': name,
            'city': city,
            'country': map_country(country),
            'capacity': capacity
        })

print(f"Parsed {len(stadiums_list)} stadiums. Generating stadium_historical_data.xml...")
xml_stads = []
xml_stads.append('<?xml version="1.0" encoding="UTF-8"?>')
xml_stads.append('<odoo>')
xml_stads.append('    <data noupdate="1">')

for stad in stadiums_list:
    xml_stads.append(f'        <record id="stadium_{stad["id"]}" model="wc.stadium">')
    xml_stads.append(f'            <field name="name">{clean_xml_string(stad["name"])}</field>')
    xml_stads.append(f'            <field name="city">{clean_xml_string(stad["city"])}</field>')
    xml_stads.append(f'            <field name="capacity">{stad["capacity"]}</field>')
    xml_stads.append(f'            <field name="country">{stad["country"]}</field>')
    xml_stads.append(f'            <field name="state">ready</field>')
    xml_stads.append('        </record>')

xml_stads.append('    </data>')
xml_stads.append('</odoo>')

with open(os.path.join(OUTPUT_DIR, "stadium_historical_data.xml"), "w", encoding="utf-8") as f:
    f.write("\n".join(xml_stads))
print("stadium_historical_data.xml generated.")

# Step 4: Parse Matches (pre-read to aggregate tournament stats)
print("Step 4: Parsing matches to aggregate tournament stats...")
tourn_stats = {} # tournament_id -> {matches_count, goals_count, match_records}
with open(CSV_MATCHES, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        tid = row.get('tournament_id')
        if not tid:
            continue
        if tid not in tourn_stats:
            tourn_stats[tid] = {'matches_count': 0, 'goals_count': 0, 'matches': []}
            
        # Parse scores
        try:
            h_score = int(row.get('home_team_score', 0))
            a_score = int(row.get('away_team_score', 0))
        except ValueError:
            h_score = 0
            a_score = 0
            
        tourn_stats[tid]['matches_count'] += 1
        tourn_stats[tid]['goals_count'] += (h_score + a_score)
        
        # Store match data
        tourn_stats[tid]['matches'].append(row)

# Step 5: Parse Tournaments and generate tournament_data.xml
print("Step 5: Parsing tournaments...")
tournaments_list = []
with open(CSV_TOURNAMENTS, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        tid = row.get('tournament_id')
        name = row.get('tournament_name')
        year = int(row.get('year', 0))
        host = row.get('host_country')
        winner = row.get('winner')
        try:
            teams_count = int(row.get('count_teams', 0))
        except ValueError:
            teams_count = 0
            
        stats = tourn_stats.get(tid, {'matches_count': 0, 'goals_count': 0})
        
        tournaments_list.append({
            'id': tid.replace('-', '_'),
            'key': tid,
            'name': name,
            'year': year,
            'host': host,
            'winner': winner,
            'teams_count': teams_count,
            'matches_count': stats['matches_count'],
            'goals_count': stats['goals_count']
        })

print(f"Parsed {len(tournaments_list)} tournaments. Generating tournament_data.xml...")
xml_tourns = []
xml_tourns.append('<?xml version="1.0" encoding="UTF-8"?>')
xml_tourns.append('<odoo>')
xml_tourns.append('    <data noupdate="1">')

for tourn in tournaments_list:
    xml_tourns.append(f'        <record id="tournament_{tourn["id"]}" model="wc.tournament">')
    xml_tourns.append(f'            <field name="key">{clean_xml_string(tourn["key"])}</field>')
    xml_tourns.append(f'            <field name="name">{clean_xml_string(tourn["name"])}</field>')
    xml_tourns.append(f'            <field name="year">{tourn["year"]}</field>')
    xml_tourns.append(f'            <field name="host_country">{clean_xml_string(tourn["host"])}</field>')
    xml_tourns.append(f'            <field name="winner">{clean_xml_string(tourn["winner"])}</field>')
    xml_tourns.append(f'            <field name="teams_count">{tourn["teams_count"]}</field>')
    xml_tourns.append(f'            <field name="matches_count">{tourn["matches_count"]}</field>')
    xml_tourns.append(f'            <field name="goals_count">{tourn["goals_count"]}</field>')
    xml_tourns.append('        </record>')

xml_tourns.append('    </data>')
xml_tourns.append('</odoo>')

with open(os.path.join(OUTPUT_DIR, "tournament_data.xml"), "w", encoding="utf-8") as f:
    f.write("\n".join(xml_tourns))
print("tournament_data.xml generated.")

# Step 6: Generate match_historical_data.xml
print("Step 6: Generating match_historical_data.xml...")
xml_matches = []
xml_matches.append('<?xml version="1.0" encoding="UTF-8"?>')
xml_matches.append('<odoo>')
xml_matches.append('    <data noupdate="1">')

match_count = 0
for tid, stats in tourn_stats.items():
    tourn_xml_id = f"tournament_{tid.replace('-', '_')}"
    for match in stats['matches']:
        mid = match.get('match_id')
        name = match.get('match_name')
        date_str = match.get('match_date')
        time_str = match.get('match_time', '00:00')
        stadium_id = match.get('stadium_id', '').replace('-', '_')
        
        home_code = match.get('home_team_code')
        away_code = match.get('away_team_code')
        
        try:
            home_score = int(match.get('home_team_score', 0))
            away_score = int(match.get('away_team_score', 0))
        except ValueError:
            home_score = 0
            away_score = 0
            
        phase = map_phase(match.get('stage_name'))
        
        # Combine date and time
        if not time_str or time_str == 'not applicable':
            time_str = '00:00'
        # ensure time is HH:MM
        if len(time_str) == 5:
            datetime_val = f"{date_str} {time_str}:00"
        else:
            datetime_val = f"{date_str} 00:00:00"
            
        xml_id = f"match_{mid.replace('-', '_')}"
        
        xml_matches.append(f'        <record id="{xml_id}" model="wc.match">')
        # Char names
        xml_matches.append(f'            <field name="team_a">{clean_xml_string(match.get("home_team_name"))}</field>')
        xml_matches.append(f'            <field name="team_b">{clean_xml_string(match.get("away_team_name"))}</field>')
        
        # Many2one links (with checks if codes are valid)
        if home_code in team_codes:
            xml_matches.append(f'            <field name="team_a_id" ref="team_{home_code}"/>')
        if away_code in team_codes:
            xml_matches.append(f'            <field name="team_b_id" ref="team_{away_code}"/>')
            
        xml_matches.append(f'            <field name="tournament_id" ref="{tourn_xml_id}"/>')
        if stadium_id in stadium_ids:
            xml_matches.append(f'            <field name="stadium_id" ref="stadium_{stadium_id}"/>')
        else:
            # Fallback to Marrakech stadium if stadium is missing
            xml_matches.append(f'            <field name="stadium_id" ref="wc_base.stadium_marrakech"/>')
            
        xml_matches.append(f'            <field name="date_time">{datetime_val}</field>')
        xml_matches.append(f'            <field name="phase">{phase}</field>')
        xml_matches.append(f'            <field name="state">done</field>')
        xml_matches.append(f'            <field name="score_a">{home_score}</field>')
        xml_matches.append(f'            <field name="score_b">{away_score}</field>')
        xml_matches.append(f'            <field name="is_historical">True</field>')
        xml_matches.append('        </record>')
        match_count += 1

xml_matches.append('    </data>')
xml_matches.append('</odoo>')

with open(os.path.join(OUTPUT_DIR, "match_historical_data.xml"), "w", encoding="utf-8") as f:
    f.write("\n".join(xml_matches))
print(f"match_historical_data.xml generated with {match_count} records.")
print("ETL Import completed successfully!")
