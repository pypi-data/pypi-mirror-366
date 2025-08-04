#!/usr/bin/env python3

"""sr2t Nmap parser"""

import sys
from dataclasses import dataclass

from prettytable import PrettyTable
from sr2t.shared.export import export_all
from sr2t.shared.utils import load_yaml


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


def extract_ssh_algorithms(host, addr, ssh_yaml, ssh_algo_data):
    """Extract SSH algorithm data from ssh2-enum-algos script if present"""

    for port in host.findall("ports/port"):
        if port.get("portid") == "22" and port.get("protocol") == "tcp":
            script = port.find("script[@id='ssh2-enum-algos']")
            if script is not None:
                ssh_algos = {}
                for table in script.findall("table"):
                    for table in script.findall("table"):
                        key = table.get("key")
                        values = [elem.text for elem in table.findall("elem")]
                        ssh_algos[key] = ", ".join(values)

                # Flag matches based on YAML
                flags = []
                for category, patterns in ssh_yaml.items():
                    algo_text = ssh_algos.get(category, "").lower()
                    for pattern in patterns:
                        flags.append("X" if pattern.lower() in algo_text else "")

                ssh_algo_data.append([addr] + flags)


def build_ssh_algo_table(ssh_algo_data, ssh_yaml, reverse_column_names):
    """Build PrettyTable and CSV array for SSH algorithm data"""

    base_header = ["ip address"]
    flag_columns = [
        f"{reverse_column_names.get(category, category).capitalize()}"
        f"{pattern.capitalize()}"
        for category, patterns in ssh_yaml.items()
        for pattern in patterns
    ]
    header = base_header + flag_columns

    # Identify columns that have at least one "X"
    used_flags = set()
    for row in ssh_algo_data:
        for idx, val in enumerate(row[1:], start=1):  # skip IP address
            if val == "X":
                used_flags.add(idx)

    # Always include "ip address" at index 0
    keep_indices = [0] + sorted(used_flags)
    filtered_header = [header[i] for i in keep_indices]

    table = PrettyTable()
    table.field_names = filtered_header
    table.align = "l"

    csv_array = []
    for row in ssh_algo_data:
        filtered_row = [row[i] for i in keep_indices]
        table.add_row(filtered_row)
        csv_array.append(filtered_row)

    return table, csv_array, filtered_header


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


def nmap_parser(args, root, workbook):
    """Main Nmap parser function"""

    data_nmap_tcp = []
    data_nmap_udp = []
    data_nmap_services = []
    ssh_algo_data = []

    # Load ssh_algo.yaml
    data_package = "sr2t.data"
    ssh_column_names = {
        "kex": "kex_algorithms",
        "cipher": "encryption_algorithms",
        "mac": "mac_algorithms",
        "compression": "compression_algorithms",  # You can omit if unused
    }
    reverse_column_names = {v: k for k, v in ssh_column_names.items()}
    ssh_yaml_raw = load_yaml(None, data_package, "nmap_ssh.yaml")
    ssh_yaml = {
        ssh_column_names[category]: patterns
        for category, patterns in ssh_yaml_raw.items()
        if category in ssh_column_names
    }

    # Parse hosts
    for element in root:
        for host in element.findall("host"):
            addr, list_addr_tcp, list_portid_tcp, list_addr_udp, list_portid_udp = (
                extract_host_data(host, args)
            )
            extract_ssh_algorithms(host, addr, ssh_yaml, ssh_algo_data)
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
    ssh_algo_table, csv_array_ssh, header_ssh = build_ssh_algo_table(
        ssh_algo_data, ssh_yaml, reverse_column_names
    )

    # Host lists
    my_nmap_host_list_tcp = (
        [ip for ip, _ in data_nmap_tcp] if args.nmap_host_list else []
    )
    my_nmap_host_list_udp = (
        [ip for ip, _ in data_nmap_udp] if args.nmap_host_list else []
    )

    exportables = [
        ("Nmap TCP", csv_array_tcp, header_tcp),
        ("Nmap UDP", csv_array_udp, header_udp),
        (
            ("Nmap Services", csv_array_services, header_services)
            if args.nmap_services == 1
            else None
        ),
        ("ssh2-enum-algos", csv_array_ssh, header_ssh),
    ]
    export_all(args, workbook, [e for e in exportables if e])

    return (
        my_nmap_tcp_table if csv_array_tcp else [],
        my_nmap_udp_table if csv_array_udp else [],
        my_nmap_services_table if csv_array_services else [],
        my_nmap_host_list_tcp,
        my_nmap_host_list_udp,
        ssh_algo_table if csv_array_ssh else [],
        workbook,
    )
