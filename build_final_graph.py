#!/usr/bin/env python3
"""
Build the final interactive network visualization
"""

import json
from pathlib import Path
import networkx as nx
from pyvis.network import Network

CATEGORY_COLORS = {
    'core': '#ff0000',        # Red - Epstein/Maxwell
    'accomplice': '#ff6600',  # Orange
    'victim': '#9900ff',      # Purple
    'political': '#0066ff',   # Blue
    'business': '#00cc00',    # Green
    'legal': '#ffcc00',       # Yellow
    'academic': '#00cccc',    # Cyan
    'entertainment': '#ff66cc', # Pink
    'staff': '#996633',       # Brown
    'journalist': '#66ff66',  # Light green
}

def main():
    print("Loading focused entities...")
    with open('focused_entities.json', 'r') as f:
        data = json.load(f)

    people = data['people']
    print(f"Loaded {len(people)} people")

    # Build NetworkX graph
    G = nx.Graph()

    # Add nodes
    for name, info in people.items():
        G.add_node(name,
                   count=info['count'],
                   category=info['category'],
                   locations=info['locations'],
                   years=info['years'],
                   connections=info['connections'])

    # Add edges from co-occurrences
    for name, info in people.items():
        for conn, weight in info['connections'].items():
            if conn in people and weight >= 1:
                if not G.has_edge(name, conn):
                    G.add_edge(name, conn, weight=weight)

    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

    # Create pyvis network
    net = Network(height='900px', width='100%', bgcolor='#0d1117',
                  font_color='white', directed=False)

    # Configure physics
    net.set_options('''
    {
        "nodes": {
            "font": {
                "size": 16,
                "face": "arial"
            },
            "borderWidth": 2,
            "shadow": true
        },
        "edges": {
            "color": {
                "inherit": false
            },
            "smooth": {
                "type": "continuous"
            },
            "shadow": true
        },
        "physics": {
            "barnesHut": {
                "gravitationalConstant": -8000,
                "centralGravity": 0.5,
                "springLength": 200,
                "springConstant": 0.05,
                "damping": 0.3
            },
            "minVelocity": 0.75
        },
        "interaction": {
            "hover": true,
            "tooltipDelay": 100,
            "hideEdgesOnDrag": true
        }
    }
    ''')

    # Add nodes
    for node in G.nodes():
        info = people[node]
        category = info['category']
        color = CATEGORY_COLORS.get(category, '#888888')
        count = info['count']

        # Size based on document count (log scale for better distribution)
        size = max(20, min(80, 15 + count * 3))

        # Build detailed tooltip
        locations = info.get('locations', {})
        loc_list = [f"{loc} ({cnt})" for loc, cnt in sorted(locations.items(), key=lambda x: -x[1])[:5]]
        loc_str = ', '.join(loc_list) if loc_list else 'Not specified'

        years = info.get('years', {})
        if years:
            year_range = f"{min(years.keys())} - {max(years.keys())}"
        else:
            year_range = 'N/A'

        connections = info.get('connections', {})
        top_conns = [f"{c} ({w})" for c, w in sorted(connections.items(), key=lambda x: -x[1])[:5]]
        conn_str = ', '.join(top_conns) if top_conns else 'None'

        title = f'''<div style="font-family: Arial; padding: 10px; max-width: 300px;">
        <h3 style="margin: 0 0 10px 0; color: {color};">{node}</h3>
        <p><b>Category:</b> {category.title()}</p>
        <p><b>Documents:</b> {count}</p>
        <p><b>Years Active:</b> {year_range}</p>
        <p><b>Locations:</b><br>{loc_str}</p>
        <p><b>Key Connections:</b><br>{conn_str}</p>
        </div>'''

        net.add_node(node, label=node, title=title, color=color, size=size)

    # Add edges
    for u, v, data in G.edges(data=True):
        weight = data.get('weight', 1)
        width = max(1, min(8, weight * 1.5))

        # Color based on connection strength
        if weight >= 5:
            edge_color = 'rgba(255, 100, 100, 0.8)'
        elif weight >= 3:
            edge_color = 'rgba(255, 200, 100, 0.7)'
        else:
            edge_color = 'rgba(150, 150, 150, 0.5)'

        net.add_edge(u, v, width=width, color=edge_color,
                     title=f"{weight} document co-occurrences")

    # Generate HTML
    html = net.generate_html()

    # Add custom legend and title
    custom_html = '''
    <style>
        .legend {
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(13, 17, 23, 0.95);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #30363d;
            z-index: 1000;
            font-family: Arial, sans-serif;
            color: white;
            max-width: 250px;
        }
        .legend h2 {
            margin: 0 0 15px 0;
            font-size: 18px;
            border-bottom: 1px solid #30363d;
            padding-bottom: 10px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin: 8px 0;
            font-size: 13px;
        }
        .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 10px;
            border: 2px solid rgba(255,255,255,0.3);
        }
        .legend-section {
            margin-top: 15px;
            padding-top: 10px;
            border-top: 1px solid #30363d;
            font-size: 12px;
            color: #8b949e;
        }
        .title-bar {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(13, 17, 23, 0.95);
            padding: 15px 25px;
            border-radius: 10px;
            border: 1px solid #30363d;
            z-index: 1000;
            font-family: Arial, sans-serif;
            color: white;
            text-align: right;
        }
        .title-bar h1 {
            margin: 0;
            font-size: 20px;
        }
        .title-bar p {
            margin: 5px 0 0 0;
            color: #8b949e;
            font-size: 12px;
        }
        .timeline-bar {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(13, 17, 23, 0.95);
            padding: 15px 25px;
            border-radius: 10px;
            border: 1px solid #30363d;
            z-index: 1000;
            font-family: Arial, sans-serif;
            color: white;
        }
        .timeline-bar label {
            font-size: 14px;
            margin-right: 15px;
        }
        .timeline-bar input[type="range"] {
            width: 400px;
            cursor: pointer;
        }
        #year-display {
            display: inline-block;
            min-width: 80px;
            text-align: center;
            font-weight: bold;
        }
    </style>

    <div class="legend">
        <h2>Epstein Network</h2>
        <div class="legend-item"><div class="legend-color" style="background: #ff0000;"></div> Core (Epstein/Maxwell)</div>
        <div class="legend-item"><div class="legend-color" style="background: #ff6600;"></div> Accomplices</div>
        <div class="legend-item"><div class="legend-color" style="background: #9900ff;"></div> Victims</div>
        <div class="legend-item"><div class="legend-color" style="background: #0066ff;"></div> Political Figures</div>
        <div class="legend-item"><div class="legend-color" style="background: #00cc00;"></div> Business/Finance</div>
        <div class="legend-item"><div class="legend-color" style="background: #ffcc00;"></div> Legal</div>
        <div class="legend-item"><div class="legend-color" style="background: #00cccc;"></div> Academic/Science</div>
        <div class="legend-item"><div class="legend-color" style="background: #ff66cc;"></div> Entertainment</div>
        <div class="legend-item"><div class="legend-color" style="background: #996633;"></div> Staff</div>
        <div class="legend-item"><div class="legend-color" style="background: #66ff66;"></div> Journalists</div>
        <div class="legend-section">
            <p>• Node size = document count</p>
            <p>• Edge thickness = co-occurrences</p>
            <p>• Click nodes for details</p>
            <p>• Drag to rearrange</p>
        </div>
    </div>

    <div class="title-bar">
        <h1>Jeffrey Epstein Document Network</h1>
        <p>Based on ''' + str(data.get('total_documents', 8531)) + ''' FOIA documents</p>
        <p>Extracted ''' + str(len(people)) + ''' key individuals</p>
    </div>
    '''

    # Insert custom HTML before closing body
    html = html.replace('</body>', custom_html + '</body>')

    # Save
    output_file = 'epstein_network_final.html'
    with open(output_file, 'w') as f:
        f.write(html)

    print(f"\nSaved visualization to {output_file}")

    # Print network stats
    print("\n=== Network Statistics ===")
    print(f"Nodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")
    print(f"Density: {nx.density(G):.3f}")

    print("\n=== Centrality Rankings ===")
    degree_cent = nx.degree_centrality(G)
    sorted_cent = sorted(degree_cent.items(), key=lambda x: -x[1])
    for name, cent in sorted_cent[:10]:
        cat = people[name]['category']
        print(f"  {name} ({cat}): {cent:.3f}")

    # Find key connectors (betweenness centrality)
    if G.number_of_edges() > 0:
        betweenness = nx.betweenness_centrality(G)
        print("\n=== Key Connectors (Betweenness) ===")
        sorted_between = sorted(betweenness.items(), key=lambda x: -x[1])
        for name, cent in sorted_between[:5]:
            if cent > 0:
                cat = people[name]['category']
                print(f"  {name} ({cat}): {cent:.3f}")

if __name__ == '__main__':
    main()
