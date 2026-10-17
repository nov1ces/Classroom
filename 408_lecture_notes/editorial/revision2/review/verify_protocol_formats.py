"""Independent byte-level checks for the revision-2 CN header diagrams.

The expected bit widths come from the actually inspected textbook headers.
The examples below are original review witnesses, not additional exam questions.
"""
import hashlib
import ipaddress
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def checksum(data):
    data += b"\0" * (len(data) % 2)
    total = sum(int.from_bytes(data[i:i + 2], "big") for i in range(0, len(data), 2))
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


def pseudo(src, dst, protocol, length):
    return src + dst + struct.pack("!BBH", 0, protocol, length)


def main():
    path = ROOT / "figures/CN_model_data.json"
    formats = json.loads(path.read_text())["protocol_formats"]
    expected = {
        "ipv4": [[4, 4, 8, 16], [16, 3, 13], [8, 8, 16], [32], [32]],
        "tcp": [[16, 16], [32], [32], [4, 6, 1, 1, 1, 1, 1, 1, 16], [16, 16]],
        "udp": [[16, 16], [16, 16]],
    }
    for name, rows in expected.items():
        actual = [[width for _, width in row] for row in formats[name]["rows"]]
        assert actual == rows
        assert all(sum(row) == 32 for row in actual)
        assert sum(map(sum, actual)) // 8 == formats[name]["fixed_bytes"]
    assert formats["ipv4"]["length_unit_bytes"] == 4
    assert formats["ipv4"]["total_length_unit_bytes"] == 1
    assert formats["ipv4"]["fragment_offset_unit_bytes"] == 8
    assert formats["tcp"]["data_offset_unit_bytes"] == 4
    assert formats["udp"]["length_unit_bytes"] == 1

    src = ipaddress.ip_address("192.0.2.1").packed
    dst = ipaddress.ip_address("198.51.100.2").packed
    data = b"ABCDE"  # odd byte count; the zero pad must not be transmitted
    udp_length = 8 + len(data)
    udp_zero = struct.pack("!HHHH", 12345, 53, udp_length, 0) + data
    udp_sum = checksum(pseudo(src, dst, 17, udp_length) + udp_zero)
    udp = udp_zero[:6] + struct.pack("!H", udp_sum or 0xFFFF) + data
    assert len(udp) == 13 and checksum(pseudo(src, dst, 17, len(udp)) + udp) == 0

    options = b"\x01\x01\x00\x00"
    ip_length = 20 + len(options) + len(udp)
    ip_zero = struct.pack("!BBHHHBBH4s4s", 0x46, 0, ip_length, 0x1234,
                          0, 64, 17, 0, src, dst) + options
    ip_header = ip_zero[:10] + struct.pack("!H", checksum(ip_zero)) + ip_zero[12:]
    packet = ip_header + udp
    ihl_bytes = (packet[0] & 15) * 4
    assert ihl_bytes == 24 and len(packet) == 37
    assert checksum(ip_header) == 0
    assert int.from_bytes(packet[2:4], "big") - ihl_bytes == 13
    assert int.from_bytes(packet[ihl_bytes + 4:ihl_bytes + 6], "big") == 13
    assert packet[ihl_bytes + 8:] == data
    altered_payload = bytearray(packet)
    altered_payload[-1] ^= 1
    assert checksum(bytes(altered_payload[:ihl_bytes])) == 0
    assert checksum(pseudo(src, dst, 17, 13) + bytes(altered_payload[ihl_bytes:])) != 0
    changed_ip = bytearray(ip_header)
    changed_ip[8] -= 1
    assert checksum(bytes(changed_ip)) != 0
    assert checksum(pseudo(src, ipaddress.ip_address("198.51.100.3").packed, 17, 13) + udp) != 0

    # A zero computed UDP checksum is transmitted as FFFF; a field of 0000
    # has the separate IPv4 "checksum not used" meaning.
    zero_base = struct.pack("!HHHH", 1000, 2000, 10, 0)
    last_word = checksum(pseudo(src, dst, 17, 10) + zero_base + b"\0\0")
    zero_calculated = zero_base + struct.pack("!H", last_word)
    assert checksum(pseudo(src, dst, 17, 10) + zero_calculated) == 0
    wire_zero = zero_base[:6] + b"\xff\xff" + struct.pack("!H", last_word)
    assert checksum(pseudo(src, dst, 17, 10) + wire_zero) == 0

    tcp_data = b"abcde"
    tcp_zero = struct.pack("!HHIIBBHHH", 12345, 80, 0x10203040,
                           0x50607080, 5 << 4, 0x18, 4096, 0, 0) + tcp_data
    tcp_sum = checksum(pseudo(src, dst, 6, len(tcp_zero)) + tcp_zero)
    tcp = tcp_zero[:16] + struct.pack("!H", tcp_sum) + tcp_zero[18:]
    assert (tcp[12] >> 4) * 4 == 20
    assert tcp[13] & 0x3F == 0x18 and tcp[12] & 15 == 0
    assert int.from_bytes(tcp[14:16], "big") == 4096
    assert checksum(pseudo(src, dst, 6, len(tcp)) + tcp) == 0
    assert checksum(pseudo(src, dst, 17, len(tcp)) + tcp) != 0
    assert 100 - 4 * 6 - 4 * 6 == 52

    eth = formats["ethernet_ii"]
    assert eth["header_bytes"] == 6 + 6 + 2 == 14
    assert eth["frame_bytes"] == [14 + 46 + 4, 14 + 1500 + 4]
    assert eth["preamble_bytes"] == 7 and eth["sfd_bytes"] == 1
    assert eth["ifg_bit_times"] == 96 and eth["mtu_bytes"] == 1500
    minimum_cycle_bits = (7 + 1 + 64) * 8 + 96
    assert minimum_cycle_bits == 672
    assert max(0, 46 - 40) == 6
    assert eth["fcs_scope"] == ["目的MAC", "源MAC", "类型", "数据及填充"]
    for name in ["ipv4", "tcp", "udp"]:
        assert formats[name]["pseudoheader_transmitted"] is False

    result = {
        "scope": "protocol bit/byte boundaries, checksum coverage, and mechanism only; no layout acceptance",
        "expected_row_widths_from_original_book": expected,
        "review_witness_udp": {"payload_bytes": 5, "udp_bytes": len(udp),
            "IHL": 6, "ip_header_bytes": ihl_bytes, "ip_total_bytes": len(packet),
            "udp_checksum_hex": f"{udp_sum:04X}",
            "ip_checksum_hex": ip_header[10:12].hex().upper(),
            "odd_padding_transmitted": False,
            "mutations_detected": ["payload changes UDP but not IPv4 checksum", "TTL invalidates IPv4 checksum", "pseudo-destination change invalidates UDP checksum", "protocol17 pseudoheader invalidates TCP checksum"],
            "computed_zero_udp_transmitted_as": "FFFF"},
        "review_witness_tcp": {"header_bytes": 20, "segment_bytes": len(tcp),
            "flags": "PSH+ACK", "window_bytes": 4096,
            "checksum_hex": f"{tcp_sum:04X}"},
        "Ethernet_II": {"frame_bytes": [64, 1518], "MTU": 1500,
            "minimum_wire_cycle_bits_in_stated_model": minimum_cycle_bits},
        "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [path, *sorted((ROOT / "manuscript/CN").glob("*.md")),
                      *[ROOT / "figures" / f"{stem}.{ext}" for stem in
                        ["CN16_ipv4_header", "CN17_tcp_header", "CN18_udp_header", "CN19_ethernet_frame"]
                        for ext in ["svg", "png"]]]},
    }
    (OUT / "independent_protocol_results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Independent CN bit/byte/serialization/checksum-coverage checks passed")


if __name__ == "__main__":
    main()
