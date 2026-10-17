#!/usr/bin/env python3
"""Independent state/number checks from actually read source problems.

This script does not import the authors' checkers and does not open lecture PDFs.
"""
from pathlib import Path
from itertools import permutations
import json

OUT = Path(__file__).resolve().parent
results = {}

# 2016/46: smaller numbers win; the running and waiting terms must oppose.
def priority(nice, cpu_time, wait_time, k1=1, k2=1):
    assert k1 > 0 and k2 > 0
    return nice+k1*cpu_time-k2*wait_time
assert priority(10, 0, 11) < priority(0, 0, 0)
assert priority(0, 3, 0) > priority(0, 2, 0)
results["OS_2016_46"] = {
    "ordering": "smaller priority runs first",
    "one_valid_formula": "nice+k1*cpuTime-k2*waitTime; k1,k2>0",
    "wait_11_priority_example": priority(10,0,11),
    "static_nice_can_starve": True,
    "boundary": "Aging requires finite/bounded competing priorities, ongoing reevaluation, and scheduling opportunities; it is not a fixed waiting-time bound for arbitrary arrivals."
}

# 2009/46: initial resident pages are 0 and 2; first access makes page 0 LRU.
resident = {0: 0x101, 2: 0x254}
lru = [0, 2]
tlb = {}
accesses = []
for va in (0x2362, 0x1565, 0x25A5):
    page, offset = divmod(va, 4096)
    cost = 10
    path = ["TLB10"]
    victim = None
    if page not in tlb:
        cost += 100
        path.append("page_table100")
        if page not in resident:
            victim = lru.pop(0)
            frame = resident.pop(victim)
            tlb.pop(victim, None)
            cost += 10**8
            path.append("fault_complete_100000000")
            resident[page] = frame
            tlb[page] = frame
            cost += 10
            path.append("retry_TLB10")
        else:
            tlb[page] = resident[page]
    cost += 100
    path.append("data100")
    if page in lru:
        lru.remove(page)
    lru.append(page)
    accesses.append({"va": f"{va:04X}H", "page": page, "offset": offset,
                     "victim": victim, "physical": f"{resident[page]*4096+offset:X}H",
                     "time_ns": cost, "path": path, "LRU_to_MRU": list(lru)})
assert [a["time_ns"] for a in accesses] == [210, 100000220, 110]
assert accesses[1]["physical"] == "101565H"
results["OS_2009_46"] = accesses

# 2020/46: linear array location and a 10/10/12 page-table split.
va = 0x10800000 + (1*1024 + 2)*4
directory = va >> 22
page_index = (va >> 12) & 1023
directory_entry = 0x00201000 + directory*4
page_entry = 0x00301*4096 + page_index*4
assert (va, directory, page_index, directory_entry, page_entry) == (
    0x10801008, 0x42, 1, 0x00201108, 0x00301004)
results["OS_2020_46"] = {"VA": f"{va:08X}H", "directory_index": directory,
    "page_table_index": page_index, "directory_entry_PA": f"{directory_entry:08X}H",
    "page_entry_PA": f"{page_entry:08X}H", "one_row_bytes": 1024*4,
    "virtual_contiguous": True, "physical_contiguous_required": False}

# 2022/45: directory association, shared inode, and mixed indexing thresholds.
clusters = 6*2**20 // 4096
assert clusters == 1536 and 10+1024 < clusters <= 10+1024+1024**2
results["OS_2022_45"] = {"stu_entries": [["course", 2], ["doc", 10]],
    "doc_data_block": 30, "read_course1_uncached_inode_and_data": 2,
    "course2_6MiB_data_blocks": clusters, "indirect_levels_needed": [1, 2],
    "direct_plus_single_capacity_blocks": 10+1024}

