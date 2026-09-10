import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def save_report(suspicious_neurons, ratio, filename="scan_report.json"):
    """Scan ka result ek JSON file mein save karta hai."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "verdict": "BACKDOOR LIKELY" if len(suspicious_neurons) > 0 else "CLEAN",
        "suspicious_neurons": suspicious_neurons,
        "ratio_per_neuron": [round(r, 2) for r in ratio],
    }

    with open(filename, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Report saved: {filename}")


def save_pdf_report(model_path, suspicious_neurons, peak_z_scores, out_path="scan_report.pdf"):
    """Scan ka result ek professional PDF report mein save karta hai."""
    verdict = "BACKDOOR LIKELY" if len(suspicious_neurons) > 0 else "CLEAN"

    doc = SimpleDocTemplate(out_path, pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#1a1a2e"))
    elements = []

    elements.append(Paragraph("NeuroFence Security Report", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Model scanned: {model_path}", styles["Normal"]))
    elements.append(Paragraph(f"Scan date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    verdict_color = colors.red if verdict == "BACKDOOR LIKELY" else colors.green
    verdict_style = ParagraphStyle("VerdictStyle", parent=styles["Heading2"], textColor=verdict_color)
    elements.append(Paragraph(f"Verdict: {verdict}", verdict_style))
    elements.append(Spacer(1, 20))

    table_data = [["Neuron", "Peak Z-Score", "Status"]]
    for i, z in enumerate(peak_z_scores):
        status = "SUSPICIOUS" if i in suspicious_neurons else "normal"
        table_data.append([str(i), f"{z:.2f}", status])

    table = Table(table_data, colWidths=[100, 150, 150])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    elements.append(table)

    doc.build(elements)
    print(f"PDF report saved: {out_path}")