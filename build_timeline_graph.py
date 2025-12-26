#!/usr/bin/env python3
"""
Build interactive network visualization with time slider
"""

import json
from pathlib import Path

# Special Wikipedia URLs for disambiguation and corrections
WIKI_OVERRIDES = {
    # Core figures
    'Jeffrey Epstein': 'https://en.wikipedia.org/wiki/Jeffrey_Epstein',
    'Ghislaine Maxwell': 'https://en.wikipedia.org/wiki/Ghislaine_Maxwell',

    # Political figures
    'Prince Andrew': 'https://en.wikipedia.org/wiki/Prince_Andrew,_Duke_of_York',
    'Bill Clinton': 'https://en.wikipedia.org/wiki/Bill_Clinton',
    'Donald Trump': 'https://en.wikipedia.org/wiki/Donald_Trump',
    'Joe Biden': 'https://en.wikipedia.org/wiki/Joe_Biden',
    'Robert Mueller': 'https://en.wikipedia.org/wiki/Robert_Mueller',

    # Victims
    'Virginia Giuffre': 'https://en.wikipedia.org/wiki/Virginia_Giuffre',
    'Jane Doe': 'https://en.wikipedia.org/wiki/Jane_Doe_(pseudonym)',
    'Jane Doe (Various)': 'https://en.wikipedia.org/wiki/Litigation_involving_Jeffrey_Epstein',

    # Associates/Accomplices
    'Jean-Luc Brunel': 'https://en.wikipedia.org/wiki/Jean-Luc_Brunel',
    'Sarah Kellen': 'https://en.wikipedia.org/wiki/Sarah_Kellen',
    'Lesley Groff': 'https://en.wikipedia.org/wiki/Litigation_involving_Jeffrey_Epstein',
    'Glenn Dubin': 'https://en.wikipedia.org/wiki/Glenn_Dubin',
    'Stan Pottinger': 'https://en.wikipedia.org/wiki/John_Stanley_Pottinger',
    'Juanesteban Ganoza': None,  # No Wikipedia page

    # Family
    'Mark Epstein': 'https://en.wikipedia.org/wiki/Jeffrey_Epstein#Family_and_early_life',
    'Isabel Maxwell': 'https://en.wikipedia.org/wiki/Isabel_Maxwell',

    # Business
    'Leslie Wexner': 'https://en.wikipedia.org/wiki/Les_Wexner',
    'Deutsche Bank': 'https://en.wikipedia.org/wiki/Deutsche_Bank',

    # Entertainment
    'Naomi Campbell': 'https://en.wikipedia.org/wiki/Naomi_Campbell',
    'David Copperfield': 'https://en.wikipedia.org/wiki/David_Copperfield_(illusionist)',

    # Legal - Epstein/Maxwell Defense
    'Roy Black': 'https://en.wikipedia.org/wiki/Roy_Black_(attorney)',
    'Jay Lefkowitz': 'https://en.wikipedia.org/wiki/Jay_Lefkowitz',
    'Ken Starr': 'https://en.wikipedia.org/wiki/Ken_Starr',
    'Alan Dershowitz': 'https://en.wikipedia.org/wiki/Alan_Dershowitz',
    'Martin Weinberg': 'https://en.wikipedia.org/wiki/Litigation_involving_Jeffrey_Epstein',
    'Reid Weingarten': 'https://en.wikipedia.org/wiki/Litigation_involving_Jeffrey_Epstein',
    'Mark Cohen': 'https://en.wikipedia.org/wiki/Litigation_involving_Jeffrey_Epstein',
    'Laura Menninger': 'https://en.wikipedia.org/wiki/Litigation_involving_Jeffrey_Epstein',
    'Jeff Pagliuca': 'https://en.wikipedia.org/wiki/Litigation_involving_Jeffrey_Epstein',
    'Christian Everdell': 'https://en.wikipedia.org/wiki/Litigation_involving_Jeffrey_Epstein',
    'Bobbi Sternheim': 'https://en.wikipedia.org/wiki/Litigation_involving_Jeffrey_Epstein',

    # Legal - Prosecutors/Judges
    'Alexander Acosta': 'https://en.wikipedia.org/wiki/Alexander_Acosta',
    'Judge Berman': 'https://en.wikipedia.org/wiki/Richard_M._Berman',
    'Alison Nathan': 'https://en.wikipedia.org/wiki/Alison_Nathan',
    'Audrey Strauss': 'https://en.wikipedia.org/wiki/Audrey_Strauss',
    'Barry Krischer': 'https://en.wikipedia.org/wiki/Jeffrey_Epstein#Criminal_proceedings_in_Florida',

    # Legal - Victims' Attorneys
    'Gloria Allred': 'https://en.wikipedia.org/wiki/Gloria_Allred',
    'David Boies': 'https://en.wikipedia.org/wiki/David_Boies',
    'Brad Edwards': 'https://en.wikipedia.org/wiki/Bradley_Edwards_(attorney)',
    'Sigrid McCawley': 'https://en.wikipedia.org/wiki/Litigation_involving_Jeffrey_Epstein',
    'Paul Cassell': 'https://en.wikipedia.org/wiki/Paul_Cassell',
    'Roberta Kaplan': 'https://en.wikipedia.org/wiki/Robbie_Kaplan',
    'Jack Scarola': 'https://en.wikipedia.org/wiki/Litigation_involving_Jeffrey_Epstein',
    'Bruce Barket': 'https://en.wikipedia.org/wiki/Litigation_involving_Jeffrey_Epstein',

    # Academic/Tech
    'Joi Ito': 'https://en.wikipedia.org/wiki/Joi_Ito',

    # Journalists
    'Julie K. Brown': 'https://en.wikipedia.org/wiki/Julie_K._Brown',
}

