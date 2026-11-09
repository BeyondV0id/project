import base64
import urllib.request
import os

mm = """flowchart LR
    subgraph P1["1. CAPTURE AND PREPARE"]
        direction TB
        A1["Meal photo with optional<br/>context and dietary goal"]
        A2["Streamlit UI calls FastAPI<br/>request validated, analysis starts"]
        A3["Image preparation and router<br/>T0 simple, T1 mixed, T2 ambiguous"]
        A1 --> A2 --> A3
    end

    subgraph P2["2. ANALYSE THE PLATE"]
        direction TB
        B1["Perception Agent (VLM)<br/>names food and marks regions<br/>never calories or grams"]
        B2["Match, retrieve, estimate portion<br/>IFCT 2017 or USDA, state filtered<br/>mass in grams with a range"]
        B3["Nutrition calculation<br/>per-100 g values scaled by grams<br/>plain Python, kJ converted to kcal"]
        B1 --> B2 --> B3
    end

    subgraph P3["3. CHECK AND DECIDE"]
        direction TB
        C1["Critic Agent<br/>checks mass, density and macros<br/>runs on T1 and T2 only"]
        C2["Confidence calculation<br/>seven signals combined into one score<br/>calibrated on labelled data"]
        C3{"Confidence high enough?"}
        C4["Clarification<br/>asks the most useful questions<br/>two questions a round, two rounds max"]
        C1 --> C2 --> C3
        C3 -->|no| C4
    end

    subgraph P4["4. REPORT AND STORE"]
        direction TB
        D1["Report Agent<br/>explains the validated values<br/>never changes the numbers"]
        D2["Diet Recommendation Agent<br/>uses validated totals and user goal<br/>general guidance, not medical advice"]
        D3["Persistence and response<br/>stores analysis, sources, artifacts<br/>returns values, ranges, sources"]
        D1 --> D2 --> D3
    end

    P1 ==> P2 ==> P3
    C3 -->|yes| P4
    C4 -.->|"answers, re-run affected parts"| B2
    C4 -.->|"skipped, report with limitations"| P4

    style P1 fill:#F4FAF6,stroke:#8FC7A5,stroke-width:2px,color:#2F6B47
    style P2 fill:#F3F8FE,stroke:#93B9E8,stroke-width:2px,color:#1F4E79
    style P3 fill:#FFF9EF,stroke:#E2BE7C,stroke-width:2px,color:#7A4E12
    style P4 fill:#F8F4FD,stroke:#B7A2E2,stroke-width:2px,color:#4B2E83
"""

raw_enc = base64.b64encode(mm.encode('utf-8')).decode('ascii')
url = f'https://mermaid.ink/img/{raw_enc}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

os.makedirs('docs/report/assets', exist_ok=True)
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
        out_path = 'docs/report/assets/system_workflow.png'
        with open(out_path, 'wb') as f:
            f.write(data)
        print(f'Successfully generated {out_path}, size={len(data)} bytes')
except Exception as e:
    print('Error:', e)
