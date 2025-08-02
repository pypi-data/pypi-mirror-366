#!/usr/bin/env python3

"""sr2t testssl.sh parser"""

import csv
import os
from importlib import resources

import yaml
from prettytable import PrettyTable


def testssl_loopy_severity(data_testssl, subelement, id_name, value, header):
    """
    Loop through all files, match specific value in "severity" field, and print
    a custom header
    """

    if subelement["id"] == id_name and subelement["severity"] != value:
        if subelement["id"] == id_name and subelement["severity"] != "OK":
            if not data_testssl:
                data_testssl.append([subelement["ip"], subelement["port"], [header]])
            elif data_testssl:
                for host, port, finding in data_testssl:
                    if (subelement["ip"] in host) and (subelement["port"] in port):
                        finding.append(header)
                        return
                data_testssl.append([subelement["ip"], subelement["port"], [header]])


def testssl_loopy_finding(data_testssl, subelement, id_name, text, header):
    """
    Loop through all files, match specific text in "finding" field, and print a
    custom header
    """

    if subelement["id"] == "TLS1" and "not offered" in subelement["finding"]:

        # Dirty hack to filter out TLS1 if not offered - any ideas?
        return

    if subelement["id"] == "TLS1_1" and "not offered" in subelement["finding"]:

        # Dirty hack to filter out TLS1_1 if not offered - any ideas?
        return

    if subelement["id"] == id_name and text in subelement["finding"]:
        if (subelement["id"] == id_name and subelement["severity"] != "OK") or (
            id_name == "cert_commonName"
        ):
            if not data_testssl:
                data_testssl.append([subelement["ip"], subelement["port"], [header]])
            elif data_testssl:
                for host, port, finding in data_testssl:
                    if (subelement["ip"] in host) and (subelement["port"] in port):
                        finding.append(header)
                        return
                data_testssl.append([subelement["ip"], subelement["port"], [header]])


def testssl_parser(args, root, data_testssl, workbook):
    """Testssl parser"""

    with resources.files("data").joinpath("testssl.yaml").open("r") as f:
        testssl_yaml = yaml.load(f, Loader=yaml.FullLoader)

    for key, value in testssl_yaml.items():
        for element in root:
            for subelement in element:
                if value.get("key") == "finding":
                    testssl_loopy_finding(
                        data_testssl,
                        subelement,
                        value.get("id"),
                        value.get("value"),
                        value.get("column"),
                    )
                if value.get("key") == "severity":
                    testssl_loopy_severity(
                        data_testssl,
                        subelement,
                        value.get("id"),
                        value.get("not_value"),
                        value.get("column"),
                    )

    vulns = sorted({vuln for _, _, found_vuln in data_testssl for vuln in found_vuln})

    my_table = PrettyTable()
    csv_array = []
    header = ["ip address", "port"]
    header.extend(vulns)
    my_table.field_names = header
    for host, port, found_vuln in data_testssl:
        row = [host, port]
        row.extend("X" if str(vuln) in found_vuln else "" for vuln in vulns)
        my_table.add_row(row)
        csv_array.append(row)
    my_table.align["ip address"] = "l"
    my_table.align["port"] = "l"

    if args.output_csv:
        with open(
            os.path.splitext(args.output_csv)[0] + "_testssl.csv", "w", encoding="utf-8"
        ) as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["ip address"] + ["port"] + vulns)
            for row in csv_array:
                csvwriter.writerow(row)

    if args.output_xlsx:
        bold = workbook.add_format({"bold": True})
        bold.set_text_wrap()
        worksheet_testssl = workbook.add_worksheet("Testssl")
        worksheet_testssl.set_tab_color("green")
        worksheet_testssl.set_column(0, 0, 30)
        tls_bad_cell = workbook.add_format()

        # Dunno why this one doesn't work >:c
        tls_bad_cell.set_align("center")

        tls_bad_cell.set_bg_color("#c00000")
        tls_bad_cell.set_font_color("#ffffff")
        tls_bad_cell.set_border(1)
        tls_bad_cell.set_border_color("#ffffff")
        tls_good_cell = workbook.add_format()

        # Dunno why this one doesn't work >:c
        tls_good_cell.set_align("center")

        tls_good_cell.set_bg_color("#046a38")
        tls_good_cell.set_font_color("#ffffff")
        tls_good_cell.set_border(1)
        tls_good_cell.set_border_color("#ffffff")

        xlsx_header = [
            {"header_format": bold, "header": f"{title}"} for title in header
        ]
        worksheet_testssl.add_table(
            0,
            0,
            len(csv_array),
            len(csv_array[0]) - 1,
            {
                "data": csv_array,
                "style": "Table Style Light 9",
                "header_row": True,
                "columns": xlsx_header,
            },
        )
        worksheet_testssl.set_row(0, 45)
        worksheet_testssl.set_column(1, len(xlsx_header) - 1, 11)
        worksheet_testssl.conditional_format(
            0,
            1,
            len(csv_array),
            len(csv_array[0]) - 1,
            {"type": "cell", "criteria": "==", "value": '"X"', "format": tls_bad_cell},
        )
        worksheet_testssl.conditional_format(
            0,
            1,
            len(csv_array),
            len(csv_array[0]) - 1,
            {"type": "cell", "criteria": "==", "value": '""', "format": tls_good_cell},
        )
        worksheet_testssl.freeze_panes(0, 1)

    return my_table, workbook
