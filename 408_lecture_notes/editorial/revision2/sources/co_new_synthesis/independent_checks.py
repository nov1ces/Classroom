"""Independent arithmetic checks for five visually reviewed CO exam questions.

This script models the stated machine rules; it does not run overflowing C.
All times and byte rates in the 2018 problem use decimal MB/s.
"""
from collections import defaultdict
from fractions import Fraction
from itertools import permutations
from pathlib import Path
import json
import math
import struct


def single(value):
    try:
        return struct.unpack('>f', struct.pack('>f', value))[0]
    except OverflowError:
        return math.copysign(math.inf, value)


def single_bits(value):
    return struct.pack('>f', value).hex().upper()


def float_sum(n):
    power = total = single(1)
    for _ in range(n):
        power = single(power * 2)
        total = single(total + power)
    return total


def fixed_sum(n):
    power = total = 1
    for _ in range(n):
        power = (power * 2) & 0xFFFFFFFF
        total = (total + power) & 0xFFFFFFFF
    signed = total if total < 2**31 else total - 2**32
    return {'hex': f'{total:08X}', 'signed': signed}


def schedule(sequence, definitions):
    """Five stages; next IF can coincide with preceding ID; read after WB."""
    ready = {}
    rows = []
    prior_id = 1
    for instruction in sequence:
        sources, destination = definitions[instruction]
        fetch = prior_id
        decode = max([fetch + 1] + [ready.get(r, 0) + 1 for r in sources])
        row = dict(instruction=instruction, IF=fetch, ID=decode,
                   EX=decode + 1, M=decode + 2, WB=decode + 3)
        rows.append(row)
        if destination:
            ready[destination] = row['WB']
        prior_id = decode
    return rows


data = {}
assert single_bits(float_sum(23)) == '4B7FFFFF'
assert float_sum(24) == 33554432
assert fixed_sum(31)['signed'] == -1
assert math.isfinite(float_sum(126)) and math.isinf(float_sum(127))
data['2017q43'] = {
    'f1_23': fixed_sum(23), 'f2_23_hex': single_bits(float_sum(23)),
    'f1_24': fixed_sum(24), 'f2_24': float_sum(24),
    'f2_24_hex': single_bits(float_sum(24)),
    'f1_31': fixed_sum(31), 'f1_largest_exact_n': 30,
    'f2_126_hex': single_bits(float_sum(126)),
    'f2_127_hex': single_bits(float_sum(127)),
    'f2_largest_finite_n': 126, 'f2_largest_exact_n': 23,
    'unsigned_n_minus_1_at_n0': f'{(0 - 1) & 0xFFFFFFFF:08X}',
    'model': 'explicit 32-bit truncation / IEEE binary32 nearest-even; not a standard-C overflow execution',
}

factorial13 = math.factorial(13)
next_pc = 0x00401025 + 5
offset = 0x00401000 - next_pc
assert offset == -42
assert list(struct.pack('<i', offset)) == [0xD6, 0xFF, 0xFF, 0xFF]
assert factorial13 & 0xFFFFFFFF == 1932053504
data['2019q45'] = {
    'f10_total_invocations': 10, 'f10_internal_recursive_calls': 9,
    'next_pc_hex': f'{next_pc:08X}', 'offset_decimal': offset,
    'offset_hex': f'{offset & 0xFFFFFFFF:08X}',
    'offset_little_endian_bytes': struct.pack('<i', offset).hex(' ').upper(),
    'factorial13': factorial13, 'factorial13_hex': f'{factorial13:X}',
    'low32_decimal': factorial13 & 0xFFFFFFFF,
    'low32_hex': f'{factorial13 & 0xFFFFFFFF:08X}',
}

groups = defaultdict(list)
trace = []
for vpn in [10, 12, 16, 7, 26, 4, 12, 20]:
    group = vpn % 8
    hit = vpn in groups[group]
    victim = None
    if hit:
        groups[group].remove(vpn)
    elif len(groups[group]) == 2:
        victim = groups[group].pop(0)
    groups[group].append(vpn)
    trace.append(dict(vpn=vpn, group=group, hit=hit, victim=victim,
                      entries_LRU_to_MRU=groups[group].copy()))
assert [r['victim'] for r in trace if r['victim'] is not None] == [4]
data['2021q44'] = {
    'virtual_page_bits': '29..12', 'page_offset_bits': '11..0',
    'tlb_tag_bits': '29..15', 'tlb_set_bits': '14..12',
    'trace': trace, 'extra_tag_bits_if_va_32': 2,
}

supplied = schedule(['load_a', 'load_b', 'add', 'store'], {
    'load_a': ([], 'R1'), 'load_b': ([], 'R2'),
    'add': (['R1', 'R2'], 'R2'), 'store': (['R2'], None),
})
assert [row['ID'] for row in supplied] == [2, 3, 7, 11]
definitions = {
    'load_x': ([], 'R1'), 'load_a': ([], 'R2'),
    'shift_x': (['R1'], 'R1'), 'add': (['R1', 'R2'], 'R2'),
    'store': (['R2'], None),
}
dependencies = [('load_x', 'shift_x'), ('shift_x', 'add'),
                ('load_a', 'add'), ('add', 'store')]
legal = []
for order in permutations(definitions):
    pos = {name: i for i, name in enumerate(order)}
    if all(pos[a] < pos[b] for a, b in dependencies):
        rows = schedule(order, definitions)
        legal.append(dict(order=list(order), cycles=rows[-1]['WB'], schedule=rows))
best = min(legal, key=lambda x: x['cycles'])
assert best['cycles'] == 17
assert (-513 >> 1) & 0xFFFF == 0xFEFF
data['2012q44'] = {
    'arithmetic_right_shift_hex': f'{(-513 >> 1) & 0xFFFF:04X}',
    'arithmetic_right_shift_signed': -513 >> 1,
    'ideal_4_instruction_cycles': 4 + 5 - 1,
    'supplied_schedule': supplied, 'legal_orderings_of_five_required_operations': legal,
    'best': best,
    'store_completion_convention': 'same five-stage chart as source/reference, including STORE WB column',
}

clock = 500_000_000
buffer_bytes = 4
rate_a, rate_b = 2_000_000, 40_000_000
query_interval = Fraction(buffer_bytes, rate_a)
query_fraction = Fraction(rate_a, buffer_bytes) * 10 * 4 / clock
b_interval_cycles = Fraction(buffer_bytes, rate_b) * clock
b_interrupt_fraction = Fraction(rate_b, buffer_bytes) * 400 / clock
dma_fraction = Fraction(rate_b, 1000) * 500 / clock
assert query_fraction == dma_fraction == Fraction(1, 25)
assert b_interval_cycles == 50 and b_interrupt_fraction == 8
data['2018q43'] = {
    'A_max_query_interval_seconds': str(query_interval),
    'A_max_query_interval_microseconds': float(query_interval * 1_000_000),
    'A_min_CPU_fraction': str(query_fraction),
    'B_interrupt_arrival_interval_cycles': int(b_interval_cycles),
    'B_interrupt_min_service_cycles': 400,
    'B_interrupt_required_CPU_fraction': str(b_interrupt_fraction),
    'B_DMA_blocks_per_second': rate_b // 1000,
    'B_DMA_max_CPU_fraction': str(dma_fraction),
}

target = Path(__file__).with_name('independent_checks.json')
target.write_text(json.dumps(data, ensure_ascii=False, indent=2))
print('Independent checks passed for', ', '.join(data))