CATEGORY_COLORS = {
    'core': '#ff0000',
    'accomplice': '#ff6600',
    'victim': '#9900ff',
    'political': '#0066ff',
    'business': '#00cc00',
    'legal': '#ffcc00',
    'academic': '#00cccc',
    'entertainment': '#ff66cc',
    'staff': '#996633',
    'journalist': '#66ff66',
    'family': '#ff9933',
    'associate': '#cc66ff',
    'financial': '#33cc99',
}

# Light colors need black text, dark colors need white text
FONT_COLORS = {
    'core': 'white',
    'accomplice': 'black',
    'victim': 'white',
    'political': 'white',
    'business': 'black',
    'legal': 'black',
    'academic': 'black',
    'entertainment': 'black',
    'staff': 'white',
    'journalist': 'black',
    'family': 'black',
    'associate': 'black',
    'financial': 'black',
}

def main():
    print("Loading focused entities...")
    with open('focused_entities.json', 'r') as f:
        data = json.load(f)

    people = data['people']
    print(f"Loaded {len(people)} people")

    # Build nodes and edges data for JavaScript
    nodes = []
    edges = []
    edge_set = set()

    for name, info in people.items():
        category = info['category']
        color = CATEGORY_COLORS.get(category, '#888888')
        font_color = FONT_COLORS.get(category, 'white')
        count = info['count']
        size = max(20, min(80, 15 + count * 3))

        # Get years this person appears in
        years = [int(y) for y in info.get('years', {}).keys()]
        if not years:
            years = [2000, 2005, 2010, 2015, 2020]  # Default range if no years found

        locations = info.get('locations', {})
        loc_list = [f"{loc} ({cnt})" for loc, cnt in sorted(locations.items(), key=lambda x: -x[1])[:5]]
        loc_str = ', '.join(loc_list) if loc_list else 'Not specified'

        connections = info.get('connections', {})
        top_conns = [f"{c} ({w})" for c, w in sorted(connections.items(), key=lambda x: -x[1])[:5]]
        conn_str = ', '.join(top_conns) if top_conns else 'None'

        year_range = f"{min(years)} - {max(years)}" if years else 'N/A'
        role = info.get('role', '')
        role_line = f"\nRole: {role}" if role else ""

        # Plain text tooltip (vis-network doesn't render HTML by default)
        title_text = f"""{name}
━━━━━━━━━━━━━━━━━━━━
Category: {category.title()}{role_line}
Documents: {count}
Years Active: {year_range}
Locations: {loc_str}
Key Connections: {conn_str}"""

        # Generate Wikipedia URL (use override if available)
        if name in WIKI_OVERRIDES:
            wiki_url = WIKI_OVERRIDES[name]  # May be None for no Wikipedia page
        else:
            wiki_name = name.replace(' ', '_')
            wiki_url = f"https://en.wikipedia.org/wiki/{wiki_name}"

        nodes.append({
            'id': name,
            'label': name,
            'color': color,
            'font': {'color': font_color},
            'size': size,
            'category': category,
            'years': years,
            'minYear': min(years),
            'maxYear': max(years),
            'title': title_text,
            'wikiUrl': wiki_url
        })

        # Add edges
        for conn, weight in connections.items():
            if conn in people:
                edge_key = tuple(sorted([name, conn]))
                if edge_key not in edge_set:
                    edge_set.add(edge_key)
                    width = max(1, min(8, weight * 1.5))
                    if weight >= 5:
                        edge_color = 'rgba(255, 100, 100, 0.8)'
                    elif weight >= 3:
                        edge_color = 'rgba(255, 200, 100, 0.7)'
                    else:
                        edge_color = 'rgba(150, 150, 150, 0.5)'

                    # Get overlapping years for this edge
                    conn_years = [int(y) for y in people[conn].get('years', {}).keys()]
                    if not conn_years:
                        conn_years = [2000, 2005, 2010, 2015, 2020]
                    overlap_years = list(set(years) & set(conn_years))
                    if not overlap_years:
                        overlap_years = list(set(years) | set(conn_years))

                    edge_id = f"{name}--{conn}"
                    edges.append({
                        'id': edge_id,
                        'from': name,
                        'to': conn,
                        'width': width,
                        'color': edge_color,
                        'weight': weight,
                        'years': overlap_years,
                        'minYear': min(overlap_years),
                        'maxYear': max(overlap_years),
                        'title': f"{weight} document co-occurrences"
                    })

    print(f"Built {len(nodes)} nodes and {len(edges)} edges")

    # Find year range
    all_years = []
    for node in nodes:
        all_years.extend(node['years'])
    min_year = min(all_years) if all_years else 1990
    max_year = max(all_years) if all_years else 2024

    print(f"Year range: {min_year} - {max_year}")

    # Generate HTML with embedded JavaScript
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Epstein Network - Timeline View</title>
    <script src="vis-network.min.js"></script>
    <link href="vis-network.min.css" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: Arial, sans-serif;
            background: #0d1117;
            color: white;
            overflow: hidden;
        }}
        #network {{
            width: 100%;
            height: 100vh;
        }}
        .legend {{
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(13, 17, 23, 0.95);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #30363d;
            z-index: 1000;
            max-width: 220px;
        }}
        .legend h2 {{
            margin: 0 0 15px 0;
            font-size: 18px;
            border-bottom: 1px solid #30363d;
            padding-bottom: 10px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 6px 0;
            font-size: 12px;
        }}
        .legend-color {{
            width: 14px;
            height: 14px;
            border-radius: 50%;
            margin-right: 8px;
            border: 2px solid rgba(255,255,255,0.3);
        }}
        .legend-section {{
            margin-top: 12px;
            padding-top: 10px;
            border-top: 1px solid #30363d;
            font-size: 11px;
            color: #8b949e;
        }}
        .title-bar {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(13, 17, 23, 0.95);
            padding: 15px 25px;
            border-radius: 10px;
            border: 1px solid #30363d;
            z-index: 1000;
            text-align: right;
        }}
        .title-bar h1 {{
            font-size: 20px;
            margin-bottom: 5px;
        }}
        .title-bar p {{
            color: #8b949e;
            font-size: 12px;
        }}
        .timeline-control {{
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(13, 17, 23, 0.95);
            padding: 20px 40px;
            border-radius: 15px;
            border: 1px solid #30363d;
            z-index: 1000;
            text-align: center;
            min-width: 600px;
        }}
        .timeline-control h3 {{
            margin-bottom: 15px;
            font-size: 16px;
        }}
        .slider-container {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        .year-display {{
            font-size: 32px;
            font-weight: bold;
            color: #58a6ff;
            min-width: 100px;
        }}
        input[type="range"] {{
            -webkit-appearance: none;
            width: 350px;
            height: 8px;
            background: #30363d;
            border-radius: 4px;
            outline: none;
        }}
        input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 24px;
            height: 24px;
            background: #58a6ff;
            border-radius: 50%;
            cursor: pointer;
            border: 3px solid white;
        }}
        input[type="range"]::-moz-range-thumb {{
            width: 24px;
            height: 24px;
            background: #58a6ff;
            border-radius: 50%;
            cursor: pointer;
            border: 3px solid white;
        }}
        .controls {{
            margin-top: 15px;
            display: flex;
            justify-content: center;
            gap: 10px;
        }}
        button {{
            background: #238636;
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }}
        button:hover {{
            background: #2ea043;
        }}
        button.secondary {{
            background: #30363d;
        }}
        button.secondary:hover {{
            background: #484f58;
        }}
        .stats {{
            margin-top: 10px;
            font-size: 12px;
            color: #8b949e;
        }}
        .mode-toggle {{
            position: fixed;
            bottom: 160px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(13, 17, 23, 0.95);
            padding: 10px 20px;
            border-radius: 8px;
            border: 1px solid #30363d;
            z-index: 1000;
            color: white;
        }}
        .mode-toggle label {{
            margin-right: 15px;
            cursor: pointer;
            color: white;
            font-size: 14px;
        }}
        .mode-toggle input {{
            margin-right: 5px;
            accent-color: #58a6ff;
        }}
    </style>
