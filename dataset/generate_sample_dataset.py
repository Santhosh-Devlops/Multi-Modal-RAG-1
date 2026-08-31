import os
import io
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

DATASET_ROOT = Path(__file__).resolve().parent

def create_chart_image(plot_func, filename: str) -> str:
    """Generate a matplotlib chart and save to temp image file."""
    temp_dir = DATASET_ROOT / "temp_images"
    temp_dir.mkdir(parents=True, exist_ok=True)
    img_path = temp_dir / filename
    
    fig = plt.figure(figsize=(6, 3.2), dpi=150)
    plot_func(plt)
    plt.tight_layout()
    plt.savefig(str(img_path), format='png', bbox_inches='tight')
    plt.close(fig)
    return str(img_path)

# --- Matplotlib Diagram Generators ---

def plot_hydraulic_schematic(plt):
    plt.title("Figure 3.1: Hydraulic Circuit & Valve Routing Schematic", fontsize=10, fontweight='bold')
    # Draw simple block schematic with interconnects
    boxes = [
        (1, 4, "Hydraulic\nReservoir"),
        (4, 4, "Variable\nPump"),
        (7, 4, "Pressure\nRelief Valve"),
        (4, 1, "Coolant\nHeat Exchanger"),
        (7, 1, "Spindle\nActuator Cylinders")
    ]
    for x, y, label in boxes:
        plt.gca().add_patch(plt.Rectangle((x-0.8, y-0.5), 1.6, 1.0, fill=True, color='#2b6cb0', alpha=0.3))
        plt.gca().add_patch(plt.Rectangle((x-0.8, y-0.5), 1.6, 1.0, fill=False, edgecolor='#2b6cb0', lw=2))
        plt.text(x, y, label, ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Draw arrows
    plt.annotate('', xy=(3.2, 4), xytext=(1.8, 4), arrowprops=dict(arrowstyle="->", color="#c53030", lw=2))
    plt.annotate('', xy=(6.2, 4), xytext=(4.8, 4), arrowprops=dict(arrowstyle="->", color="#c53030", lw=2))
    plt.annotate('', xy=(4, 1.5), xytext=(4, 3.5), arrowprops=dict(arrowstyle="->", color="#2f855a", lw=2))
    plt.annotate('', xy=(6.2, 1), xytext=(4.8, 1), arrowprops=dict(arrowstyle="->", color="#2f855a", lw=2))
    plt.xlim(0, 9)
    plt.ylim(0, 5.5)
    plt.axis('off')

def plot_mri_cryogen_diagram(plt):
    plt.title("Figure 4.2: Superconducting Magnet Cryogenic Subsystem", fontsize=10, fontweight='bold')
    t = np.linspace(0, 24, 100)
    helium_level = 95 - 0.25 * t + 0.1 * np.sin(t)
    pressure = 1.2 + 0.05 * np.cos(t / 2)
    
    ax1 = plt.gca()
    ax1.plot(t, helium_level, color='#2b6cb0', lw=2, label="Liquid Helium Level (%)")
    ax1.set_xlabel("Operational Time (Hours)", fontsize=8)
    ax1.set_ylabel("Helium Level (%)", color='#2b6cb0', fontsize=8)
    ax1.set_ylim(80, 100)
    
    ax2 = ax1.twinx()
    ax2.plot(t, pressure, color='#c53030', lw=2, linestyle='--', label="Boil-off Pressure (Bar)")
    ax2.set_ylabel("Boil-off Pressure (Bar)", color='#c53030', fontsize=8)
    ax2.set_ylim(1.0, 1.5)

def plot_financial_performance_chart(plt):
    plt.title("Figure 2.1: Five-Year Revenue & Operating Profit Trajectory", fontsize=10, fontweight='bold')
    years = ['FY22', 'FY23', 'FY24', 'FY25', 'FY26']
    revenue = [42.5, 48.0, 55.2, 61.8, 74.4]
    ebitda = [9.2, 11.5, 13.8, 16.2, 21.0]
    
    x = np.arange(len(years))
    width = 0.35
    plt.bar(x - width/2, revenue, width, label='Gross Revenue ($M)', color='#2b6cb0')
    plt.bar(x + width/2, ebitda, width, label='EBITDA Profit ($M)', color='#38a169')
    plt.xlabel('Fiscal Year', fontsize=8)
    plt.ylabel('Amount in Millions USD', fontsize=8)
    plt.xticks(x, years)
    plt.legend(fontsize=8)
    plt.grid(axis='y', linestyle=':', alpha=0.6)

def plot_robotics_kinematics_diagram(plt):
    plt.title("Figure 3.3: 6-DOF Manipulator Joint Kinematics & Coordinate Frames", fontsize=10, fontweight='bold')
    # Draw kinematic arm
    x_pts = [0, 1.5, 3.0, 4.2, 5.0]
    y_pts = [0, 2.5, 2.0, 3.5, 3.0]
    plt.plot(x_pts, y_pts, '-o', color='#2d3748', lw=3, markersize=8, markerfacecolor='#e53e3e')
    for i, (x, y) in enumerate(zip(x_pts, y_pts)):
        plt.text(x+0.1, y+0.1, f"Joint {i+1}", fontsize=8, fontweight='bold')
    plt.xlim(-0.5, 6.0)
    plt.ylim(-0.5, 4.5)
    plt.grid(True, linestyle='--', alpha=0.5)

def plot_avionics_radar_block(plt):
    plt.title("Figure 5.1: X-Band Pulse-Doppler Radar Transceiver Architecture", fontsize=10, fontweight='bold')
    blocks = [
        (1, 3, "Waveform\nGenerator"),
        (3.5, 3, "Solid-State\nPower Amp"),
        (6, 3, "Duplexer &\nArray Antenna"),
        (3.5, 1, "Low Noise\nReceiver"),
        (1, 1, "Digital Signal\nProcessor (DSP)")
    ]
    for x, y, label in blocks:
        plt.gca().add_patch(plt.Rectangle((x-0.9, y-0.45), 1.8, 0.9, fill=True, color='#4a5568', alpha=0.25))
        plt.gca().add_patch(plt.Rectangle((x-0.9, y-0.45), 1.8, 0.9, fill=False, edgecolor='#2d3748', lw=1.5))
        plt.text(x, y, label, ha='center', va='center', fontsize=7.5, fontweight='bold')
    plt.annotate('', xy=(2.6, 3), xytext=(1.9, 3), arrowprops=dict(arrowstyle="->", color="#c53030", lw=2))
    plt.annotate('', xy=(5.1, 3), xytext=(4.4, 3), arrowprops=dict(arrowstyle="->", color="#c53030", lw=2))
    plt.annotate('', xy=(4.4, 1), xytext=(5.5, 2.5), arrowprops=dict(arrowstyle="->", color="#2b6cb0", lw=2))
    plt.annotate('', xy=(1.9, 1), xytext=(2.6, 1), arrowprops=dict(arrowstyle="->", color="#2b6cb0", lw=2))
    plt.xlim(0, 7.5)
    plt.ylim(0, 4.5)
    plt.axis('off')


def build_15_page_pdf(output_path: Path, title: str, domain: str, doc_code: str, diagram_func, diagram_name: str, table_data: list, spec_paragraphs: list):
    """Build a rich 15-page PDF document with sections, tables, images, and domain data."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=10
    )
    h1_style = ParagraphStyle(
        'DocH1',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#2b6cb0'),
        spaceBefore=12,
        spaceAfter=6
    )
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading3'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#2d3748'),
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=6
    )
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Italic'],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#718096')
    )

    story = []
    
    # Generate Chart Image
    chart_path = create_chart_image(diagram_func, diagram_name)

    # 15 Pages of rich structured content
    for page_idx in range(1, 16):
        story.append(Paragraph(f"<b>{title}</b> &mdash; {domain} Engineering Reference", title_style if page_idx == 1 else h2_style))
        story.append(Paragraph(f"Document Code: {doc_code} | Domain: {domain} | Page {page_idx} of 15 | Synthetic Demonstration Dataset", meta_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e0'), spaceAfter=8, spaceBefore=4))

        if page_idx == 1:
            story.append(Paragraph("1. Executive System Overview & Scope", h1_style))
            story.append(Paragraph(
                f"This document defines the comprehensive operational specifications, maintenance standards, and technical safety guidelines for the <b>{title}</b>. "
                f"It is engineered for multi-disciplinary operators, technicians, and supervisory personnel operating within the <b>{domain}</b> sector. "
                "All parameters and tolerances described herein are strictly validated under standard ISO/IEC quality and environmental frameworks.",
                body_style
            ))
            story.append(Paragraph("1.1 Regulatory Compliance & Operational Constraints", h2_style))
            story.append(Paragraph(
                "Operators must ensure compliance with all environmental and physical operating limits. "
                "Any variation exceeding standard tolerances necessitates immediate preventive inspection and diagnostic execution.",
                body_style
            ))
            
        elif page_idx == 2:
            story.append(Paragraph("2. Architectural Subsystems & Component Identification", h1_style))
            story.append(Paragraph(
                "The system comprises four interdependent modules: the primary power actuation subsystem, the precision sensor feedback loop, "
                "the environmental thermal regulator, and the computerized supervisory controller. "
                "Each subsystem operates within strictly regulated closed-loop feedback thresholds.",
                body_style
            ))
            story.append(Paragraph(spec_paragraphs[0], body_style))

        elif page_idx == 3:
            story.append(Paragraph("3. Operational Specifications & Safe Operating Limits", h1_style))
            story.append(Paragraph(
                "System reliability is maintained by continuous monitoring of pressure, temperature, rotational velocity, and electrical load. "
                "The threshold table below summarizes the operational bands across continuous, warning, and emergency trip levels.",
                body_style
            ))
            # Insert Main Specifications Table
            tbl = Table(table_data, colWidths=[130, 90, 90, 100, 110])
            tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2b6cb0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8.5),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f7fafc'), colors.white]),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 8))
            story.append(Paragraph(spec_paragraphs[1], body_style))

        elif page_idx == 4:
            story.append(Paragraph("4. Subsystem Schematic & Visual Routing Diagram", h1_style))
            story.append(Paragraph(
                "The visual schematic below details component interconnections, fluid/signal routing paths, and directional feedback mechanisms. "
                "Refer to the numbered component blocks when performing preventative maintenance or tracing diagnostic telemetry.",
                body_style
            ))
            story.append(Spacer(1, 4))
            story.append(RLImage(chart_path, width=5.8*inch, height=2.8*inch))
            story.append(Spacer(1, 6))
            story.append(Paragraph("Figure Interpretation: Component blocks in blue represent primary actuators; red arrows indicate high-pressure / excitation paths; green arrows indicate return and feedback routing.", body_style))

        elif page_idx == 5:
            story.append(Paragraph("5. Scheduled Preventive Maintenance Protocol", h1_style))
            story.append(Paragraph(
                "Maintenance tasks are structured around operating hour milestones: 50 hours (Initial Inspection), 250 hours (Quarterly Service), 500 hours (Major Overhaul), and 2000 hours (Comprehensive Calibration). "
                "Failure to replace filtration elements or replenish synthetic lubrication at specified intervals will void system warranty.",
                body_style
            ))
            # Maintenance Schedule Table
            maint_data = [
                ["Interval", "Subsystem Component", "Service Procedure", "Lubricant / Spec", "Sign-Off"],
                ["50 Hours", "Hydraulic Filter", "Visual Inspection & Differential Delta Check", "ISO VG 46", "Tech Level 1"],
                ["250 Hours", "Cooling Core", "Thermal Flush & Radiator Debris Purge", "50/50 Glycol", "Tech Level 1"],
                ["500 Hours", "Spindle / Bearings", "Synthetic Precision Bearing Regrease", "Klüber NBU 15", "Lead Engineer"],
                ["1000 Hours", "Actuator Seals", "Fluorocarbon O-Ring Replacement", "Viton Grade A", "Certified Tech"],
                ["2000 Hours", "Optical Encoders", "Laser Interferometer Calibration", "NIST Traceable", "Senior Specialist"]
            ]
            m_tbl = Table(maint_data, colWidths=[65, 95, 160, 100, 90])
            m_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#edf2f7'), colors.white]),
                ('FONTSIZE', (0, 1), (-1, -1), 7.5),
            ]))
            story.append(m_tbl)
            story.append(Spacer(1, 6))
            story.append(Paragraph(spec_paragraphs[2], body_style))

        elif page_idx in [6, 7, 8, 9, 10, 11, 12, 13, 14]:
            sec_num = page_idx
            story.append(Paragraph(f"{sec_num}. Specialized Operating Procedures & In-Depth Analysis (Part {page_idx - 5})", h1_style))
            story.append(Paragraph(spec_paragraphs[min(len(spec_paragraphs)-1, page_idx - 3)], body_style))
            story.append(Paragraph(
                f"Detailed diagnostic logs recorded during trial operations in {domain} applications demonstrate sustained operational stability. "
                "Continuous telemetry ensures that variance remains well within 0.05% of target standard values. "
                "Operators must maintain a daily physical logbook complementing the automated digital supervisory data logger.",
                body_style
            ))
            
            # Add secondary diagnostic table
            diag_data = [
                ["Code", "Condition / Symptom", "Probable Root Cause", "Corrective Action", "Priority"],
                ["ERR-01", "Pressure Drop > 15%", "Clogged intake manifold strainer", "Clean/replace primary mesh", "High"],
                ["ERR-04", "Temperature Exceeds 70 C", "Insufficient coolant circulation rate", "Verify pump impeller rpm", "Critical"],
                ["WARN-09", "Vibration Delta > 2.5 mm/s", "Imbalanced rotational tooling spindle", "Perform dynamic balancing", "Medium"],
                ["INFO-12", "Calibration Offset", "Ambient thermal drift compensation", "Execute zero-offset routine", "Low"]
            ]
            d_tbl = Table(diag_data, colWidths=[55, 120, 145, 135, 60])
            d_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a5568')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
                ('FONTSIZE', (0, 1), (-1, -1), 7.5),
            ]))
            story.append(d_tbl)

        elif page_idx == 15:
            story.append(Paragraph("15. Emergency Procedures, Safety Interlocks & Compliance Sign-Off", h1_style))
            story.append(Paragraph(
                "In the event of an emergency trip or catastrophic parameter deviation, the automated safety interlocks will de-energize the main power contactor within 25 milliseconds. "
                "Personnel must follow the mandatory lockout-tagout (LOTO) protocol before inspecting internal enclosures.",
                body_style
            ))
            story.append(Paragraph(
                "This technical reference has been verified and approved for internship and multi-agent multimodal RAG demonstration. "
                "Ground truth citations referencing any page from 1 to 15 are fully indexed into the vector intelligence database.",
                body_style
            ))
            story.append(Spacer(1, 10))
            story.append(Paragraph("<b>Authorization Sign-Off:</b> Chief Technical Officer &mdash; Quality Assurance Department", meta_style))

        if page_idx < 15:
            story.append(PageBreak())

    doc.build(story)
    print(f"Generated 15-page manual: {output_path.name}")


def generate_all_datasets():
    print("Starting generation of multi-domain 15+ page multimodal demonstration dataset...")
    
    # 1. Manufacturing Domain: Industrial CNC Machining Manual
    mfg_table = [
        ["Parameter", "Nominal Operating", "Warning Threshold", "Critical Shutdown", "Unit / Spec"],
        ["Spindle Speed", "8,000 - 12,000", "14,500", "16,000", "RPM"],
        ["Hydraulic Pressure", "140 - 160", "185", "210", "Bar"],
        ["Operating Temperature", "40 - 60", "70", "85", "Degrees Celsius"],
        ["Coolant Flow Rate", "45 - 60", "30", "15", "Liters / Minute"],
        ["Spindle Runout Tolerance", "< 0.003", "0.008", "0.015", "Millimeters (mm)"],
        ["Bearing Grease Interval", "500", "550", "600", "Operating Hours"]
    ]
    mfg_specs = [
        "The high-precision electro-spindle uses ceramic hybrid ball bearings capable of achieving 16,000 RPM under continuous torque.",
        "Hydraulic actuation drives the automatic tool changer (ATC) with a 24-pocket carousel and dual-gripper arm mechanism.",
        "Lubrication of linear guideways is managed by a centralized automatic impulse pump operating at 15-minute intervals."
    ]
    build_15_page_pdf(
        DATASET_ROOT / "manufacturing" / "industrial_cnc_machining_manual.pdf",
        "Industrial CNC 5-Axis Machining Center Technical Manual",
        "Manufacturing",
        "MAN-CNC-2026-X5",
        plot_hydraulic_schematic,
        "mfg_hydraulic.png",
        mfg_table,
        mfg_specs
    )

    # 2. Healthcare Domain: MRI Medical Diagnostic System
    hc_table = [
        ["Subsystem Parameter", "Standard Target", "Alert Boundary", "Critical Limit", "Standard / Unit"],
        ["Static Magnetic Field (B0)", "3.000", "2.985", "2.950", "Tesla (T)"],
        ["Liquid Helium Boil-off", "1.10 - 1.25", "1.35", "1.50", "Bar (Cryo Pressure)"],
        ["Helium Fill Level", "90 - 98", "80", "70", "Percent (%)"],
        ["RF Power Peak SAR", "< 2.0", "3.2", "4.0", "Watts / kg (Body SAR)"],
        ["Gradient Slew Rate", "200", "220", "250", "Tesla / meter / second"],
        ["Patient Bore Temperature", "20 - 22", "24", "26", "Degrees Celsius"]
    ]
    hc_specs = [
        "Superconducting magnet technology requires continuous vacuum insulation and closed-loop cryogenic re-condensation.",
        "Zone IV safety strictly prohibits ferromagnetic implements; 5 Gauss exclusion boundary must be physically demarcated.",
        "Radiofrequency transmit coils employ 16-channel phased array architecture for ultra-high SNR neuro-imaging."
    ]
    build_15_page_pdf(
        DATASET_ROOT / "healthcare" / "mri_medical_diagnostic_system_manual.pdf",
        "High-Field 3.0T MRI Diagnostic System Technical Manual",
        "Healthcare",
        "MED-MRI-3000-HD",
        plot_mri_cryogen_diagram,
        "hc_mri.png",
        hc_table,
        hc_specs
    )

    # 3. Finance Domain: Annual Financial Performance Report
    fin_table = [
        ["Financial Metric", "FY24 Actual", "FY25 Actual", "FY26 Projected", "Variance YoY ($M)"],
        ["Gross Operating Revenue", "$55.2M", "$61.8M", "$74.4M", "+$12.6M (+20.4%)"],
        ["Cost of Goods Sold (COGS)", "$28.4M", "$31.0M", "$36.2M", "+$5.2M (+16.8%)"],
        ["Operating Profit (EBITDA)", "$13.8M", "$16.2M", "$21.0M", "+$4.8M (+29.6%)"],
        ["Capital Expenditure (CAPEX)", "$11.2M", "$12.5M", "$14.8M", "+$2.3M (+18.4%)"],
        ["R&D Innovation Investment", "$6.4M", "$7.8M", "$9.5M", "+$1.7M (+21.8%)"],
        ["Net Cash Flow from Operations", "$16.5M", "$19.1M", "$24.6M", "+$5.5M (+28.8%)"]
    ]
    fin_specs = [
        "Consolidated financial statements demonstrate robust 20.4% year-over-year revenue expansion driven by automated product lines.",
        "CAPEX allocation prioritized modern multi-axis CNC manufacturing facilities and secure cloud data center infrastructure.",
        "Operational efficiency gains expanded EBITDA margin from 25.0% in FY24 to 28.2% in FY26."
    ]
    build_15_page_pdf(
        DATASET_ROOT / "finance" / "annual_financial_performance_report.pdf",
        "Global Technology Holdings Annual Financial Performance Report",
        "Finance",
        "FIN-REP-2026-Q4",
        plot_financial_performance_chart,
        "fin_perf.png",
        fin_table,
        fin_specs
    )

    # 4. Education Domain: Applied Robotics Engineering Handbook
    edu_table = [
        ["Kinematic Parameter", "Joint 1 (Base)", "Joint 2 (Shoulder)", "Joint 3 (Elbow)", "Joints 4-6 (Wrist)"],
        ["Motion Range", "+/- 170 deg", "-100/+135 deg", "-120/+155 deg", "+/- 360 deg"],
        ["Max Angular Velocity", "180 deg/s", "175 deg/s", "180 deg/s", "360 deg/s"],
        ["Payload Capacity", "16.0 kg", "16.0 kg", "16.0 kg", "12.0 kg"],
        ["Repeatability Tolerance", "+/- 0.02 mm", "+/- 0.02 mm", "+/- 0.02 mm", "+/- 0.015 mm"],
        ["Operating Duty Cycle", "100%", "100%", "100%", "100% (Continuous)"]
    ]
    edu_specs = [
        "Forward and inverse kinematics are derived using standard Denavit-Hartenberg (D-H) 4x4 homogenous transformation matrices.",
        "Actuator drives utilize brushless DC servomotors integrated with 100:1 harmonic drive zero-backlash gearheads.",
        "Safety zones implement ISO 10218 collaborative speed and separation monitoring with dynamic laser perimeter scanning."
    ]
    build_15_page_pdf(
        DATASET_ROOT / "education" / "applied_robotics_engineering_handbook.pdf",
        "Applied Robotics & Kinematics Engineering Handbook",
        "Education",
        "EDU-ROB-6DOF-2026",
        plot_robotics_kinematics_diagram,
        "edu_robotics.png",
        edu_table,
        edu_specs
    )

    # 5. Defence Domain: Aerospace Avionics Maintenance Spec
    def_table = [
        ["Avionics Subsystem", "Nominal Frequency / Spec", "Max Allowable Drift", "Environmental Temp", "MIL-STD Ref"],
        ["X-Band Radar Transceiver", "9.3 - 9.8 GHz", "+/- 2.5 MHz", "-40 C to +85 C", "MIL-STD-810H"],
        ["Fly-By-Wire Actuation Bus", "Quad-Redundant CAN", "0 dropped frames", "-55 C to +105 C", "MIL-STD-1553B"],
        ["Tactical Data Link (Link 16)", "960 - 1215 MHz", "Jitter < 5 ns", "-40 C to +70 C", "STANAG 5516"],
        ["Inertial Navigation (INS)", "Ring Laser Gyro", "< 0.8 NM / Hour", "-40 C to +85 C", "DO-178C Level A"],
        ["Primary Power Distribution", "115 VAC 400 Hz 3-Phase", "+/- 5 VAC", "-50 C to +90 C", "MIL-STD-704F"]
    ]
    def_specs = [
        "Solid-state active electronically scanned array (AESA) radar incorporates gallium nitride (GaN) transmit-receive modules.",
        "Flight control computer features triple-modular redundancy (TMR) with hardware voting logic to prevent single-point failures.",
        "Electromagnetic interference (EMI) shielding meets 100 dB attenuation threshold across 10 kHz to 18 GHz frequency spectrum."
    ]
    build_15_page_pdf(
        DATASET_ROOT / "defence" / "aerospace_avionics_maintenance_spec.pdf",
        "Aerospace Avionics & Radar Maintenance Engineering Specification",
        "Defence",
        "DEF-AVX-SPEC-2026",
        plot_avionics_radar_block,
        "def_radar.png",
        def_table,
        def_specs
    )

    print("All multi-domain 15-page demonstration datasets generated successfully!")

if __name__ == "__main__":
    generate_all_datasets()
