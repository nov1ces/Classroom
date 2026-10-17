#!/usr/bin/env python3
"""Independent calculations from visually transcribed source conditions.

This script does not read a manuscript, an existing answer ledger, or lecture PDFs.
All time units are explicit. Textbook simplifications are named in each result.
Run from any directory; results.json is written beside this file.
"""
from __future__ import annotations

from collections import deque
from fractions import Fraction
import hashlib
import ipaddress as ip
import json
import math
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent


def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\0"
    value = sum(struct.unpack(f"!{len(data)//2}H", data))
    while value >> 16:
        value = (value & 0xFFFF) + (value >> 16)
    return (~value) & 0xFFFF


def packet(hexadecimal: str) -> dict:
    b = bytes.fromhex(hexadecimal)
    ihl = (b[0] & 15) * 4
    t = b[ihl:]
    total = int.from_bytes(b[2:4], "big")
    tcp_hl = (t[12] >> 4) * 4
    out = {
        "first_40_bytes": b.hex(" "), "version": b[0] >> 4,
        "ip_header_bytes": ihl, "total_bytes": total,
        "identification_hex": f"{int.from_bytes(b[4:6], 'big'):04x}",
        "ttl": b[8], "protocol": b[9],
        "src": str(ip.ip_address(b[12:16])),
        "dst": str(ip.ip_address(b[16:20])),
        "src_port": int.from_bytes(t[0:2], "big"),
        "dst_port": int.from_bytes(t[2:4], "big"),
        "seq": int.from_bytes(t[4:8], "big"),
        "ack": int.from_bytes(t[8:12], "big"),
        "tcp_header_bytes": tcp_hl, "flags_hex": f"{t[13]:02x}",
        "SYN": bool(t[13] & 2), "ACK": bool(t[13] & 16),
        "data_bytes": total - ihl - tcp_hl,
        "ethernet_padding_bytes": max(0, 46 - total),
        "ip_header_checksum_remainder": checksum(b[:ihl]),
        "full_tcp_header_present_in_excerpt": len(t) >= tcp_hl,
    }
    # A 40-B excerpt is enough to check the whole TCP checksum only for a
    # 40-B IP packet. The SYN options and packet 4's payload are not supplied.
    if total == len(b):
        pseudo = b[12:20] + bytes([0, b[9]]) + (total - ihl).to_bytes(2, "big")
        out["tcp_checksum_remainder"] = checksum(pseudo + t)
    return out


def check_2012() -> dict:
    # Transcribed from book PDF 266, enlarged and opened for checksum digits.
    raw = [
        "45 00 00 30 01 9b 40 00 80 06 1d e8 c0 a8 00 08 d3 44 47 50 "
        "0b d9 13 88 84 6b 41 c5 00 00 00 00 70 02 43 80 5d b0 00 00",
        "45 00 00 30 00 00 40 00 31 06 6e 83 d3 44 47 50 c0 a8 00 08 "
        "13 88 0b d9 e0 59 9f ef 84 6b 41 c6 70 12 16 d0 37 e1 00 00",
        "45 00 00 28 01 9c 40 00 80 06 1d ef c0 a8 00 08 d3 44 47 50 "
        "0b d9 13 88 84 6b 41 c6 e0 59 9f f0 50 10 43 80 2b 32 00 00",
        "45 00 00 38 01 9d 40 00 80 06 1d de c0 a8 00 08 d3 44 47 50 "
        "0b d9 13 88 84 6b 41 c6 e0 59 9f f0 50 18 43 80 e6 55 00 00",
        "45 00 00 28 68 11 40 00 31 06 06 7a d3 44 47 50 c0 a8 00 08 "
        "13 88 0b d9 e0 59 9f f0 84 6b 41 d6 50 10 16 d0 57 d2 00 00",
    ]
    ps = [packet(x) for x in raw]
    original = packet(
        "45 00 00 28 68 11 40 00 40 06 ec ad d3 44 47 50 ca 76 01 06 "
        "13 88 a1 08 e0 59 9f f0 84 6b 41 d6 50 10 16 d0 b7 d6 00 00"
    )
    sent_h = [i+1 for i, p in enumerate(ps) if p["src"] == "192.168.0.8"]
    handshake = [i+1 for i, p in enumerate(ps[:3])
                 if p["SYN"] or (p["ACK"] and p["data_bytes"] == 0)]
    padding = [i+1 for i, p in enumerate(ps) if p["ethernet_padding_bytes"]]
    confirmed = ps[4]["ack"] - (ps[0]["seq"] + 1)
    hops = original["ttl"] - ps[4]["ttl"]
    assert sent_h == [1, 3, 4] and handshake == [1, 2, 3]
    assert padding == [3, 5] and confirmed == 16 and hops == 15
    assert ps[2]["tcp_checksum_remainder"] == 0
    assert ps[4]["tcp_checksum_remainder"] == 0
    # IPv4 checksums in these transcribed source rows are not all valid; do
    # not silently fix nonessential source checksum bytes using the answers.
    return {"packets": ps, "server_original": original,
            "H_sent": sent_h, "handshake": handshake, "padding": padding,
            "confirmed_application_bytes": confirmed, "routers": hops,
            "book_answer_agrees": True,
            "limits": ["Only the first 40 B are supplied: packet 1/2 TCP options and packet 4 data are absent.",
                       "Source checksum bytes are retained verbatim; unused inconsistencies are reported."]}


