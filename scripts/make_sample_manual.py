"""Generate a FICTIONAL machine manual for demos (no real vendor's content).

python scripts/make_sample_manual.py  ->  sample_data/HP-200_manual.pdf
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

OUT = Path(__file__).resolve().parent.parent / "sample_data" / "HP-200_manual.pdf"
S = getSampleStyleSheet()
H1, H2, P = S["Title"], S["Heading2"], S["BodyText"]


def table(rows, widths):
    t = Table(rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
    ]))
    return t


def para_rows(rows):
    return [[Paragraph(str(c), P) for c in r] for r in rows]


story = [
    # p.1
    Paragraph("HP-200 Hydraulic Press — Operation &amp; Maintenance Manual", H1),
    Paragraph("Fictional equipment created for software demonstration only. "
              "Manufacturer: Example Press Works (fictional). Document rev. C.", P),
    Spacer(1, 12),
    Paragraph("1. General safety", H2),
    Paragraph("WARNING: Only trained operators may run the HP-200. Wear safety glasses, "
              "cut-resistant gloves and steel-toe shoes in the press area. Never place hands "
              "between the ram and the bed while the hydraulic unit is energised. "
              "Both light curtains must be tested at the start of every shift by passing the "
              "test rod through the beam; the ram must stop within 120 ms.", P),
    Paragraph("Before any maintenance, cleaning, or die change, perform the Lockout/Tagout "
              "(LOTO) procedure in section 3 and release stored hydraulic pressure.", P),
    PageBreak(),
    # p.2
    Paragraph("2. Technical specifications", H2),
    table(para_rows([
        ["Item", "Value"],
        ["Maximum force", "200 kN"],
        ["Ram stroke", "250 mm"],
        ["Working pressure", "180 bar (max. relief valve setting 195 bar)"],
        ["Hydraulic oil", "ISO VG 46 hydraulic oil, tank capacity 60 L"],
        ["Normal oil temperature", "35–55 °C"],
        ["Motor", "7.5 kW, 400 V, 3-phase, 50 Hz"],
        ["Oil filter", "Return-line filter cartridge, part no. HF-46-10 (10 µm)"],
        ["Light curtain", "Type 4, stopping time limit 120 ms"],
    ]), [150, 300]),
    PageBreak(),
    # p.3
    Paragraph("3. Lockout/Tagout (LOTO) procedure", H2),
    Paragraph("1) Tell affected operators that the press will be shut down. "
              "2) Return the ram to top-dead-centre and press STOP. "
              "3) Turn the main disconnect switch Q1 to OFF and fit your personal padlock and tag. "
              "4) Open the pressure-release valve V3 on the hydraulic unit and wait until "
              "gauge G1 reads 0 bar. "
              "5) Place the safety block under the ram. "
              "6) Try to start the press to verify it does not move (zero-energy check). "
              "Only the person who fitted the lock may remove it.", P),
    PageBreak(),
    # p.4
    Paragraph("4. Error codes", H2),
    table(para_rows([
        ["Code", "Meaning", "Action"],
        ["E-01", "Emergency stop pressed", "Release the E-stop, find the reason it was pressed, press RESET."],
        ["E-03", "Light curtain interrupted during stroke",
         "Remove the obstruction. If it repeats with no obstruction, clean the lenses and check alignment (section 5.2)."],
        ["E-07", "Hydraulic oil temperature high (above 65 °C)",
         "Stop production and let the unit cool. Check oil level, clean the oil cooler fins, "
         "check the cooling fan. If E-07 returns within 1 hour, replace the oil filter HF-46-10 (section 6) "
         "and call maintenance."],
        ["E-12", "Low hydraulic pressure (below 150 bar)",
         "Check oil level, look for leaks at hose fittings, check the pump coupling. "
         "Do not raise the relief valve above 195 bar."],
        ["E-15", "Ram position sensor fault",
         "Perform LOTO, check the sensor cable connector X12. Replace sensor if the fault remains."],
        ["E-21", "Oil filter clogged (differential pressure switch)",
         "Replace filter cartridge HF-46-10 within the current shift."],
    ]), [45, 140, 265]),
    PageBreak(),
    # p.5
    Paragraph("5. Troubleshooting", H2),
    Paragraph("5.1 Ram moves slowly: usually low oil level, a clogged filter (see E-21) or "
              "air in the hydraulic system. Bleed air by running 10 empty strokes at low speed.", P),
    Paragraph("5.2 Light curtain false trips: clean both lenses with a soft lint-free cloth. "
              "The alignment LED must be steady green; adjust the brackets until it is.", P),
    Paragraph("5.3 Abnormal noise from the pump: a high-pitched whine often means cavitation "
              "caused by low oil or a blocked suction strainer. Stop the press and check "
              "oil level first.", P),
    Paragraph("5.4 Oil leak at cylinder: perform LOTO, release pressure, then tighten the "
              "fitting to 45 N·m. If the rod seal leaks, the seal kit SK-200 must be replaced "
              "by qualified maintenance staff.", P),
    PageBreak(),
    # p.6
    Paragraph("6. Preventive maintenance schedule", H2),
    table(para_rows([
        ["Interval", "Task"],
        ["Every shift", "Test light curtains; check oil level sight glass; look for leaks."],
        ["Weekly", "Clean oil cooler fins with compressed air (max 4 bar); check hoses for wear."],
        ["Every 500 operating hours", "Replace return-line filter cartridge HF-46-10."],
        ["Every 2,000 operating hours or yearly", "Change hydraulic oil (ISO VG 46, 60 L); take an oil sample."],
        ["Yearly", "Verify light-curtain stopping time ≤ 120 ms with a stop-time meter; "
                   "inspect ram guide gibs."],
    ]), [150, 300]),
    Spacer(1, 10),
    Paragraph("Replacing the oil filter: perform LOTO (section 3), place a drip tray, unscrew "
              "the filter bowl, replace the HF-46-10 cartridge and O-ring, hand-tighten plus "
              "1/4 turn, then run 5 empty strokes and check for leaks.", P),
    PageBreak(),
    # p.7
    Paragraph("7. Die change", H2),
    Paragraph("1) Perform LOTO (section 3) and place the safety block. "
              "2) Loosen the four upper die clamps C1–C4 and the lower clamps C5–C8. "
              "3) Use the die cart to slide the die out; never lift dies above 25 kg by hand. "
              "4) Clean the bed and ram faces. 5) Insert the new die, centre it with the "
              "locating pins and torque clamps to 60 N·m in a cross pattern. "
              "6) Remove the safety block and lock, then run one slow single stroke to check "
              "die closing height.", P),
]

OUT.parent.mkdir(exist_ok=True)
SimpleDocTemplate(str(OUT), pagesize=A4, title="HP-200 Manual (fictional)").build(story)
print("wrote", OUT)