</head>
<body>
    <div id="network"></div>

    <div class="legend">
        <h2>Epstein Network</h2>
        <div class="legend-item"><div class="legend-color" style="background: #ff0000;"></div> Core</div>
        <div class="legend-item"><div class="legend-color" style="background: #ff6600;"></div> Accomplices</div>
        <div class="legend-item"><div class="legend-color" style="background: #ff9933;"></div> Family</div>
        <div class="legend-item"><div class="legend-color" style="background: #9900ff;"></div> Victims</div>
        <div class="legend-item"><div class="legend-color" style="background: #0066ff;"></div> Political</div>
        <div class="legend-item"><div class="legend-color" style="background: #00cc00;"></div> Business</div>
        <div class="legend-item"><div class="legend-color" style="background: #33cc99;"></div> Financial</div>
        <div class="legend-item"><div class="legend-color" style="background: #ffcc00;"></div> Legal</div>
        <div class="legend-item"><div class="legend-color" style="background: #cc66ff;"></div> Associates</div>
        <div class="legend-item"><div class="legend-color" style="background: #00cccc;"></div> Academic</div>
        <div class="legend-item"><div class="legend-color" style="background: #ff66cc;"></div> Entertainment</div>
        <div class="legend-item"><div class="legend-color" style="background: #996633;"></div> Staff</div>
        <div class="legend-item"><div class="legend-color" style="background: #66ff66;"></div> Journalists</div>
        <div class="legend-section">
            <p>Node size = mentions</p>
            <p>Edge width = co-occurrences</p>
            <p style="color: #58a6ff; margin-top: 8px;">Click any node to open Wikipedia</p>
        </div>
    </div>

    <div class="title-bar">
        <h1>Jeffrey Epstein Document Network</h1>
        <p>Based on {data.get('total_documents', 19154):,} FOIA documents</p>
        <p id="visible-count">Showing all {len(nodes)} individuals</p>
    </div>

    <div class="mode-toggle">
        <label><input type="radio" name="mode" value="cumulative" checked> Cumulative (up to year)</label>
        <label><input type="radio" name="mode" value="exact"> Exact year only</label>
        <label><input type="radio" name="mode" value="all"> Show all</label>
    </div>

    <div class="timeline-control">
        <h3>Timeline Filter</h3>
        <div class="slider-container">
            <span>{min_year}</span>
            <input type="range" id="yearSlider" min="{min_year}" max="{max_year}" value="{max_year}">
            <span>{max_year}</span>
            <div class="year-display" id="yearDisplay">{max_year}</div>
        </div>
        <div class="controls">
            <button id="playBtn">Play Timeline</button>
            <button class="secondary" id="resetBtn">Reset</button>
        </div>
        <div class="stats" id="statsDisplay">
            Visible: {len(nodes)} people, {len(edges)} connections
        </div>
    </div>

    <script>
        // Data
        const allNodes = {json.dumps(nodes)};
        const allEdges = {json.dumps(edges)};

        // Create datasets
        const nodesDataset = new vis.DataSet(allNodes);
        const edgesDataset = new vis.DataSet(allEdges);

        // Create network
        const container = document.getElementById('network');
        const data = {{ nodes: nodesDataset, edges: edgesDataset }};
        const options = {{
            nodes: {{
                font: {{ size: 14, color: 'white', face: 'arial' }},
                borderWidth: 2,
                shadow: true
            }},
            edges: {{
                smooth: {{ type: 'continuous' }},
                shadow: true
            }},
            physics: {{
                barnesHut: {{
                    gravitationalConstant: -8000,
                    centralGravity: 0.5,
                    springLength: 200,
                    springConstant: 0.05,
                    damping: 0.3
                }},
                minVelocity: 0.75
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 100
            }}
        }};

        const network = new vis.Network(container, data, options);

        // Timeline controls
        const slider = document.getElementById('yearSlider');
        const yearDisplay = document.getElementById('yearDisplay');
        const statsDisplay = document.getElementById('statsDisplay');
        const visibleCount = document.getElementById('visible-count');
        const playBtn = document.getElementById('playBtn');
        const resetBtn = document.getElementById('resetBtn');

        let mode = 'cumulative';
        let isPlaying = false;
        let playInterval = null;

        // Mode toggle
        document.querySelectorAll('input[name="mode"]').forEach(radio => {{
            radio.addEventListener('change', (e) => {{
                mode = e.target.value;
                filterByYear(parseInt(slider.value));
            }});
        }});

        function filterByYear(year) {{
            yearDisplay.textContent = year;

            let visibleNodes = 0;
            let visibleEdges = 0;

            // Update nodes
            allNodes.forEach(node => {{
                let visible = false;

                if (mode === 'all') {{
                    visible = true;
                }} else if (mode === 'cumulative') {{
                    visible = node.minYear <= year;
                }} else {{ // exact
                    visible = node.years.includes(year);
                }}

                nodesDataset.update({{
                    id: node.id,
                    hidden: !visible,
                    physics: visible
                }});

                if (visible) visibleNodes++;
            }});

            // Update edges
            allEdges.forEach(edge => {{
                let visible = false;

                if (mode === 'all') {{
                    visible = true;
                }} else if (mode === 'cumulative') {{
                    visible = edge.minYear <= year;
                }} else {{
                    visible = edge.years.includes(year);
                }}

                // Also check if both connected nodes are visible
                const fromNode = nodesDataset.get(edge.from);
                const toNode = nodesDataset.get(edge.to);
                visible = visible && !fromNode.hidden && !toNode.hidden;

                edgesDataset.update({{
                    id: edge.id,
                    hidden: !visible
                }});

                if (visible) visibleEdges++;
            }});

            statsDisplay.textContent = `Visible: ${{visibleNodes}} people, ${{visibleEdges}} connections`;
            visibleCount.textContent = `Showing ${{visibleNodes}} individuals`;
        }}

        // Slider event
        slider.addEventListener('input', (e) => {{
            filterByYear(parseInt(e.target.value));
        }});

        // Play button
        playBtn.addEventListener('click', () => {{
            if (isPlaying) {{
                clearInterval(playInterval);
                playBtn.textContent = 'Play Timeline';
                isPlaying = false;
            }} else {{
                slider.value = {min_year};
                filterByYear({min_year});
                isPlaying = true;
                playBtn.textContent = 'Stop';

                playInterval = setInterval(() => {{
                    let currentYear = parseInt(slider.value);
                    if (currentYear >= {max_year}) {{
                        clearInterval(playInterval);
                        playBtn.textContent = 'Play Timeline';
                        isPlaying = false;
                    }} else {{
                        slider.value = currentYear + 1;
                        filterByYear(currentYear + 1);
                    }}
                }}, 800);
            }}
        }});

        // Reset button
        resetBtn.addEventListener('click', () => {{
            if (isPlaying) {{
                clearInterval(playInterval);
                playBtn.textContent = 'Play Timeline';
                isPlaying = false;
            }}
            slider.value = {max_year};
            document.querySelector('input[value="cumulative"]').checked = true;
            mode = 'cumulative';
            filterByYear({max_year});
        }});

        // Initialize
        filterByYear({max_year});

        // Click handler for Wikipedia links
        network.on('click', function(params) {{
            if (params.nodes.length > 0) {{
                const nodeId = params.nodes[0];
                const node = allNodes.find(n => n.id === nodeId);
                if (node && node.wikiUrl) {{
                    window.open(node.wikiUrl, '_blank');
                }}
            }}
        }});

        // Change cursor on hover
        network.on('hoverNode', function() {{
            container.style.cursor = 'pointer';
        }});
        network.on('blurNode', function() {{
            container.style.cursor = 'default';
        }});
    </script>
</body>
</html>'''

    output_file = 'epstein_network_timeline.html'
    with open(output_file, 'w') as f:
        f.write(html)

    print(f"\nSaved timeline visualization to {output_file}")

if __name__ == '__main__':
    main()