def check_2013() -> dict:
    routes = [
        (ip.ip_network("153.14.5.0/24"), "153.14.3.2", "S0"),
        (ip.ip_network("194.17.20.0/23"), "194.17.24.2", "S1"),
        (ip.ip_network("194.17.20.128/25"), None, "E0"),
    ]
    dest = ip.ip_address("194.17.20.200")
    matching = [(str(n), hop, iface) for n, hop, iface in routes if dest in n]
    best = max((r for r in routes if dest in r[0]), key=lambda r: r[0].prefixlen)
    # The /23 is a covering aggregate with a more-specific direct exception,
    # not an exact collapse of just /25 and /24.
    checks = {"153.14.5.1": "S0", "153.14.5.200": "S0",
              "194.17.20.1": "S1", "194.17.20.200": "E0",
              "194.17.21.1": "S1"}
    for addr, iface in checks.items():
        x = ip.ip_address(addr)
        selected = max((r for r in routes if x in r[0]), key=lambda r: r[0].prefixlen)
        assert selected[2] == iface
    assert best[2] == "E0"
    return {"routes": [{"destination": str(n), "next_hop": h, "interface": i}
                        for n, h, i in routes], "matching_routes": matching,
            "selected_interface": best[2], "route_count": len(routes),
            "protocol": "BGP (BGP-4), over TCP", "book_answer_agrees": True}


def check_2016() -> dict:
    buffer_bytes, mss, isn, rtt_ms = 20*1024, 1024, 100, 200
    cwnd = 1
    delivered = 0
    rounds = []
    while delivered < buffer_bytes:
        before = delivered
        rwnd_segments = (buffer_bytes - delivered) // mss
        sent_segments = min(cwnd, rwnd_segments)
        delivered += sent_segments*mss
        rounds.append({"round": len(rounds)+1, "cwnd_before_MSS": cwnd,
                       "rwnd_before_B": buffer_bytes-before,
                       "sent_segments": sent_segments, "cumulative_bytes": delivered,
                       "end_ms": (len(rounds)+1)*rtt_ms})
        # The threshold is 32 MSS and never reached in this 20-segment file.
        cwnd += sent_segments
    ack8_rwnd = buffer_bytes - 8*mss
    ack8_cwnd = (1+8)*mss
    seq = isn+1+buffer_bytes
    rate_bps = Fraction(buffer_bytes*8*1000, len(rounds)*rtt_ms)
    close_ms = Fraction(3,2)*rtt_ms
    assert [r["sent_segments"] for r in rounds] == [1,2,4,8,5]
    assert (ack8_rwnd, ack8_cwnd, seq, rate_bps, close_ms) == (12288,9216,20581,163840,300)
    return {"second_handshake": {"SYN": 1,"ACK": 1,"ack": isn+1},
            "after_ack_8": {"rwnd_B": ack8_rwnd,"cwnd_B": ack8_cwnd,
                            "sending_window_B": min(ack8_rwnd,ack8_cwnd)},
            "rounds": rounds, "next_seq_at_zero_window": seq,
            "elapsed_ms_from_first_data_to_zero_window": len(rounds)*rtt_ms,
            "average_bps": int(rate_bps), "average_kbps_decimal": float(rate_bps/1000),
            "S_shortest_release_ms": int(close_ms), "book_answer_agrees": True,
            "limits": ["Each segment is acknowledged; no receive-buffer consumption.",
                       "The shortest close combines S's ACK and FIN immediately; no extra application wait.",
                       "This is S's close time, not H3's 2MSL TIME-WAIT duration."]}


