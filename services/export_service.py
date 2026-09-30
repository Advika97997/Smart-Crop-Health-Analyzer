from __future__ import annotations

import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from config.settings import EXPORT_DIR
from core.helpers import export_file_name


class ExportService:
    HEADERS = ['ID', 'Crop', 'Image Path', 'Status', 'Health Score', 'Green %', 'Disease %', 'Edge %', 'Notes', 'Analyzed On']

    @classmethod
    def export_csv(cls, records: list[dict]) -> Path:
        path = EXPORT_DIR / export_file_name('analysis_history', 'csv')
        with path.open('w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(cls.HEADERS)
            for row in records:
                writer.writerow([
                    row['result_id'], row['crop_name'], row['image_path'], row['health_status'],
                    row['health_score'], row['green_percentage'], row['disease_area_percentage'],
                    row['edge_density'], row.get('notes', ''), row['analyzed_on'],
                ])
        return path

    @classmethod
    def export_pdf(cls, records: list[dict]) -> Path:
        path = EXPORT_DIR / export_file_name('analysis_history', 'pdf')
        doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
        styles = getSampleStyleSheet()
        story = [Paragraph('Crop Health Analyzer – Analysis History Report', styles['Title']), Spacer(1, 12)]
        rows = [cls.HEADERS]
        for row in records:
            rows.append([
                row['result_id'], row['crop_name'], row['image_path'][-28:], row['health_status'],
                row['health_score'], row['green_percentage'], row['disease_area_percentage'],
                row['edge_density'], (row.get('notes') or '')[:20], str(row['analyzed_on'])[:19],
            ])
        table = Table(rows, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d6a4f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#eef7f0')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(table)
        doc.build(story)
        return path