# 2018/46: addressable length and two independent file-count resources.
per_index = 4096//4
max_length = (8+per_index+per_index**2+per_index**3)*4096
inode_count = 2**20 * (4096//64)
data_file_count = 512*2**20 // 2
assert per_index == 1024 and inode_count == 64*2**20 and data_file_count == 256*2**20
results["OS_2018_46"] = {"index_entries_per_cluster": per_index,
    "max_file_bytes": max_length, "equivalent": "4TiB+4GiB+4MiB+32KiB",
    "inodes_available": inode_count, "data_pool_file_capacity": data_file_count,
    "max_5600B_files": min(inode_count, data_file_count),
    "F1_6KiB_last_logical_cluster": (6*1024-1)//4096,
    "F2_40KiB_last_logical_cluster": (40*1024-1)//4096,
    "question_3_requested_object": "last cluster NUMBER, not last cluster data",
    "cluster_number_extra_disk_reads_given_inode_resident": [0, 1],
    "cluster_number_disk_reads_if_inode_uncached": [1, 2],
    "data_disk_reads_given_inode_resident_comparison_only": [1, 2]}

# 2023/46: derive the order from blocking, interrupt and wakeup prerequisites.
# This is a source question with keyboard input, not a disk/DMA calculation.
state = "running"
order = []
for operation in (2, 6, 4, 3, 1, 5):
    if operation == 2:
        assert state == "running"
        state = "blocked"
    elif operation in (6, 4, 3):
        assert state == "blocked"
    elif operation == 1:
        assert state == "blocked"
        state = "ready"
    elif operation == 5:
        assert state == "ready"
        state = "running"
    order.append(operation)
assert order[order.index(1)-1:order.index(1)+2] == [3,1,5]
assert order[order.index(6)+1] == 4
results["OS_2023_46"] = {
    "operation_order": order,
    "neighbors_of_1": [3,5], "next_after_6": 4,
    "must_switch_away_after": 2,
    "P_becomes_schedulable_after": 1,
    "driver_operation_among_six": 3,
    "P_state_before_wakeup_during_keyboard_handler": "blocked",
    "CPU_mode_in_handler": "kernel",
    "boundary": "After wakeup P is ready, not necessarily running; system-call return additionally requires P to be selected and resumed."
}

# 2019/44: geometry, shortest next seek, and cluster-to-first-sector CHS.
requests = [100260, 60005, 101660, 110560]
current = 85
pending = requests[:]
order, cylinders = [], [current]
while pending:
    nxt = min(pending, key=lambda x: abs(x//1000-current))
    pending.remove(nxt)
    order.append(nxt)
    current = nxt//1000
    cylinders.append(current)
first_sector = 100530*2
cylinder, remainder = divmod(first_sector, 10*200)
head, sector = divmod(remainder, 200)
assert order == [100260, 101660, 110560, 60005]
assert (cylinder, head, sector) == (100, 5, 60)
results["OS_2019_44"] = {"capacity_bytes": 300*10*200*512,
    "capacity_KiB": 300*10*200*512//1024, "SSTF_clusters": order,
    "SSTF_cylinders": cylinders, "CHS_first_sector": [cylinder,head,sector],
    "cluster_size_bytes": 2*512}

# DS figure: create threads only in originally null child slots.
tree = {"A": ("B", "C"), "B": ("D", "E"), "C": (None, "F"),
        "D": (None, None), "E": (None, None), "F": (None, None)}
def inorder(node):
    return [] if node is None else inorder(tree[node][0])+[node]+inorder(tree[node][1])
walk = inorder("A")
threads, fields = [], {}
for i, node in enumerate(walk):
    left, right = tree[node]
    pred = walk[i-1] if i else None
    succ = walk[i+1] if i+1 < len(walk) else None
    fields[node] = {"L": left if left else pred, "ltag": int(left is None),
                    "R": right if right else succ, "rtag": int(right is None)}
    if left is None: threads.append([node, "L", pred])
    if right is None: threads.append([node, "R", succ])
def first(node):
    while fields[node]["ltag"] == 0: node = fields[node]["L"]
    return node
def next_node(node):
    return fields[node]["R"] if fields[node]["rtag"] else first(fields[node]["R"])
thread_walk, p = [], first("A")
while p is not None:
    assert p not in thread_walk
    thread_walk.append(p)
    p = next_node(p)
assert walk == thread_walk == list("DBEACF")
assert len(threads) == 7 and sum(t[2] is None for t in threads) == 2
results["DS_06_inorder_threads"] = {"inorder": walk, "fields": fields,
    "original_null_fields_to_threads": threads, "thread_domain_count": len(threads),
    "ordinary_node_targets": 5, "empty_boundary_targets": 2,
    "successor_walk_without_stack": thread_walk}

# CO6-5: no forwarding, same-register read/write in same cycle disallowed.
def schedule(instructions):
    writes, state = {}, []
    prev_id = 1
    for name, reads, dest in instructions:
        fetch = prev_id
        decode = max([fetch+1]+[writes[x]+1 for x in reads if x in writes])
        wb = decode+3
        state.append({"instruction": name, "IF": fetch, "ID": decode,
                      "EX": decode+1, "M": decode+2, "WB": wb})
        if dest is not None: writes[dest] = wb
        prev_id = decode
    return state
sum_sequence = [("LOAD_a", [], "r1"), ("LOAD_b", [], "r2"),
                ("ADD_r1_r2", ["r1", "r2"], "r2"), ("STORE", ["r2"], None)]
sum_schedule = schedule(sum_sequence)
assert [x["ID"] for x in sum_schedule] == [2, 3, 7, 11]
assert sum_schedule[-1]["WB"] == 14
deps = {"LOAD_x": set(), "LOAD_a": set(), "SHL_x": {"LOAD_x"},
        "ADD": {"SHL_x", "LOAD_a"}, "STORE": {"ADD"}}
ops = {"LOAD_x": ([], "x"), "LOAD_a": ([], "a"), "SHL_x": (["x"], "x"),
       "ADD": (["x", "a"], "sum"), "STORE": (["sum"], None)}
valid = []
for seq in permutations(deps):
    done = set()
    if any(not deps[x] <= set(seq[:i]) for i,x in enumerate(seq)): continue
    sched = schedule([(x, *ops[x]) for x in seq])
    valid.append((sched[-1]["WB"], list(seq), sched))
minimum = min(x[0] for x in valid)
assert minimum == 17
results["CO_2012_44_pipeline"] = {"sum_schedule": sum_schedule,
    "legal_dependency_orders": len(valid), "minimum_cycles": minimum,
    "optimal_orders": [x[1] for x in valid if x[0] == minimum],
    "optimal_schedule": next(x[2] for x in valid if x[0] == minimum),
    "SHR_minus513_16bit": f"{((-513)>>1) & 0xffff:04X}H"}
assert results["CO_2012_44_pipeline"]["SHR_minus513_16bit"] == "FEFFH"

# CO4-6: machine bytes, signed displacement, factorial and signed product fit.
call_bytes = bytes.fromhex("E8 D6 FF FF FF")
displacement = int.from_bytes(call_bytes[1:], "little", signed=True)
next_pc = 0x00401025+len(call_bytes)
assert displacement == -42 and next_pc+displacement == 0x00401000
factorial13 = 1
for n in range(2,14): factorial13 *= n
assert factorial13 == 6227020800 and factorial13 % 2**32 == 1932053504
results["CO_2019_45_call"] = {"call_bytes": call_bytes.hex(" "),
    "next_PC": f"{next_pc:08X}H", "signed_displacement": displacement,
    "target": f"{next_pc+displacement:08X}H", "13_factorial": factorial13,
    "low32_result": factorial13 % 2**32, "C_signed_overflow_is_undefined": True}

payload = {"status": "PASS_INDEPENDENT_CALCULATIONS", "checks": results,
           "method": "Independent source-derived state calculations; no lecture PDF opened or rendered."}
(OUT/"independent_content_states.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"status":payload["status"],"checks":list(results)}, ensure_ascii=False))
