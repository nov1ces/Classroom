"""Recompute the actual DS revision-2 diagram states independently.

Reads the author's scene data as the object under review; uses separate
insertion/rotation/split/merge/range checks to establish expected states.
No figure generator is run, and no manuscript or V1 report is written.
"""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "tools/draw_ds_figures.py"
spec = importlib.util.spec_from_file_location("reviewed_ds_scene_data", SOURCE)
scene = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scene)


def height(t):
    return 0 if t is None else 1 + max(height(t[1]), height(t[2]))


def inorder(t):
    return [] if t is None else inorder(t[1]) + [t[0]] + inorder(t[2])


def factors(t):
    if t is None:
        return {}
    return {**factors(t[1]), t[0]: height(t[1]) - height(t[2]), **factors(t[2])}


def bst_insert(t, key):
    if t is None:
        return [key, None, None]
    t = deepcopy(t)
    assert t[0] != key
    branch = 1 if key < t[0] else 2
    t[branch] = bst_insert(t[branch], key)
    return t


def rotate(t, direction, key):
    t = deepcopy(t)
    if t[0] != key:
        branch = 1 if key < t[0] else 2
        t[branch] = rotate(t[branch], direction, key)
        return t
    if direction == "left":
        pivot = t[2]
        assert pivot is not None
        t[2] = pivot[1]
        pivot[1] = t
    else:
        pivot = t[1]
        assert pivot is not None
        t[1] = pivot[2]
        pivot[2] = t
    return pivot


def node(keys, children=()):
    return {"keys": list(keys), "children": list(children)}


def bkeys(t):
    if not t["children"]:
        return list(t["keys"])
    result = []
    for i, child in enumerate(t["children"]):
        result += bkeys(child)
        if i < len(t["keys"]):
            result.append(t["keys"][i])
    return result


def bcheck(t, allowed=None):
    allowed = allowed or {}
    leaves = []
    violations = {}

    def walk(u, path, low, high, depth):
        keys = u["keys"]
        assert keys == sorted(set(keys)), ("unsorted/duplicate node", path)
        assert all(low < key < high for key in keys), ("wrong child interval", path)
        minimum = 1 if not path else 2
        if not minimum <= len(keys) <= 4:
            violations[path] = len(keys)
        children = u["children"]
        if children:
            assert len(children) == len(keys) + 1, ("child count", path)
            cuts = [low, *keys, high]
            for i, child in enumerate(children):
                walk(child, path + (i,), cuts[i], cuts[i + 1], depth + 1)
        else:
            leaves.append(depth)

    walk(t, (), float("-inf"), float("inf"), 1)
    assert violations == allowed, ("unmarked occupancy violation", violations, allowed)
    assert len(set(leaves)) == 1, ("unequal leaf depths", leaves)
    ordered = bkeys(t)
    assert ordered == sorted(set(ordered)), "tree-wide duplicate/out-of-order key"
    return {"keys": ordered, "key_count": len(ordered), "height": leaves[0],
            "temporary_violations": [{"path": list(p), "keys": k} for p, k in violations.items()]}


def at(t, path):
    for i in path:
        t = t["children"][i]
    return t


def leaf_insert(t, key):
    t = deepcopy(t)
    cur = t
    while cur["children"]:
        i = sum(k < key for k in cur["keys"])
        cur = cur["children"][i]
    assert key not in cur["keys"]
    cur["keys"].append(key)
    cur["keys"].sort()
    return t


def split(t, path):
    t = deepcopy(t)
    u = at(t, path)
    assert len(u["keys"]) == 5
    left = node(u["keys"][:2], u["children"][:3] if u["children"] else [])
    right = node(u["keys"][3:], u["children"][3:] if u["children"] else [])
    promoted = u["keys"][2]
    if not path:
        return node([promoted], [left, right])
    parent = at(t, path[:-1])
    i = path[-1]
    parent["keys"].insert(i, promoted)
    parent["children"][i:i + 1] = [left, right]
    return t


def merge_adjacent(t, parent_path, separator_index):
    t = deepcopy(t)
    parent = at(t, parent_path)
    i = separator_index
    left, right = parent["children"][i:i + 2]
    merged = node(left["keys"] + [parent["keys"][i]] + right["keys"],
                  left["children"] + right["children"])
    del parent["keys"][i]
    parent["children"][i:i + 2] = [merged]
    return t


def borrow_right(t, parent_path, child_index):
    t = deepcopy(t)
    parent = at(t, parent_path)
    left, right = parent["children"][child_index:child_index + 2]
    left["keys"].append(parent["keys"][child_index])
    parent["keys"][child_index] = right["keys"].pop(0)
    if right["children"]:
        left["children"].append(right["children"].pop(0))
    return t


