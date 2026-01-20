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

    # Sort categories for the summary table (Priority: Ready for Entry > Ready for Exit > Monitoring > Other)
    summary_priority = []
    summary_priority.extend(categories["READY FOR ENTRY"])
    summary_priority.extend(categories["READY FOR EXIT"])
    summary_priority.extend(categories["MONITORING"])
    summary_priority.extend(categories["OTHER"])
    
    # Generate Summary Table
    if summary_priority:
        report_lines.append("## 📊 Summary Table")
        report_lines.append("| Ticker | Verdict | Pattern (VSA) | Stage | Action |")
        report_lines.append("| :--- | :--- | :--- | :--- | :--- |")
        
        for ticker, data in summary_priority:
            verdict = data.get('verdict', 'N/A')
            stage = data.get('setup_stage', 'N/A')
            pattern = data.get('vsa_status', 'N/A')
            
            # Combine trigger info for brevity
            trigger = data.get('entry_trigger') or "Monitor"
            # Truncate long trigger text for table
            if len(trigger) > 50:
                trigger = trigger[:47] + "..."
            
            # Add emoji based on verdict
            verdict_icon = "🟢" if "BULL" in verdict.upper() else "🔴" if "BEAR" in verdict.upper() else "⚪"
            
            report_lines.append(f"| **{ticker}** | {verdict_icon} {verdict} | {pattern} | {stage} | {trigger} |")
        
        report_lines.append("")
        report_lines.append("---")

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
            report_lines.append(f"**Key Levels:** {', '.join(data.get('key_levels', []) if isinstance(data.get('key_levels'), list) else [str(data.get('key_levels'))])}")
            report_lines.append(f"")
            
            # Actionable info
            report_lines.append(f"#### Action Plan")
            report_lines.append(f"- **Entry Trigger:** {data.get('entry_trigger', 'N/A')}")
            report_lines.append(f"- **Invalidation:** {data.get('invalidation_level', 'N/A')}")
            report_lines.append(f"---")

    write_section("🚀 Ready for Entry", categories["READY FOR ENTRY"])
    write_section("⚠️ Ready for Exit", categories["READY FOR EXIT"])
    write_section("👀 Watch/Monitoring", categories["MONITORING"])
    write_section("Other", categories["OTHER"])
    
    return "\n".join(report_lines)

