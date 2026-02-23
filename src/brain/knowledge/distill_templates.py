import json
import os

def distill():
    source_dir = "/Users/german/Documents/Github/ClawCore_Unified/src/brain/knowledge/archive"
    output_file = "/Users/german/Documents/Github/ClawCore_Unified/src/brain/knowledge/MAPA_DE_CAPACIDADES.md"
    
    summary = "# 🗺️ MAPA DE CAPACIDADES CLAWCORE (Axiomas)\n\n"
    count = 0

    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".json"):
                try:
                    with open(os.path.join(root, file), 'r') as f:
                        data = json.load(f)
                        nodes = [n.get('type') for n in data.get('nodes', [])]
                        summary += f"- **{file}**: {', '.join(set(nodes[:5]))}...\n"
                        count += 1
                except:
                    continue
    
    with open(output_file, 'w') as f:
        f.write(summary)
    print(f"✅ Destiladas {count} plantillas en MAPA_DE_CAPACIDADES.md")

if __name__ == "__main__":
    distill()