def borrow_left(t, parent_path, child_index):
    t = deepcopy(t)
    parent = at(t, parent_path)
    left, right = parent["children"][child_index - 1:child_index + 1]
    right["keys"].insert(0, parent["keys"][child_index - 1])
    parent["keys"][child_index - 1] = left["keys"].pop()
    if left["children"]:
        right["children"].insert(0, left["children"].pop())
    return t


def main():
    result = {"scope": "tree mechanism and state verification; no layout/PDF acceptance",
              "scene_source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "AVL": [], "B_tree": {}}
    for case in scene.AVL_CASES:
        pre = case["pre_insert"]
        states = case["states"]
        assert all(abs(x) <= 1 for x in factors(pre).values())
        assert bst_insert(pre, case["insert"]) == states[0]
        target = sorted(inorder(pre) + [case["insert"]])
        current = states[0]
        for operation, following in zip(case["operations"], states[1:]):
            current = rotate(current, operation["direction"], operation["at"])
            assert current == following, ("wrong rotation/transfer", case["type"])
        for t in states:
            assert inorder(t) == target
        assert [height(pre), height(states[0]), height(states[-1])] == [3, 4, 3]
        assert all(abs(x) <= 1 for x in factors(states[-1]).values())
        result["AVL"].append({"case": case["type"], "inorder": target,
                              "state_heights": [height(t) for t in states],
                              "state_balance_factors": [factors(t) for t in states]})

    ins = scene.BTREE_INSERT_STATES
    assert leaf_insert(scene.BTREE_INSERT_INITIAL, 29) == ins[0]
    assert split(ins[0], (4,)) == ins[1]
    assert split(ins[1], ()) == ins[2]
    initial = bcheck(scene.BTREE_INSERT_INITIAL)
    insert_checks = [bcheck(t, allowed) for t, allowed in
                     zip(ins, [{(4,): 5}, {(): 5}, {}])]
    assert initial["key_count"] == 16
    assert all(row["keys"] == sorted(initial["keys"] + [29]) for row in insert_checks)

    bor = scene.BTREE_BORROW_STATES
    deleted = deepcopy(scene.BTREE_BORROW_INITIAL)
    deleted["children"][0]["keys"].remove(2)
    assert deleted == bor[0]
    assert borrow_right(bor[0], (), 0) == bor[1]
    borrow_checks = [bcheck(bor[0], {(0,): 1}), bcheck(bor[1])]
    assert bkeys(bor[0]) == bkeys(bor[1])

    deletion = scene.BTREE_DELETE_STATES
    deleted = deepcopy(ins[2])
    deleted["children"][0]["children"][0]["keys"].remove(1)
    assert deleted == deletion[0]
    assert merge_adjacent(deletion[0], (0,), 0) == deletion[1]
    assert merge_adjacent(deletion[1], (), 0) == deletion[2]
    assert deletion[2]["children"][0] == deletion[3]
    delete_checks = [bcheck(t, allowed) for t, allowed in
                     zip(deletion, [{(0, 0): 1}, {(0,): 1}, {(): 0}, {}])]
    target = [key for key in bkeys(ins[2]) if key != 1]
    assert all(row["keys"] == target for row in delete_checks)

    # Independent witnesses for the text's internal-child-transfer rule.
    right_witness = node([40], [node([10], [node([1, 5]), node([15, 20])]),
        node([60, 80, 100], [node([45, 50]), node([65, 70]), node([85, 90]), node([105, 110])])])
    fixed_right = borrow_right(right_witness, (), 0)
    assert bkeys(right_witness) == bkeys(fixed_right)
    bcheck(right_witness, {(0,): 1})
    bcheck(fixed_right)
    assert fixed_right["children"][0]["children"][-1]["keys"] == [45, 50]
    left_witness = node([60], [node([10, 30, 40], [node([1, 5]), node([15, 20]), node([33, 35]), node([45, 50])]),
        node([100], [node([80, 90]), node([105, 110])])])
    fixed_left = borrow_left(left_witness, (), 1)
    assert bkeys(left_witness) == bkeys(fixed_left)
    bcheck(left_witness, {(1,): 1})
    bcheck(fixed_left)
    assert fixed_left["children"][1]["children"][0]["keys"] == [45, 50]

    result["B_tree"] = {"order": 5, "initial": initial, "insertion": insert_checks,
                         "borrow": borrow_checks, "cascade_delete": delete_checks,
                         "independent_internal_borrow_child_transfer": "both directions checked"}
    result["current_inputs_sha256"] = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [*sorted((ROOT / "manuscript/DS").glob("*.md")),
                  *[ROOT / "figures" / f"{stem}.{ext}"
                    for stem in ["DS_14_avl_rotations", "DS_21_avl_double_rotations", "DS_15_btree_split", "DS_20_btree_delete"]
                    for ext in ["svg", "png"]]]}
    (OUT / "independent_tree_results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Independent AVL rotations/transfers and all 5-order B-tree states passed")


if __name__ == "__main__":
    main()
