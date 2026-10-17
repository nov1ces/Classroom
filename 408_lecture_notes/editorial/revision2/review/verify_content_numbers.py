"""Independent arithmetic/state checks for revision 2, using original problem data.

This checks content only. It makes no statement about pagination or layout.
Run from any directory; results capture the current chapter SHA-256 values.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def f32(x: float) -> float:
    try:
        return struct.unpack(">f", struct.pack(">f", x))[0]
    except OverflowError:
        return math.copysign(math.inf, x)


def f2(n: int) -> float:
    # IEEE binary32 rounding after each source-level multiplication and addition.
    total = power = f32(1.0)
    for _ in range(n):
        power = f32(power * 2.0)
        total = f32(total + power)
    return total


def bits32(x: float) -> str:
    return struct.pack(">f", x).hex().upper()


def tlb_trace() -> list[dict]:
    # Two ways in each of eight sets. Each list is MRU -> LRU.
    sets = {i: [] for i in range(8)}
    trace = []
    for vpn in [10, 12, 16, 7, 26, 4, 12, 20]:
        group = vpn % 8
        tag = vpn // 8
        before = list(sets[group])
        hit = vpn in before
        evicted = None
        if hit:
            sets[group].remove(vpn)
        elif len(sets[group]) == 2:
            evicted = sets[group].pop()
        sets[group].insert(0, vpn)
        trace.append(dict(vpn_decimal=vpn, group=group, tag_decimal=tag,
                          hit=hit, before_mru_to_lru=before,
                          after_mru_to_lru=list(sets[group]), evicted=evicted))
    return trace


def pipeline_schedules() -> list[dict]:
    # 2012q44: in-order issue/complete, no forwarding, and reads may not occur
    # in the same cycle as a source register's writeback. IF may overlap ID.
    predecessors = {
        "LoadX": set(), "LoadA": set(), "ShiftX": {"LoadX"},
        "Add": {"ShiftX", "LoadA"}, "Store": {"Add"},
    }
    rows = []
    for order in itertools.permutations(predecessors):
        done = set()
        if any(not predecessors[op].issubset(set(order[:i]))
               for i, op in enumerate(order)):
            continue
        last_id = 1
        wb = {}
        schedule = []
        for op in order:
            fetch = last_id
            decode = max([last_id + 1] + [wb[p] + 1 for p in predecessors[op]])
            wb[op] = decode + 3
            schedule.append(dict(op=op, IF=fetch, ID=decode,
                                 EX=decode + 1, M=decode + 2, WB=decode + 3))
            last_id = decode
            done.add(op)
        rows.append(dict(order=list(order), cycles=wb[order[-1]], stages=schedule))
    return sorted(rows, key=lambda row: row["cycles"])


def joint_translation_trace() -> list[dict]:
    # Original OS book physical p236, tables3.1-3.3, independently image-read.
    # Tuple order here is tag, valid, PFN; each access starts from this snapshot.
    tlb = {
        0: [(0x03, 0, None), (0x00, 0, None), (0x09, 1, 0x0D), (0x07, 1, 0x02)],
        3: [(0x07, 0, None), (0x0A, 1, 0x34), (0x03, 1, 0x0D), (0x02, 0, None)],
    }
    page_table = {0x03: (1, 0x02), 0x08: (0, None)}
    cache = {5: (0x0D, 1, [0x36, 0x72, 0xF0, 0x1D]),
             0xC: (0x02, 0, [None] * 4)}
    result = []
    for va in [0x03D4, 0x00F1, 0x0229]:
        vpn, page_offset = divmod(va, 64)
        tlb_tag, tlb_set = divmod(vpn, 4)
        matches = [pfn for tag, valid, pfn in tlb[tlb_set] if valid and tag == tlb_tag]
        row = dict(virtual_address=f"{va:04X}", VPN=f"{vpn:02X}",
                   page_offset=f"{page_offset:02X}", TLB_set=tlb_set,
                   TLB_tag=f"{tlb_tag:02X}", TLB_hit=bool(matches))
        if matches:
            pfn = matches[0]
        else:
            present, pfn = page_table[vpn]
            row["PTE_present"] = bool(present)
            if not present:
                row["stops_at"] = "page fault; no current physical address or data-Cache lookup"
                result.append(row)
                continue
        physical = pfn * 64 + page_offset
        block, byte = divmod(physical, 4)
        cache_tag, cache_index = divmod(block, 16)
        stored_tag, valid, contents = cache[cache_index]
        hit = bool(valid and cache_tag == stored_tag)
        row.update(PFN=f"{pfn:02X}", physical_address=f"{physical:03X}",
                   Cache_tag=f"{cache_tag:02X}", Cache_line=f"{cache_index:X}",
                   block_byte=byte, Cache_hit=hit,
                   final_byte=f"{contents[byte]:02X}" if hit else None,
                   final_source="Cache" if hit else "main memory; byte value not supplied")
        result.append(row)
    assert result[0]["physical_address"] == "354" and result[0]["final_byte"] == "36"
    assert result[1]["physical_address"] == "0B1" and result[1]["Cache_hit"] is False
    assert result[1]["final_byte"] is None
    assert result[2]["PTE_present"] is False and "physical_address" not in result[2]
    return result


def main() -> None:
    trace = tlb_trace()
    schedules = pipeline_schedules()
    factorial13 = math.factorial(13)
    displacement = 0x00401000 - (0x00401025 + 5)
    poll_period = 4 / 2e6
    poll_cycles_per_second = (1 / poll_period) * 10 * 4
    dma_cycles_per_second = (40e6 / 1000) * 500
    result = {
        "scope": "independent numerical/state verification only; no visual acceptance",
        "chapter_sha256": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / "manuscript").glob("*/*.md"))
        },
        "CO_2017_Q43": {
            "source": "CO original book physical PDF78,86-87 (printed66,74-75)",
            "f1_model": "32-bit two's-complement modulo arithmetic for this exam; not an ISO C signed-overflow guarantee",
            "f1_23_integer_bits": f"{(1 << 24) - 1:08X}",
            "f2_23_bits": bits32(f2(23)),
            "f1_24_mathematical": (1 << 25) - 1,
            "f2_24": f2(24),
            "f1_31_wrap_signed": -1,
            "maximum_exact_signed_int_n": 30,
            "maximum_finite_f2_n": max(n for n in range(128) if math.isfinite(f2(n))),
            "maximum_exact_f2_n": max(n for n in range(128) if f2(n) == (1 << (n + 1)) - 1),
            "f2_127_bits": bits32(f2(127)),
        },
        "CO_2019_Q45": {
            "source": "CO original book physical PDF195-196,200-201 (printed183-184,188-189)",
            "call_PC_after": f"{0x00401025 + 5:08X}",
            "relative_signed_displacement": displacement,
            "relative_displacement_bits": f"{displacement & 0xFFFFFFFF:08X}",
            "little_endian_displacement_bytes": struct.pack("<i", displacement).hex(" ").upper(),
            "factorial13": factorial13,
            "low32_factorial13": factorial13 & 0xFFFFFFFF,
            "calls_in_f1_10_including_initial": 10,
            "recursive_call_instruction_executions": 9,
            "signed_imul_overflow_condition": "full product is not the sign extension of its low 32 bits",
        },
        "CO_2021_Q44": {
            "source": "CO original book physical PDF152,157 (printed140,145)",
            "VA_bits": 30, "PA_bits": 24, "page_offset_bits": 12,
            "VPN_bits": 18, "PFN_bits": 12, "TLB_set_bits": 3,
            "TLB_tag_bits": 15, "tag_width_increase_if_VA_32": 2,
            "trace": trace,
        },
        "CO_2012_Q44": {
            "source": "CO original book physical PDF271,277 (printed259,265)",
            "minus513_bits": f"{(-513) & 0xFFFF:04X}",
            "arithmetic_shift_right1_bits": f"{((-513) >> 1) & 0xFFFF:04X}",
            "four_independent_instructions_cycles": 5 + 4 - 1,
            "minimum_cycles": schedules[0]["cycles"],
            "all_valid_five_operation_orders": schedules,
            "lower_bound": "LoadX WB>=5, ShiftX ID>=6/WB>=9, Add ID>=10/WB>=13, Store ID>=14/WB>=17",
        },
        "CO_2018_Q43": {
            "source": "CO original book physical PDF328-329,337 (printed316-317,325)",
            "MB_unit": "10^6 bytes, as used by the original solution",
            "poll_max_interval_us": poll_period * 1e6,
            "poll_min_calls_per_second": 1 / poll_period,
            "poll_cpu_fraction": poll_cycles_per_second / 500e6,
            "interrupt_response_plus_service_us": 400 / 500e6 * 1e6,
            "B_32bit_arrival_interval_us": 4 / 40e6 * 1e6,
            "interrupt_capacity_sufficient": 400 / 500e6 <= 4 / 40e6,
            "dma_blocks_per_second": 40e6 / 1000,
            "dma_cpu_fraction": dma_cycles_per_second / 500e6,
        },
        "CO3_13_textbook_example_not_exam": {
            "source": "OS original book physical PDF235-237 (printed223-225), section3.2.9; original tables3.1-3.3 and solution",
            "virtual_fields_bits": [6, 2, 6],
            "physical_fields_bits": [6, 4, 2],
            "independent_initial_snapshot_for_each_query": True,
            "trace": joint_translation_trace(),
        },
    }
    assert result["CO_2017_Q43"]["f2_23_bits"] == "4B7FFFFF"
    assert result["CO_2017_Q43"]["maximum_finite_f2_n"] == 126
    assert result["CO_2017_Q43"]["maximum_exact_f2_n"] == 23
    assert trace[-1]["evicted"] == 4 and trace[-2]["hit"]
    assert schedules[0]["cycles"] == 17
    assert result["CO_2019_Q45"]["low32_factorial13"] == 1932053504
    assert math.isclose(result["CO_2018_Q43"]["poll_cpu_fraction"], 0.04)
    assert math.isclose(result["CO_2018_Q43"]["dma_cpu_fraction"], 0.04)
    (OUT / "independent_numbers.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Five source-based CO problems plus joint textbook example passed; wrote independent_numbers.json")


if __name__ == "__main__":
    main()
