#!/usr/bin/env python3

"""sr2t Nmap parser"""

import csv
import os
import sys
from dataclasses import dataclass

from prettytable import PrettyTable


@dataclass
class NmapParams:
    """Nmap parameters for parsing"""

    var1: str
    var2: list
    var3: str
    host: object
    addr: str
    args: object


def nmap_loopy(params: NmapParams):
    """Loop to collect addresses or port IDs based on protocol and state"""
    for port in params.host.findall("ports/port"):
        if port.get("protocol") == params.var3:
            portid = port.get("portid")
            for root_state in port.findall("state"):
                if root_state.get("state") == params.args.nmap_state:
                    if params.var1 == "address":
                        params.var2.append(params.addr)
                    elif params.var1 == "portid":
                        params.var2.append(portid)
                    else:
                        sys.exit(1)


def nmap_service_loopy(host, args, addr, data_nmap_services):
    """Loop to collect service information from ports"""
    for port in host.findall("ports/port"):
        portid = port.get("portid")
        for root_state in port.findall("state"):
            if root_state.get("state") == args.nmap_state:
                for service in port.findall("service"):
                    proto = port.get("protocol")
                    service_name = service.get("name")
                    state = root_state.get("state")
                    data_nmap_services.append(
                        [addr, portid, proto, service_name, state]
                    )


def extract_host_data(host, args):
    """Extract address and port data from a host element"""
    addr = host.find("address").get("addr")

    list_addr_tcp = []
    list_portid_tcp = []
    list_addr_udp = []
    list_portid_udp = []

    param_sets = []
    for proto, addr_list, portid_list in [
        ("tcp", list_addr_tcp, list_portid_tcp),
        ("udp", list_addr_udp, list_portid_udp),
    ]:
        for var1, var2 in [("address", addr_list), ("portid", portid_list)]:
            param_sets.append(
                NmapParams(
                    var1=var1, var2=var2, var3=proto, host=host, addr=addr, args=args
                )
            )

    for params in param_sets:
        nmap_loopy(params)

    return addr, list_addr_tcp, list_portid_tcp, list_addr_udp, list_portid_udp


def build_protocol_table(data, ports):
    """Build PrettyTable and CSV array for TCP/UDP data"""
    table = PrettyTable()
    header = ["ip address"] + ports
    table.field_names = header
    table.align["ip address"] = "l"

    csv_array = []
    for ip_address, open_ports in data:
        row = [ip_address]
        row.extend("X" if str(port) in open_ports else "" for port in ports)
        table.add_row(row)
        csv_array.append(row)

    return table, csv_array, header


def build_services_table(data_nmap_services):
    """Build PrettyTable and CSV array for service data"""
    header = ["ip address", "port", "proto", "service", "state"]
    table = PrettyTable()
    table.field_names = header
    table.align = "l"

    csv_array = []
    for row in data_nmap_services:
        table.add_row(row)
        csv_array.append(row)

    return table, csv_array, header


def export_csv(filename, header, data):
    """Export data to a CSV file"""
    with open(filename, "w", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header)
        for row in data:
            csvwriter.writerow(row)


def export_xlsx(workbook, sheet_name, header, data):
    """Export data to an XLSX worksheet"""
    bold = workbook.add_format({"bold": True})
    bold.set_text_wrap()
    xlsx_header = [{"header_format": bold, "header": f"{title}"} for title in header]

    worksheet = workbook.add_worksheet(sheet_name)
    worksheet.set_tab_color("purple")
    worksheet.set_column(0, 0, 15)
    worksheet.add_table(
        0,
        0,
        len(data),
        len(data[0]) - 1,
        {
            "data": data,
            "style": "Table Style Light 9",
            "header_row": True,
            "columns": xlsx_header,
        },
    )
    worksheet.freeze_panes(0, 1)


def export_all(
    args,
    workbook,
    csv_array_tcp,
    header_tcp,
    csv_array_udp,
    header_udp,
    csv_array_services,
    header_services,
):
    """Handles CSV and XLSX export for all tables"""

    if args.output_csv:
        base = os.path.splitext(args.output_csv)[0]
        if csv_array_tcp:
            export_csv(f"{base}_nmap_tcp.csv", header_tcp, csv_array_tcp)
        if csv_array_udp:
            export_csv(f"{base}_nmap_udp.csv", header_udp, csv_array_udp)
        if csv_array_services and args.nmap_services == 1:
            export_csv(f"{base}_nmap_services.csv", header_services, csv_array_services)

    if args.output_xlsx:
        if csv_array_tcp:
            export_xlsx(workbook, "Nmap TCP", header_tcp, csv_array_tcp)
        if csv_array_udp:
            export_xlsx(workbook, "Nmap UDP", header_udp, csv_array_udp)
        if csv_array_services and args.nmap_services == 1:
            export_xlsx(workbook, "Nmap Services", header_services, csv_array_services)


def nmap_parser(args, root, workbook):
    """Main Nmap parser function"""

    data_nmap_tcp = []
    data_nmap_udp = []
    data_nmap_services = []

    # Parse hosts
    for element in root:
        for host in element.findall("host"):
            addr, list_addr_tcp, list_portid_tcp, list_addr_udp, list_portid_udp = (
                extract_host_data(host, args)
            )
            nmap_service_loopy(host, args, addr, data_nmap_services)

            if list_addr_tcp:
                data_nmap_tcp.append([list_addr_tcp[0], list_portid_tcp])
            if list_addr_udp:
                data_nmap_udp.append([list_addr_udp[0], list_portid_udp])

    # Get sorted port lists
    tcp_ports = (
        sorted({int(port) for _, ports in data_nmap_tcp for port in ports})
        if data_nmap_tcp
        else []
    )
    udp_ports = (
        sorted({int(port) for _, ports in data_nmap_udp for port in ports})
        if data_nmap_udp
        else []
    )

    # Build tables
    my_nmap_tcp_table, csv_array_tcp, header_tcp = build_protocol_table(
        data_nmap_tcp, tcp_ports
    )
    my_nmap_udp_table, csv_array_udp, header_udp = build_protocol_table(
        data_nmap_udp, udp_ports
    )
    my_nmap_services_table, csv_array_services, header_services = build_services_table(
        data_nmap_services
    )

    # Host lists
    my_nmap_host_list_tcp = (
        [ip for ip, _ in data_nmap_tcp] if args.nmap_host_list else []
    )
    my_nmap_host_list_udp = (
        [ip for ip, _ in data_nmap_udp] if args.nmap_host_list else []
    )

    # Export
    export_all(
        args,
        workbook,
        csv_array_tcp,
        header_tcp,
        csv_array_udp,
        header_udp,
        csv_array_services,
        header_services,
    )
    # Return results
    return (
        my_nmap_tcp_table if csv_array_tcp else [],
        my_nmap_udp_table if csv_array_udp else [],
        my_nmap_services_table if csv_array_services else [],
        my_nmap_host_list_tcp,
        my_nmap_host_list_udp,
        workbook,
    )
