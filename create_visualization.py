#!/usr/bin/env python3
"""
Create interactive network visualization of Epstein document relationships
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
from pyvis.network import Network
import pandas as pd

# List of KNOWN notable people to include (verified names)
KNOWN_NOTABLE = {
    # Core case figures
    'jeffrey epstein', 'jeffrey e. epstein', 'ghislaine maxwell',
    'jean luc brunel', 'jean luc', 'sarah kellen', 'nadia marcinkova',
    'lesley groff', 'adriana ross',

    # Victims/witnesses
    'virginia giuffre', 'virginia roberts', 'courtney wild',
    'annie farmer', 'maria farmer', 'carolyn', 'johanna sjoberg',

    # Legal
    'alan dershowitz', 'kenneth starr', 'jay lefkowitz',
    'brad edwards', 'david boies',

    # Rich/Powerful connections
    'bill clinton', 'donald trump', 'prince andrew',
    'prince andrew duke of york', 'les wexner', 'leslie wexner',
    'leon black', 'glenn dubin', 'eva andersson-dubin',
    'mort zuckerman', 'mortimer zuckerman', 'tom pritzker',
    'reid hoffman', 'bill gates', 'jes staley', 'james staley',
    'ehud barak',

    # Scientists/Academics
    'stephen hawking', 'marvin minsky', 'george church',
    'lawrence krauss', 'steven pinker', 'joi ito',

    # Entertainment/Media
    'woody allen', 'kevin spacey', 'chris tucker', 'naomi campbell',
    'david copperfield',

    # Employees/Staff
    'juan alessi', 'alfredo rodriguez', 'tony figueroa',
    'cathy alexander', 'janusz banasiak',

    # Investigators/Officials
    'alexander acosta', 'marie villafana',
}

# Patterns that indicate noise/redactions
NOISE_PATTERNS = [
    r'^b\d', r'^b5', r'^b6', r'^b7', r'^\d+$',
    r'automated', r'marital status', r'victim specialist',
    r'appearance date', r'birth date', r'suite', r'mobile',
    r'photo lineup', r'wolf camera', r'foley square',
    r'galerie', r'serial', r'camera', r'ted conference',
    r'far east', r'fat', r'^st\s', r'zorro', r'trop',
    r'clinton morroco', r'clinton fat', r'london clinton',
]

def is_noise(name):
    """Check if a name is noise/redaction"""
    name_lower = name.lower()
    for pattern in NOISE_PATTERNS:
        if re.search(pattern, name_lower):
            return True
    # Too short
    if len(name) < 5:
        return True
    # All numbers or special chars
    if re.match(r'^[\d\s\-.,]+$', name):
        return True
    return False

def is_notable(name):
    """Check if person is in our notable list"""
    name_lower = name.lower()
    for notable in KNOWN_NOTABLE:
        if notable in name_lower or name_lower in notable:
            return True
    return False

def normalize_name(name):
    """Normalize name variations"""
    name_lower = name.lower().strip()

    # Common variations
    variations = {
        'jeffrey e. epstein': 'Jeffrey Epstein',
        'jeffrey epstein': 'Jeffrey Epstein',
        "jeffrey epstein's": 'Jeffrey Epstein',
        'jeffrey \nepstein': 'Jeffrey Epstein',
        'ghislaine maxwell': 'Ghislaine Maxwell',
        'g. maxwell': 'Ghislaine Maxwell',
        'jean luc brunel': 'Jean-Luc Brunel',
        'jean luc': 'Jean-Luc Brunel',
        'jean luc 2': 'Jean-Luc Brunel',
        'virginia giuffre': 'Virginia Giuffre',
        'virginia roberts': 'Virginia Giuffre',
        'prince andrew duke of york': 'Prince Andrew',
        'prince andrew': 'Prince Andrew',
        'les wexner': 'Les Wexner',
        'leslie wexner': 'Les Wexner',
        'alan dershowitz': 'Alan Dershowitz',
        'bill clinton': 'Bill Clinton',
        'donald trump': 'Donald Trump',
        'bill gates': 'Bill Gates',
        'mort zuckerman': 'Mortimer Zuckerman',
        'mortimer zuckerman': 'Mortimer Zuckerman',
        'leon black': 'Leon Black',
        'glenn dubin': 'Glenn Dubin',
        'eva andersson-dubin': 'Eva Dubin',
        'sarah kellen': 'Sarah Kellen',
        'nadia marcinkova': 'Nadia Marcinkova',
        'lesley groff': 'Lesley Groff',
        'brad edwards': 'Brad Edwards',
        'ehud barak': 'Ehud Barak',
        'stephen hawking': 'Stephen Hawking',
        'marvin minsky': 'Marvin Minsky',
        'lawrence krauss': 'Lawrence Krauss',
        'david copperfield': 'David Copperfield',
        'chris tucker': 'Chris Tucker',
        'naomi campbell': 'Naomi Campbell',
        'kevin spacey': 'Kevin Spacey',
        'woody allen': 'Woody Allen',
        'kenneth starr': 'Kenneth Starr',
        'reid hoffman': 'Reid Hoffman',
        'jes staley': 'Jes Staley',
        'james staley': 'Jes Staley',
        'miami herald': 'Miami Herald',  # This is an organization, filter it
        'richard taus': 'Richard Taus',
    }

    return variations.get(name_lower, name.title())

# Node categories for coloring
CATEGORIES = {
    'core': ['Jeffrey Epstein', 'Ghislaine Maxwell'],
    'accomplice': ['Sarah Kellen', 'Nadia Marcinkova', 'Lesley Groff',
                   'Jean-Luc Brunel', 'Adriana Ross'],
    'victim': ['Virginia Giuffre', 'Courtney Wild', 'Annie Farmer',
               'Maria Farmer', 'Carolyn', 'Johanna Sjoberg'],
    'political': ['Bill Clinton', 'Donald Trump', 'Prince Andrew', 'Ehud Barak'],
    'business': ['Les Wexner', 'Leon Black', 'Glenn Dubin', 'Mortimer Zuckerman',
                 'Bill Gates', 'Reid Hoffman', 'Jes Staley', 'Tom Pritzker'],
    'legal': ['Alan Dershowitz', 'Kenneth Starr', 'Brad Edwards', 'David Boies'],
    'academic': ['Stephen Hawking', 'Marvin Minsky', 'Lawrence Krauss',
                 'George Church', 'Steven Pinker', 'Joi Ito'],
    'entertainment': ['David Copperfield', 'Chris Tucker', 'Naomi Campbell',
                      'Kevin Spacey', 'Woody Allen'],
}

CATEGORY_COLORS = {
    'core': '#ff0000',       # Red
    'accomplice': '#ff6600', # Orange
    'victim': '#9900ff',     # Purple
    'political': '#0066ff',  # Blue
    'business': '#00cc00',   # Green
    'legal': '#ffcc00',      # Yellow
    'academic': '#00cccc',   # Cyan
    'entertainment': '#ff66cc', # Pink
    'other': '#888888',      # Gray
}

def get_category(name):
    """Get the category of a person"""
    for cat, members in CATEGORIES.items():
        if name in members:
            return cat
    return 'other'

def main():
    print("Loading extracted entities...")
    with open('extracted_entities.json', 'r') as f:
        data = json.load(f)

    people_data = data['people']

    # Filter and normalize people
    filtered_people = {}
    name_mapping = {}  # original -> normalized

    for name, info in people_data.items():
        if is_noise(name):
            continue

        normalized = normalize_name(name)

        # Skip organizations mistakenly classified as people
        if normalized in ['Miami Herald', 'FBI', 'DOJ']:
            continue

        # Merge with existing if normalized name already exists
        if normalized in filtered_people:
            existing = filtered_people[normalized]
            existing['count'] += info['count']
            # Merge connections
            for conn, cnt in info.get('connections', {}).items():
                if not is_noise(conn):
                    conn_norm = normalize_name(conn)
                    if conn_norm not in ['Miami Herald', 'FBI', 'DOJ']:
                        existing['connections'][conn_norm] = existing['connections'].get(conn_norm, 0) + cnt
            # Merge locations
            for loc, cnt in info.get('locations', {}).items():
                existing['locations'][loc] = existing['locations'].get(loc, 0) + cnt
        else:
            # Filter connections to remove noise
            clean_connections = {}
            for conn, cnt in info.get('connections', {}).items():
                if not is_noise(conn):
                    conn_norm = normalize_name(conn)
                    if conn_norm not in ['Miami Herald', 'FBI', 'DOJ']:
                        clean_connections[conn_norm] = clean_connections.get(conn_norm, 0) + cnt

            filtered_people[normalized] = {
                'count': info['count'],
                'is_notable': info.get('is_notable', False) or is_notable(name),
                'connections': clean_connections,
                'locations': info.get('locations', {}),
                'date_range': info.get('date_range'),
            }

        name_mapping[name] = normalized

    print(f"Filtered to {len(filtered_people)} clean people records")

    # Build the network
    G = nx.Graph()

    # Add nodes
    for name, info in filtered_people.items():
        # Only include people with connections or notable status
        if info['connections'] or info['is_notable'] or info['count'] >= 5:
            category = get_category(name)
            G.add_node(name,
                       count=info['count'],
                       category=category,
                       locations=list(info.get('locations', {}).keys())[:5],
                       date_range=info.get('date_range'))

    # Add edges based on co-occurrence
    for name, info in filtered_people.items():
        if name not in G.nodes():
            continue
        for conn, weight in info['connections'].items():
            if conn in G.nodes() and weight >= 2:  # At least 2 co-occurrences
                if G.has_edge(name, conn):
                    G[name][conn]['weight'] += weight
                else:
                    G.add_edge(name, conn, weight=weight)

    # Remove isolated nodes
    isolated = list(nx.isolates(G))
    G.remove_nodes_from(isolated)

    print(f"Network has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

    # Create interactive visualization with pyvis
    net = Network(height='900px', width='100%', bgcolor='#1a1a2e',
                  font_color='white', directed=False)

    # Physics settings for better layout
    net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=150)

    # Add nodes with styling
    for node in G.nodes():
        info = filtered_people.get(node, {})
        category = get_category(node)
        color = CATEGORY_COLORS.get(category, '#888888')

        # Size based on mention count
        count = info.get('count', 1)
        size = min(50, max(15, 10 + count * 0.5))

        # Build tooltip
        locations = info.get('locations', {})
        top_locs = sorted(locations.items(), key=lambda x: -x[1])[:3]
        loc_str = ', '.join([f"{l}" for l, c in top_locs]) if top_locs else 'Unknown'

        date_range = info.get('date_range')
        date_str = ''
        if date_range:
            date_str = f"\nDate range: {date_range.get('earliest', 'N/A')[:10]} to {date_range.get('latest', 'N/A')[:10]}"

        title = f"<b>{node}</b><br>Category: {category.title()}<br>Mentions: {count}<br>Locations: {loc_str}{date_str}"

        net.add_node(node, label=node, title=title, color=color, size=size,
                     borderWidth=2, borderWidthSelected=4)

    # Add edges with styling
    for u, v, data in G.edges(data=True):
        weight = data.get('weight', 1)
        width = min(10, max(1, weight * 0.3))
        net.add_edge(u, v, width=width, color='rgba(150,150,150,0.5)',
                     title=f"{weight} co-occurrences")

    # Add legend as HTML
    legend_html = '''
    <div style="position: fixed; top: 10px; left: 10px; background: rgba(0,0,0,0.8);
                padding: 15px; border-radius: 10px; z-index: 1000; color: white; font-family: Arial;">
        <h3 style="margin-top: 0;">Epstein Network</h3>
        <p style="font-size: 12px; margin: 5px 0;"><span style="color: #ff0000;">●</span> Core (Epstein/Maxwell)</p>
        <p style="font-size: 12px; margin: 5px 0;"><span style="color: #ff6600;">●</span> Accomplices</p>
        <p style="font-size: 12px; margin: 5px 0;"><span style="color: #9900ff;">●</span> Victims</p>
        <p style="font-size: 12px; margin: 5px 0;"><span style="color: #0066ff;">●</span> Political Figures</p>
        <p style="font-size: 12px; margin: 5px 0;"><span style="color: #00cc00;">●</span> Business/Finance</p>
        <p style="font-size: 12px; margin: 5px 0;"><span style="color: #ffcc00;">●</span> Legal</p>
        <p style="font-size: 12px; margin: 5px 0;"><span style="color: #00cccc;">●</span> Academic/Science</p>
        <p style="font-size: 12px; margin: 5px 0;"><span style="color: #ff66cc;">●</span> Entertainment</p>
        <p style="font-size: 12px; margin: 5px 0;"><span style="color: #888888;">●</span> Other</p>
        <hr>
        <p style="font-size: 11px;">Node size = mention frequency</p>
        <p style="font-size: 11px;">Edge thickness = co-occurrence count</p>
        <p style="font-size: 11px;">Click nodes to see details</p>
    </div>
    '''

    # Save the network
    output_file = 'epstein_network.html'
    net.save_graph(output_file)

    # Inject the legend
    with open(output_file, 'r') as f:
        html = f.read()

    # Insert legend before closing body tag
    html = html.replace('</body>', legend_html + '</body>')

    with open(output_file, 'w') as f:
        f.write(html)

    print(f"\nSaved interactive visualization to {output_file}")

    # Also save summary stats
    stats = {
        'total_nodes': G.number_of_nodes(),
        'total_edges': G.number_of_edges(),
        'top_connected': sorted(
            [(n, G.degree(n)) for n in G.nodes()],
            key=lambda x: -x[1]
        )[:20],
        'categories': {cat: len([n for n in G.nodes() if get_category(n) == cat])
                      for cat in CATEGORY_COLORS.keys()},
    }

    with open('network_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)

    print("\n=== Top 20 Most Connected People ===")
    for name, degree in stats['top_connected']:
        cat = get_category(name)
        print(f"  {name}: {degree} connections ({cat})")

    print("\n=== Category Breakdown ===")
    for cat, count in stats['categories'].items():
        if count > 0:
            print(f"  {cat}: {count}")

if __name__ == '__main__':
    main()