def check_2017() -> dict:
    bits, frame_B, rate, rtt_ms = 3, 1000, 100_000_000, Fraction(96,100)
    modulus, width = 1 << bits, (1 << bits)-1
    # (a): R0,1 and R1,3 are in order; R3,3 arrives while R2 is missing.
    expected_b = 0
    for seq in [0,1,3]:
        if seq == expected_b:
            expected_b = (expected_b+1)%modulus
    base_a, sent_next_a = 3, 5
    outstanding_a = (sent_next_a-base_a)%modulus
    new_frames = [((sent_next_a+i)%modulus,expected_b)
                  for i in range(width-outstanding_a)]
    # (b): cumulative ACK 2 leaves data sequence 2,3,4 outstanding. R2,2
    # is in order at A, so all retransmissions now piggyback ACK 3.
    retry = [(x,3) for x in [2,3,4]]
    td_ms = Fraction(frame_B*8*1000,rate)
    cycle_ms = td_ms+rtt_ms+td_ms  # piggyback ACK is also a full data frame
    u = min(Fraction(1),width*td_ms/cycle_ms)
    assert new_frames == [(5,2),(6,2),(7,2),(0,2),(1,2)]
    assert retry[0] == (2,3) and u == Fraction(1,2)
    return {"modulus": modulus,"GBN_max_window": width,
            "certain_received_by_B": ["S0,0","S1,0","S2,0"],
            "A_expected_B_sequence_at_a_t1": expected_b,
            "a_outstanding_sequences": [3,4],
            "a_new_frames": [f"S{x},{y}" for x,y in new_frames],
            "b_retransmissions": [f"S{x},{y}" for x,y in retry],
            "frame_send_ms": float(td_ms),"first_ACK_cycle_ms": float(cycle_ms),
            "max_utilization": float(u), "book_answer_agrees": True,
            "limits": ["RTT is used as the round-trip propagation delay in the textbook formula.",
                       "Always piggybacked ACKs occupy another 1000-B data frame; ACK serialization cannot be set to zero."]}