def generate_csv(results):
    import csv
    import io
    
    output = io.StringIO()
    
    
    # Write Legend to separate file
    legend_path = f"{REPORT_DIR}/REPORT_LEGEND.txt"
    with open(legend_path, 'w') as f:
        f.write("VSA SCREENER RESULTS - LEGEND\n")
        f.write("-----------------------------\n")
        f.write("CLV (Close Location Value): +1.0 (High Close) to -1.0 (Low Close). >0.5 Bullish, <-0.5 Bearish.\n")
        f.write("RelVol (Relative Volume): Ratio vs 20SMA. >1.5 High, >2.0 Ultra High, <0.7 Low.\n")
        f.write("PRIORITIES:\n")
        f.write("  VERY_HIGH: Monthly Confirmed + Weekly Confirmed (Perfect Alignment)\n")
        f.write("  HIGH: Monthly Confirmed + Weekly Stopping Volume (Sequence Early) OR Monthly Context + Weekly Confirmed\n")
        f.write("  MEDIUM: Weekly Confirmed (No Monthly support) OR Monthly Confirmed (No Weekly support)\n")
        f.write("  LOW: Watchlist only (Accumulation detected but no confirmation)\n")
        f.write("ACTION:\n")
        f.write("  ENTER_NOW: Confirmed Signal + Daily Trigger Met\n")
        f.write("  WAIT_FOR_TEST: Anchor found, waiting for Test\n")
        f.write("COLUMNS:\n")
        f.write("  Anchor_Date: The date of the initial VSA signal. Types:\n")
        f.write("     - STOPPING_VOLUME: Bullish Anchor (Down bar, High Vol, Close off lows)\n")
        f.write("     - BUYING_CLIMAX: Bearish Anchor (Up bar, High Vol, Weak Close)\n")
        f.write("     - SUPPLY_DOMINANCE: Bearish Anchor (Down bar, High Vol, Weak Close)\n")
        f.write("  Test1/Test2_Date: The dates of subsequent confirmation bars (Tests) on the same timeframe.\n")
        f.write("  Daily_Confirmation: 'TEST_OBSERVED' if a Test pattern appeared on the Daily chart in the last 5 days.\n")
    
    headers = [
        "Ticker",
        "Quarterly_Context",
        "Monthly_Context",
        "Weekly_Context",
        "Monthly_Signal",
        "Monthly_Anchor_Date",
        "Monthly_Test1_Date",
        "Monthly_Test2_Date",
        "Weekly_Signal",
        "Weekly_Anchor_Date",
        "Weekly_Test1_Date",
        "Weekly_Test2_Date",
        "Daily_Confirmation",
        "Verdict",
        "Priority",
        "Action",
        "Entry_Trigger",
        "Invalidation",
        "Key_Level_Support",
        "Key_Level_Resistance",
        "Weekly_CLV",
        "Weekly_RelVol",
        "Current_Price"
    ]
    
    writer = csv.DictWriter(output, fieldnames=headers, lineterminator='\n')
    writer.writeheader()
    
    for ticker, data in results.items():
        if "error" in data:
            continue
            
        # Parse Monthly/Weekly Signals (which might be dicts or strings depending on source)
        # From filter_tickers, they are dicts: {'type':..., 'status':..., 'anchor_date':...}
        m_sig = data.get('monthly_signal', {})
        w_sig = data.get('weekly_signal', {})
        
        # Helper to format signal string from dict
        def fmt_sig(sig_dict):
            if not isinstance(sig_dict, dict): return str(sig_dict)
            t = sig_dict.get('type')
            s = sig_dict.get('status')
            if not t: return "NONE"
            return f"{t}_{s}"

        # Determine Action
        action = "MONITOR"
        w_status = w_sig.get('status', '')
        if "CONFIRMED" in w_status and data.get('daily_confirmation') == "TEST_OBSERVED":
            action = "ENTER_NOW"
        elif "CONFIRMED" in w_status:
            action = "ENTER_PENDING_DAILY"
        elif "WATCH" in w_status:
            action = "WAIT_FOR_TEST"

        row = {
            "Ticker": ticker,
            "Quarterly_Context": data.get('quarterly_context', 'N/A'),
            "Monthly_Context": data.get('monthly_context', 'N/A'),
            
            "Monthly_Signal": fmt_sig(m_sig),
            "Monthly_Anchor_Date": m_sig.get('anchor_date', ''),
            "Monthly_Test1_Date": m_sig.get('test1_date', ''),
            "Monthly_Test2_Date": m_sig.get('test2_date', ''),
            
            "Weekly_Context": data.get('weekly_context', 'N/A'),
            "Weekly_Signal": fmt_sig(w_sig),
            "Weekly_Anchor_Date": w_sig.get('anchor_date', ''),
            "Weekly_Test1_Date": w_sig.get('test1_date', ''),
            "Weekly_Test2_Date": w_sig.get('test2_date', ''),
            
            "Daily_Confirmation": data.get('daily_confirmation', 'NONE'),
            
            "Verdict": data.get('verdict', 'NEUTRAL'),
            "Priority": data.get('priority', 'LOW'),
            "Action": action,
            
            "Entry_Trigger": data.get('entry_trigger', ''),
            "Invalidation": data.get('invalidation_level', ''),
            
            # Key levels is a list usually
            "Key_Level_Support": (data.get('key_levels', []) + [''])[0] if isinstance(data.get('key_levels'), list) and data.get('key_levels') else '',
            "Key_Level_Resistance": (data.get('key_levels', []) + ['',''])[1] if isinstance(data.get('key_levels'), list) and len(data.get('key_levels', []))>1 else '',
            
            "Weekly_CLV": data.get('latest_weekly_clv', ''),
            "Weekly_RelVol": data.get('latest_weekly_relvol', ''),
            "Current_Price": data.get('current_price', '')
        }
        writer.writerow(row)
        
    return output.getvalue()

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
        
    # NEW: Generate CSV
    csv_content = generate_csv(results)
    csv_filename = f"{REPORT_DIR}/REPORT_{datetime.now().strftime('%Y-%m-%d')}.csv"
    with open(csv_filename, 'w', encoding='utf-8') as f:
        f.write(csv_content)
        
    logging.info(f"Report generated: {filename} and {csv_filename}")

if __name__ == "__main__":
    save_report()
