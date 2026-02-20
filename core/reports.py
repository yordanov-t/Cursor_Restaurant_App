"""
Reports module for generating reservation statistics and PDF exports.

Generates monthly, weekly, and daily reservation charts.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Union
import os
from collections import defaultdict


def row_get(row: Union[Dict, Any], key: str, default=None):
    """
    Safely get value from a row (supports both dict and sqlite3.Row).
    
    Args:
        row: Dictionary or sqlite3.Row object
        key: Column/key name
        default: Default value if key not found
        
    Returns:
        Value or default
    """
    try:
        # Try dict-style get method first
        if hasattr(row, 'get'):
            return row.get(key, default)
        # Try direct indexing (works for sqlite3.Row)
        elif hasattr(row, '__getitem__') and hasattr(row, 'keys'):
            if key in row.keys():
                return row[key]
            return default
        # Fallback for other dict-like objects
        else:
            return row[key] if key in row else default
    except (KeyError, IndexError, TypeError):
        return default


def get_reservations_by_period(reservations: List[Any]) -> Tuple[Dict, Dict, Dict]:
    """
    Aggregate reservations by month, week, and day.
    
    Args:
        reservations: List of reservation records (dict or sqlite3.Row)
    
    Returns:
        Tuple of (monthly_counts, weekly_counts, daily_counts)
    """
    monthly = defaultdict(int)
    weekly = defaultdict(int)
    daily = defaultdict(int)
    
    for res in reservations:
        try:
            # Get time_slot value safely
            time_slot = row_get(res, "time_slot", "")
            if not time_slot:
                continue
            
            # Parse datetime
            dt = datetime.strptime(time_slot, "%Y-%m-%d %H:%M")
            
            # Monthly aggregation (YYYY-MM)
            month_key = dt.strftime("%Y-%m")
            monthly[month_key] += 1
            
            # Weekly aggregation (YYYY-Www)
            week_key = dt.strftime("%Y-W%U")
            weekly[week_key] += 1
            
            # Daily aggregation (YYYY-MM-DD)
            day_key = dt.strftime("%Y-%m-%d")
            daily[day_key] += 1
            
        except (ValueError, TypeError, AttributeError) as e:
            # Skip rows with invalid/missing time_slot
            continue
    
    return dict(monthly), dict(weekly), dict(daily)


def export_reports_to_pdf(
    monthly: Dict[str, int],
    weekly: Dict[str, int],
    daily: Dict[str, int],
    output_path: str
) -> bool:
    """
    Export reservation statistics to PDF.
    
    Args:
        monthly: Monthly reservation counts
        weekly: Weekly reservation counts
        daily: Daily reservation counts
        output_path: Path to save PDF file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors as rl_colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=rl_colors.HexColor('#047857'),
            spaceAfter=30,
            alignment=TA_CENTER,
        )
        story.append(Paragraph("Reservation Statistics Report", title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Monthly statistics
        story.append(Paragraph("Monthly Reservations", styles['Heading2']))
        if monthly:
            monthly_data = [["Month", "Count"]]
            for month in sorted(monthly.keys()):
                monthly_data.append([month, str(monthly[month])])
            monthly_data.append(["TOTAL", str(sum(monthly.values()))])
            
            monthly_table = Table(monthly_data)
            monthly_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), rl_colors.HexColor('#047857')),
                ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), rl_colors.HexColor('#E8F5E9')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, rl_colors.grey),
            ]))
            story.append(monthly_table)
        else:
            story.append(Paragraph("No monthly data available", styles['Normal']))
        
        story.append(Spacer(1, 0.3 * inch))
        
        # Weekly statistics
        story.append(Paragraph("Weekly Reservations (Last 12 weeks)", styles['Heading2']))
        if weekly:
            sorted_weeks = sorted(weekly.keys())[-12:]  # Last 12 weeks
            weekly_data = [["Week", "Count"]]
            for week in sorted_weeks:
                weekly_data.append([week, str(weekly[week])])
            weekly_data.append(["TOTAL", str(sum(weekly[w] for w in sorted_weeks))])
            
            weekly_table = Table(weekly_data)
            weekly_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), rl_colors.HexColor('#047857')),
                ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), rl_colors.HexColor('#E8F5E9')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, rl_colors.grey),
            ]))
            story.append(weekly_table)
        else:
            story.append(Paragraph("No weekly data available", styles['Normal']))
        
        story.append(PageBreak())
        
        # Daily statistics (last 30 days)
        story.append(Paragraph("Daily Reservations (Last 30 days)", styles['Heading2']))
        if daily:
            sorted_days = sorted(daily.keys())[-30:]  # Last 30 days
            daily_data = [["Date", "Count"]]
            for day in sorted_days:
                daily_data.append([day, str(daily[day])])
            daily_data.append(["TOTAL", str(sum(daily[d] for d in sorted_days))])
            
            daily_table = Table(daily_data)
            daily_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), rl_colors.HexColor('#047857')),
                ('TEXTCOLOR', (0, 0), (-1, 0), rl_colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), rl_colors.HexColor('#E8F5E9')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, rl_colors.grey),
            ]))
            story.append(daily_table)
        else:
            story.append(Paragraph("No daily data available", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        return True
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return False


def get_default_export_path() -> str:
    """Get default path for PDF export."""
    try:
        from core.storage import get_data_dir
        data_dir = get_data_dir()
        return os.path.join(data_dir, f"reservations_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    except:
        # Fallback to current directory
        return f"reservations_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
