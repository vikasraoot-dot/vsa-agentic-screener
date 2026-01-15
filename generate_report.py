import json
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

INPUT_FILE = 'vsa_results.json'
REPORT_DIR = 'reports'

def load_results():
    if not os.path.exists(INPUT_FILE):
        return {}
    with open(INPUT_FILE, 'r') as f:
        return json.load(f)

def generate_markdown(results):
    date_str = datetime.now().strftime('%Y-%m-%d')
    report_lines = [f"# VSA Analysis Report - {date_str}", ""]
    
    # Group by setup stage/verdict
    # Categories: READY FOR ENTRY, MONITORING, EXIT, OTHER
    categories = {
        "READY FOR ENTRY": [],
        "READY FOR EXIT": [],
        "MONITORING": [],
        "OTHER": []
    }
    
    for ticker, data in results.items():
        if "error" in data:
            continue
            
        stage = data.get("setup_stage", "Monitoring").upper()
        verdict = data.get("verdict", "NEUTRAL").upper()
        
        if "ENTRY" in stage:
            categories["READY FOR ENTRY"].append((ticker, data))
        elif "EXIT" in stage:
            categories["READY FOR EXIT"].append((ticker, data))
        elif "MONITORING" in stage:
            categories["MONITORING"].append((ticker, data))
        else:
            categories["OTHER"].append((ticker, data))

    # Helper function to write a section
    def write_section(title, items):
        if not items:
            return
        report_lines.append(f"## {title}")
        for ticker, data in items:
            report_lines.append(f"### {ticker} ({data.get('verdict', 'N/A')})")
            report_lines.append(f"**VSA Status:** {data.get('vsa_status', 'N/A')}")
            report_lines.append(f"")
            report_lines.append(f"**Smart Money Logic:**")
            report_lines.append(f"{data.get('smart_money_logic', 'N/A')}")
            report_lines.append(f"")
            report_lines.append(f"**Correlation:**")
            report_lines.append(f"{data.get('correlation_analysis', 'N/A')}")
            report_lines.append(f"")
            report_lines.append(f"**Key Levels:** {', '.join(data.get('key_levels', []))}")
            report_lines.append(f"")
            
            # Actionable info
            report_lines.append(f"#### Action Plan")
            report_lines.append(f"- **Entry Trigger:** {data.get('entry_trigger', 'N/A')}")
            report_lines.append(f"- **Volume Req:** {data.get('volume_requirement', 'N/A')}")
            report_lines.append(f"- **Invalidation:** {data.get('invalidation_level', 'N/A')}")
            report_lines.append(f"- **Exit Trigger:** {data.get('exit_trigger', 'N/A')}")
            report_lines.append(f"---")

    write_section("🚀 Ready for Entry", categories["READY FOR ENTRY"])
    write_section("⚠️ Ready for Exit", categories["READY FOR EXIT"])
    write_section("👀 Watch/Monitoring", categories["MONITORING"])
    write_section("Other", categories["OTHER"])
    
    return "\n".join(report_lines)

def save_report():
    results = load_results()
    if not results:
        logging.info("No results to report.")
        return
        
    report_content = generate_markdown(results)
    
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)
        
    filename = f"{REPORT_DIR}/REPORT_{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    logging.info(f"Report generated: {filename}")

if __name__ == "__main__":
    save_report()
