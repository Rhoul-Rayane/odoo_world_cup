import sys
import os
import requests
import base64
import urllib.parse

odoo_path = r"C:\Users\rayan\Documents\dev\odoo_world_cup\odoo"
sys.path.insert(0, odoo_path)

import odoo
from odoo.modules.registry import Registry
from odoo.api import Environment

# Define the 10 Moroccan Stadiums from Bid Book & guide
STADIUMS_DATA = [
    # Official Match Venues (Gross Capacity >= 40,000)
    {
        'name': 'Grand Stade de Tanger',
        'city': 'Tanger',
        'capacity': 75600,
        'gross_capacity': 75600,
        'net_capacity': 75600,
        'stadium_type': 'match',
        'image_filename': 'tagier_stadium_new.webp',
        'country': 'morocco',
        'fifa_code': 'TNG',
        'gps_lat': 35.7336,
        'gps_lng': -5.8450
    },
    {
        'name': 'Stade Prince Moulay Abdellah',
        'city': 'Rabat',
        'capacity': 68700,
        'gross_capacity': 68700,
        'net_capacity': 68700,
        'stadium_type': 'match',
        'image_filename': 'Complexe Sportif Prince Moulay Abdellah-1.webp',
        'country': 'morocco',
        'fifa_code': 'RBT',
        'gps_lat': 33.9592,
        'gps_lng': -6.8481
    },
    {
        'name': 'Grand Stade Hassan II',
        'city': 'Casablanca',
        'capacity': 115000,
        'gross_capacity': 115000,
        'net_capacity': 115000,
        'stadium_type': 'match',
        'image_filename': 'tagier_stadium_new.webp',  # fallback to Tanger image for rendering
        'country': 'morocco',
        'fifa_code': 'CAS',
        'gps_lat': 33.6214,
        'gps_lng': -7.5028
    },
    {
        'name': 'Stade de Fès',
        'city': 'Fès',
        'capacity': 55800,
        'gross_capacity': 55800,
        'net_capacity': 55800,
        'stadium_type': 'match',
        'image_filename': 'grand-stade-fes-1.webp',
        'country': 'morocco',
        'fifa_code': 'FEZ',
        'gps_lat': 34.0044,
        'gps_lng': -4.9786
    },
    {
        'name': 'Grand Stade de Marrakech',
        'city': 'Marrakech',
        'capacity': 45860,
        'gross_capacity': 45860,
        'net_capacity': 45860,
        'stadium_type': 'match',
        'image_filename': 'Grand Stade de Marrakech-1.webp',
        'country': 'morocco',
        'fifa_code': 'RAK',
        'gps_lat': 31.7056,
        'gps_lng': -7.9806
    },
    {
        'name': 'Grand Stade d\'Agadir',
        'city': 'Agadir',
        'capacity': 46000,
        'gross_capacity': 46000,
        'net_capacity': 46000,
        'stadium_type': 'match',
        'image_filename': 'grand-stade-agadir-1.webp',
        'country': 'morocco',
        'fifa_code': 'AGA',
        'gps_lat': 30.4286,
        'gps_lng': -9.5397
    },
    # Official Training Sites / Team Base Camps (TBC)
    {
        'name': 'Complexe Mohammed V',
        'city': 'Casablanca',
        'capacity': 45000,
        'gross_capacity': 45000,
        'net_capacity': 45000,
        'stadium_type': 'training',
        'image_filename': 'Complexe Mohammed V - Casablanca-1.webp',
        'country': 'morocco',
        'fifa_code': 'MV5',
        'gps_lat': 33.5828,
        'gps_lng': -7.6475
    },
    {
        'name': 'Stade Moulay El Hassan',
        'city': 'Rabat',
        'capacity': 22000,
        'gross_capacity': 22000,
        'net_capacity': 22000,
        'stadium_type': 'training',
        'image_filename': 'moulay_el_hassan_stadium_new.webp',
        'country': 'morocco',
        'fifa_code': 'MEH',
        'gps_lat': 33.9722,
        'gps_lng': -6.8286
    },
    {
        'name': 'Stade Olympique de Rabat',
        'city': 'Rabat',
        'capacity': 21000,
        'gross_capacity': 21000,
        'net_capacity': 21000,
        'stadium_type': 'training',
        'image_filename': 'olymipc_staidum_new.webp',
        'country': 'morocco',
        'fifa_code': 'SOR',
        'gps_lat': 33.9481,
        'gps_lng': -6.8833
    },
    {
        'name': 'Stade Al-Medina',
        'city': 'Rabat',
        'capacity': 18000,
        'gross_capacity': 18000,
        'net_capacity': 18000,
        'stadium_type': 'training',
        'image_filename': 'al_barid_stadium_new_(al madina).webp',
        'country': 'morocco',
        'fifa_code': 'MED',
        'gps_lat': 33.9856,
        'gps_lng': -6.8611
    }
]

