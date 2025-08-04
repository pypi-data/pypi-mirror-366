#!/usr/bin/env python3

"""Shared export functions"""

import csv
import os


def export_csv(filename, header, data):
    """Export data to a CSV file"""
    with open(filename, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(data)


def export_xlsx(workbook, sheet_name, header, data):
    """Export data to an XLSX worksheet with conditional formatting"""

    bold = workbook.add_format({"bold": True, "text_wrap": True})
    bad_cell = workbook.add_format({"bg_color": "#c00000", "font_color": "#ffffff"})
    good_cell = workbook.add_format({"bg_color": "#046a38", "font_color": "#ffffff"})

    xlsx_header = [{"header_format": bold, "header": str(title)} for title in header]

    worksheet = workbook.add_worksheet(sheet_name)
    worksheet.set_tab_color("purple")
    worksheet.set_column(0, len(header) - 1, 15)
    worksheet.freeze_panes(1, 1)

    worksheet.add_table(
        0,
        0,
        len(data),
        len(header) - 1,
        {
            "data": data,
            "style": "Table Style Light 9",
            "header_row": True,
            "columns": xlsx_header,
        },
    )

    # Apply conditional formatting
    if sheet_name.lower() == "ssh2-enum-algos":
        worksheet.conditional_format(
            1,
            0,
            len(data),
            len(header) - 1,
            {"type": "cell", "criteria": "==", "value": '"X"', "format": bad_cell},
        )
        worksheet.conditional_format(
            1,
            0,
            len(data),
            len(header) - 1,
            {"type": "cell", "criteria": "==", "value": '""', "format": good_cell},
        )


def export_all(args, workbook, exportables):
    """Handles CSV and XLSX export for all provided datasets"""
    base = os.path.splitext(args.output_csv or args.output_xlsx or "nmap_export")[0]

    for label, csv_array, header in exportables:
        if args.output_csv and csv_array:
            export_csv(f"{base}_{label}.csv", header, csv_array)

        if args.output_xlsx and csv_array:
            export_xlsx(workbook, label.title(), header, csv_array)