def check_2018() -> dict:
    tech = ip.ip_network("192.168.1.128/25")
    sales = ip.ip_network("192.168.1.0/25")
    existing_hosts = 208-129+1
    spare_hosts = tech.num_addresses-2-existing_hosts-1  # router .254
    data_total, mtu, header = 1500-20, 800, 20
    largest = ((mtu-header)//8)*8
    left, offset, fragments = data_total, 0, []
    while left:
        data = min(largest,left)
        fragments.append({"payload_B":data,"ip_total_B":data+header,
                          "offset_8B":offset//8,"MF":int(left>data)})
        offset += data
        left -= data
    assert spare_hosts == 45
    assert fragments == [{"payload_B":776,"ip_total_B":796,"offset_8B":0,"MF":1},
                         {"payload_B":704,"ip_total_B":724,"offset_8B":97,"MF":0}]
    return {"sales": str(sales),"sales_broadcast":str(sales.broadcast_address),
            "technical":str(tech),"already_assigned_hosts":existing_hosts,
            "technical_additional_hosts":spare_hosts,
            "largest_fragment_payload_B":largest,"fragments":fragments,
            "payload_conservation_B":sum(f["payload_B"] for f in fragments),
            "book_answer_agrees":True}


def check_2021() -> dict:
    mac = {"R":"00-11-22-33-44-aa","DNS":"00-11-22-33-44-bb",
           "H1":"00-11-22-33-44-cc","H2":"00-11-22-33-44-dd"}
    port = {"DNS":1,"R":2,"H2":3,"H1":4}
    broadcast = "ff-ff-ff-ff-ff-ff"
    events = [
        ("H1","*","ARP request for local DNS"),
        ("DNS","H1","ARP reply"),
        ("H1","DNS","DNS query / UDP"),
        ("DNS","H1","DNS reply / UDP"),
        ("H1","*","ARP request for gateway R"),
        ("R","H1","ARP reply"),
        ("H1","R","TCP SYN for remote Web server"),
        ("R","H1","forwarded TCP SYN+ACK"),
        ("H1","R","TCP ACK"),
        ("H1","R","first HTTP request"),
    ]
    table, trace, h2 = {}, [], []
    for sender,receiver,kind in events:
        src = mac[sender]
        dst = broadcast if receiver == "*" else mac[receiver]
        table[src] = port[sender]
        if receiver == "*" or dst not in table:
            outgoing = [p for p in [1,2,3,4] if p != port[sender]]
        else:
            outgoing = [table[dst]] if table[dst] != port[sender] else []
        e = {"kind":kind,"src":src,"dst":dst,"input_port":port[sender],
             "output_ports":outgoing,"table_after":dict(table)}
        trace.append(e)
        if port["H2"] in outgoing:
            h2.append(e)
    assert table == {mac["H1"]:4,mac["DNS"]:1,mac["R"]:2}
    assert len(h2) == 2 and all(e["dst"] == broadcast for e in h2)
    return {"encapsulation":"DNS -> UDP -> IPv4 -> Ethernet II",
            "trace":trace,"final_switch_table":table,"H2_received":h2,
            "H2_minimum_frames_in_textbook_flow":len(h2),"book_answer_agrees":True,
            "limits":["A fresh DNS lookup is the textbook's intended workflow; an empty DNS cache is not an explicit stem condition.",
                      "No switch aging or unrelated traffic is inserted; the stem explicitly excludes unrelated traffic.",
                      "CSMA/CD is a medium-access algorithm, not the Ethernet II frame format; the textbook itself adds this correction."]}


def check_2023() -> dict:
    mss, size, isn, threshold, rtt_ms = 1000, 18000, 100, 4, 10
    remain, cwnd, rounds = size//mss, 1, []
    while remain:
        sent = min(remain,cwnd)
        remain -= sent
        rounds.append({"round":len(rounds)+1,"cwnd_MSS":cwnd,"sent_segments":sent,
                       "total_segments_sent":size//mss-remain,
                       "end_ms_after_data_start":(len(rounds)+1)*rtt_ms})
        cwnd = min(cwnd*2,threshold) if cwnd < threshold else cwnd+1
    data_ms = len(rounds)*rtt_ms
    elapsed_ms = rtt_ms+data_ms
    # 2101 acknowledges the first two 1000-B segments. The first ACK of
    # round 2 changes cwnd 2 -> 3; 7101 finishes round 3 (7 segments).
    ack_2101 = {"segments_confirmed":(2101-(isn+1))//mss,"cwnd_MSS":1+2}
    ack_7101 = {"segments_confirmed":(7101-(isn+1))//mss,"cwnd_MSS":5}
    avg_bps = Fraction(size*8*1000,elapsed_ms)
    assert [r["sent_segments"] for r in rounds] == [1,2,4,5,6]
    assert (elapsed_ms,avg_bps) == (60,2400000)
    return {"control_connection":"persistent during FTP session",
            "data_connection":"nonpersistent, created for this transfer",
            "login_connection":"control", "first_data_seq":isn+1,
            "second_close_ACK":isn+1+size+1,
            "ACK_2101":ack_2101,"ACK_7101":ack_7101,"rounds":rounds,
            "data_transfer_ms":data_ms,"handshake_ms":rtt_ms,
            "elapsed_ms":elapsed_ms,"average_application_bps":int(avg_bps),
            "average_application_Bps":int(avg_bps/8),"book_answer_agrees":True,
            "limits":["The round-based textbook congestion-avoidance model grows by 1 MSS per RTT; it is not an exact implementation trace.",
                      "ACK 2101 occurs within the second round: cwnd is 3 MSS there, not the round-end value 4 MSS.",
                      "The measured interval starts with the data-connection SYN; login/control connection and connection teardown are outside it."]}


def bfs(edges, start):
    graph = {x:set() for edge in edges for x in edge}
    for a,b in edges:
        graph[a].add(b); graph[b].add(a)
    distance = {start:0}
    queue = deque([start])
    while queue:
        a = queue.popleft()
        for b in sorted(graph[a]):
            if b not in distance:
                distance[b] = distance[a]+1
                queue.append(b)
    return distance


def check_2024() -> dict:
    edges = [("R11","R12"),("R12","R13"),("R11","R14"),
             ("R14","R15"),("R15","R16"),("R13","R15")]
    extra = ("R13","R16")
    variants = {}
    for name,es in [("book",edges),("community_exam",edges+[extra])]:
        nets = {}
        for root,net in [("R14","210.2.3.0/24"),("R16","210.2.4.0/24")]:
            ds = bfs(es,root)
            last_ms = (max(ds.values())-1)*30000
            stages = {str(t):sorted(n for n,d in ds.items() if d <= t//30000+1)
                      for t in range(0,int(last_ms)+1,30000)}
            nets[net] = {"router_hop_distances_from_direct_router":ds,
                         "known_at_ms_since_initial_exchange":stages,
                         "all_correct_after_ms":last_ms}
        variants[name] = {"edges":es,"networks":nets}
    shortest_paths = {"R11":["AS2","AS8","AS19"],
                      "R12":["AS3","AS7","AS11","AS19"],
                      "R13":["AS4","AS10","AS19"]}
    min_as = min(map(len,shortest_paths.values()))
    eligible = [r for r,p in shortest_paths.items() if len(p)==min_as]
    selections = {}
    for start in ["R14","R15"]:
        ds = bfs(edges,start)
        selections[start] = min(eligible,key=lambda r:ds[r])
    assert selections == {"R14":"R11","R15":"R13"}
    for v in variants.values():
        assert [n["all_correct_after_ms"] for n in v["networks"].values()] == [30000,60000]
    return {"AS4_IGP":"OSPF","AS3_minimum_TTL":15+1,
            "topology_variants":variants,"external_session":"eBGP",
            "reachability_message":"UPDATE","internal_session":"iBGP",
            "AS_paths":shortest_paths,"shortest_AS_path_candidates":eligible,
            "selected_BGP_next_hops":selections,"book_answer_agrees":True,
            "limits":["The community original image has R13--R16, absent in the book question and solution diagrams.",
                      "The two final propagation times agree, but their intermediate learned-router sets differ.",
                      "The first distance-vector exchange occurs at t=0; it is not charged another 30 s."]}


def check_2025() -> dict:
    altitude_km, c_km_s, rate, file_B, frame_B = 36000,300000,200000,4000,1500
    propagation = Fraction(2*altitude_km,c_km_s)
    file_send = Fraction(file_B*8,rate)
    frame_send = Fraction(frame_B*8,rate)
    cycle = frame_send+2*propagation
    min_window = math.ceil(Fraction(4,5)*cycle/frame_send)
    bits = (min_window+1-1).bit_length()
    utilization = {str(w):float(min(Fraction(1),w*frame_send/cycle)) for w in [7,8,9]}
    management = ip.ip_interface("10.10.10.33/26").network
    work = ip.ip_network("10.10.10.64/26")
    life = ip.ip_network("10.10.10.128/25")
    nets = [management,work,life]
    assert sum(x.num_addresses for x in nets) == 256
    assert all(not a.overlaps(b) for i,a in enumerate(nets) for b in nets[i+1:])
    assert (propagation,file_send,file_send+propagation,min_window,bits) == (Fraction(6,25),Fraction(4,25),Fraction(2,5),8,4)
    return {"propagation_one_way_ms":int(propagation*1000),
            "bottleneck_bps":rate,"file_serialization_ms":int(file_send*1000),
            "ideal_upload_lower_bound_ms":int((file_send+propagation)*1000),
            "frame_serialization_ms":int(frame_send*1000),"ACK_cycle_ms":int(cycle*1000),
            "minimum_window":min_window,"minimum_sequence_bits":bits,
            "utilization_by_window":utilization,
            "subnets":{"work":str(work),"management":str(management),"life":str(life)},
            "usable_addresses":{str(n):n.num_addresses-2 for n in nets},
            "one_4000_B_Gigabit_serialization_us":32,
            "book_answer_agrees":True,
            "limits":["The 400-ms textbook answer neglects LAN serialization as well as propagation; the stem expressly neglects LAN propagation only.",
                      "400 ms is an ideal lower bound/approximation. A strict store-and-forward Ethernet completion time needs additional framing/forwarding assumptions.",
                      "SLP ACK length is expressly negligible, unlike the 2017 piggybacked data ACK.",
                      "Satellite altitude is used as both ground-to-satellite leg lengths in the textbook geometric model."]}


def main():
    calculations = {"2012q47":check_2012(),"2013q47":check_2013(),
                    "2016q41":check_2016(),"2017q47":check_2017(),
                    "2018q47":check_2018(),"2021q47":check_2021(),
                    "2023q47":check_2023(),"2024q47":check_2024(),
                    "2025q47":check_2025()}
    result = {"scope":"nine complete CN comprehensive questions; source calculations only",
              "source":"conditions transcribed from the actually opened original textbook and community PDF images",
              "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "all_nine_book_answer_checks_pass":all(c["book_answer_agrees"] for c in calculations.values()),
              "calculations":calculations}
    (HERE/"results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"all_nine_book_answer_checks_pass":result["all_nine_book_answer_checks_pass"],
                      "questions":list(calculations)},ensure_ascii=False))


if __name__ == "__main__":
    main()