def download_and_encode_image(filename):
    if not filename:
        return False
    base_url = "https://moroccostadiumguide.com/images/stadiums/"
    # Encode spaces and special chars
    url = base_url + urllib.parse.quote(filename)
    try:
        print(f"Downloading image from {url} ...")
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            print("  Successfully downloaded!")
            return base64.b64encode(r.content)
        else:
            print(f"  Failed with status code: {r.status_code}")
    except Exception as e:
        print(f"  Error downloading image: {e}")
    return False

def main():
    try:
        config_path = r"C:\Users\rayan\Documents\dev\odoo_world_cup\odoo\odoo.conf"
        odoo.tools.config.parse_config(['-c', config_path])
        db_name = odoo.tools.config.get('db_name') or 'worldcup'
        
        registry = Registry(db_name)
        with registry.cursor() as cr:
            env = Environment(cr, odoo.SUPERUSER_ID, {})
            print(f"Connected to Odoo database: {db_name}")
            
            # 1. PURGE DEPENDENTS
            print("Purging match/stadium dependent records...")
            
            # Security Deployments
            if 'wc.security.deployment' in env:
                deployments = env['wc.security.deployment'].search([])
                print(f"  Unlinking {len(deployments)} security deployments...")
                deployments.unlink()
                
            # Crowd Monitorings
            if 'wc.crowd.monitoring' in env:
                crowd_mons = env['wc.crowd.monitoring'].search([])
                print(f"  Unlinking {len(crowd_mons)} crowd monitoring records...")
                crowd_mons.unlink()
                
            # Incidents
            if 'wc.logistics.incident' in env:
                incidents = env['wc.logistics.incident'].search([])
                print(f"  Unlinking {len(incidents)} logistics incidents...")
                incidents.unlink()
                
            # Logistics Requests
            if 'wc.logistics.request' in env:
                reqs = env['wc.logistics.request'].search([])
                print(f"  Unlinking {len(reqs)} logistics requests...")
                reqs.unlink()
                
            # Logistics Transports
            if 'wc.logistics.transport' in env:
                trans = env['wc.logistics.transport'].search([])
                print(f"  Unlinking {len(trans)} logistics transport records...")
                trans.unlink()
                
            # Sustainability audits
            for model_name in ['wc.waste.tracking', 'wc.carbon.footprint', 'wc.sustainability.audit']:
                if model_name in env:
                    records = env[model_name].search([])
                    print(f"  Unlinking {len(records)} records from {model_name}...")
                    records.unlink()
                    
            # Zones
            if 'wc.stadium.zone' in env:
                zones = env['wc.stadium.zone'].search([])
                print(f"  Unlinking {len(zones)} stadium zones...")
                zones.unlink()
                
            # Logistics resources
            if 'wc.logistics.resource' in env:
                res = env['wc.logistics.resource'].search([])
                print(f"  Unlinking {len(res)} logistics resources...")
                res.unlink()
                
            # Transport stations and parkings
            for model_name in ['wc.transport.station', 'wc.parking.zone', 'wc.transport.schedule']:
                if model_name in env:
                    records = env[model_name].search([])
                    print(f"  Unlinking {len(records)} records from {model_name}...")
                    records.unlink()
            
            # Volunteers stadium preferred/assigned references
            if 'wc.volunteer' in env:
                volunteers = env['wc.volunteer'].search([])
                print(f"  Clearing stadium links on {len(volunteers)} volunteers...")
                volunteers.write({
                    'preferred_stadium_id': False,
                    'assigned_stadium_id': False
                })
            
            # Ticket Pricing
            if 'wc.ticket.pricing' in env:
                pricings = env['wc.ticket.pricing'].search([])
                print(f"  Unlinking {len(pricings)} ticket pricings...")
                pricings.unlink()
                
            # 2. PURGE MATCHES AND TOURNAEMNTS
            if 'wc.match' in env:
                matches = env['wc.match'].search([])
                print(f"  Unlinking {len(matches)} matches...")
                matches.unlink()
                
            if 'wc.tournament' in env:
                tournaments = env['wc.tournament'].search([])
                print(f"  Unlinking {len(tournaments)} tournaments...")
                tournaments.unlink()
                
            # Delete ir.model.data references for old data to keep Odoo registry clean
            cr.execute("DELETE FROM ir_model_data WHERE model IN ('wc.stadium', 'wc.match', 'wc.tournament')")
            print("  Deleted ir.model.data references.")
            
            # 3. PURGE EXISTING STADIUMS (foreign and small complexes)
            if 'wc.stadium' in env:
                stadiums = env['wc.stadium'].search([])
                print(f"  Unlinking {len(stadiums)} existing stadiums in DB...")
                stadiums.unlink()
                
            # 4. INITIALIZE 2030 TOURNAMENT
            print("Initializing WC-2030 tournament...")
            tournament = env['wc.tournament'].create({
                'key': 'WC-2030',
                'name': 'Coupe du Monde FIFA 2030 - Maroc',
                'year': 2030,
                'host_country': 'Maroc',
                'teams_count': 48,
                'matches_count': 104,
                'goals_count': 0,
                'attendance': 0
            })
            print(f"  Created tournament ID: {tournament.id}")
            
            # 5. INITIALIZE THE 10 MOROCCAN STADIUMS
            print("Creating 10 Moroccan stadiums...")
            created_stadiums = {}
            for std_data in STADIUMS_DATA:
                img_data = download_and_encode_image(std_data.get('image_filename'))
                vals = {
                    'name': std_data['name'],
                    'city': std_data['city'],
                    'capacity': std_data['capacity'],
                    'gross_capacity': std_data['gross_capacity'],
                    'net_capacity': std_data['net_capacity'],
                    'stadium_type': std_data['stadium_type'],
                    'country': std_data['country'],
                    'fifa_code': std_data['fifa_code'],
                    'gps_lat': std_data['gps_lat'],
                    'gps_lng': std_data['gps_lng'],
                    'state': 'ready',
                    'image': img_data
                }
                stadium_rec = env['wc.stadium'].create(vals)
                created_stadiums[std_data['fifa_code']] = stadium_rec
                print(f"  Created stadium '{stadium_rec.name}' (ID: {stadium_rec.id}) as type '{stadium_rec.stadium_type}'")
                
                # Create default zones for match stadiums
                if std_data['stadium_type'] == 'match':
                    for zone_letter in ['A', 'B', 'C', 'D']:
                        env['wc.stadium.zone'].create({
                            'stadium_id': stadium_rec.id,
                            'name': f"Tribune {zone_letter}",
                            'zone_type': 'tribune',
                            'capacity': std_data['capacity'] // 4
                        })
            
            # 6. GENERATE MOCK 2030 MATCHES (Option A)
            print("Generating 2030 mock matches...")
            # We need some national teams. Let's find Morocco, Spain, Portugal, and other top teams from database
            teams = env['wc.team'].search([])
            teams_dict = {t.code_fifa: t for t in teams}
            
            # Add missing core teams if not in database
            core_teams = [
                ('MAR', 'Maroc', 'CAF', 10),
                ('ESP', 'Espagne', 'UEFA', 8),
                ('POR', 'Portugal', 'UEFA', 6),
                ('FRA', 'France', 'UEFA', 2),
                ('ARG', 'Argentine', 'CONMEBOL', 1),
                ('BRA', 'Brésil', 'CONMEBOL', 5),
                ('ENG', 'Angleterre', 'UEFA', 4),
                ('GER', 'Allemagne', 'UEFA', 12)
            ]
            for fifa_code, name, conf, rank in core_teams:
                if fifa_code not in teams_dict:
                    new_team = env['wc.team'].create({
                        'name': name,
                        'code_fifa': fifa_code,
                        'confederation': conf,
                        'fifa_ranking': rank,
                        'lpi_score': 3.5,
                        'lpi_rank': 20
                    })
                    teams_dict[fifa_code] = new_team
                    print(f"  Created missing national team: {name} ({fifa_code})")
            
            # Create some exciting mock matches for 2030
            # Let's map match venues
            venues = [created_stadiums[code] for code in ['CAS', 'TNG', 'RBT', 'FEZ', 'RAK', 'AGA']]
            
            match_fixtures = [
                # Group Stage
                ('Group A', 'MAR', 'POR', venues[0], '2030-06-13 19:00:00', 'planned'),
                ('Group A', 'ESP', 'ARG', venues[1], '2030-06-14 16:00:00', 'planned'),
                ('Group B', 'FRA', 'GER', venues[2], '2030-06-15 15:00:00', 'planned'),
                ('Group B', 'ENG', 'BRA', venues[3], '2030-06-15 20:00:00', 'planned'),
                ('Group C', 'MAR', 'ESP', venues[4], '2030-06-19 20:00:00', 'planned'),
                ('Group C', 'POR', 'ARG', venues[5], '2030-06-20 18:00:00', 'planned'),
                
                # Round of 16
                ('Huitième de finale 1', 'MAR', 'GER', venues[1], '2030-07-06 20:00:00', 'planned'),
                ('Huitième de finale 2', 'FRA', 'POR', venues[2], '2030-07-07 17:00:00', 'planned'),
                
                # Quarter-finals
                ('Quart de finale 1', 'MAR', 'FRA', venues[5], '2030-07-12 20:00:00', 'planned'),
                ('Quart de finale 2', 'ARG', 'ENG', venues[4], '2030-07-13 18:00:00', 'planned'),
                
                # Semi-finals
                ('Demi-finale 1', 'MAR', 'ARG', venues[0], '2030-07-16 20:00:00', 'planned'),
                ('Demi-finale 2', 'ESP', 'POR', venues[1], '2030-07-17 20:00:00', 'planned'),
                
                # Final
                ('Finale', 'MAR', 'ESP', venues[0], '2030-07-21 19:00:00', 'planned')
            ]
            
            for phase, team_a_code, team_b_code, venue, date_str, state in match_fixtures:
                m = env['wc.match'].create({
                    'tournament_id': tournament.id,
                    'team_a_id': teams_dict[team_a_code].id,
                    'team_b_id': teams_dict[team_b_code].id,
                    'stadium_id': venue.id,
                    'date_time': date_str,
                    'phase': 'final' if 'finale' in phase.lower() else 'group',
                    'state': state,
                    'is_historical': False
                })
                # Odoo should trigger its computed display names
                print(f"  Created match: {phase} - {m.name} at {venue.name}")
            
            print("\nDatabase reconstruction completed successfully!")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
