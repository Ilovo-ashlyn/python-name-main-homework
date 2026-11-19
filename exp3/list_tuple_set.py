# -*- coding: utf-8 -*-
"""实验 3：列表、元组、集合（任务 1~5 + 拓展）。

运行：python list_tuple_set.py
任务 1 的「预判」是先手写、再由程序自动核对；其余结论全部由代码现场计算。
"""


def keep_order(seq):
    """保序去重：只保留第一次出现的元素（用集合加速查找，元素需可哈希）。"""
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def task1():
    cases = [
        ("del ls[::3]", list(range(10)), slice(None, None, 3), [1, 2, 4, 5, 7, 8]),
        ("del ls[1::3]", list(range(10)), slice(1, None, 3), [0, 2, 3, 5, 6, 8, 9]),
        ("del ls[::-2]", list(range(6)), slice(None, None, -2), [0, 2, 4]),
        ("del ls[::2]", [1, 2, 3, 4, 5, 6], slice(None, None, 2), [2, 4, 6]),
    ]
    for name, ls, sl, guess in cases:
        before = ls[:]
        del ls[sl]
        mark = "[OK]" if ls == guess else "[差异]"
        print(f"  {name:<20} {before} -> 预判 {guess} | 实测 {ls} {mark}")

    for nums in ([1, 2, 3, 4, 5, 6], [1, 2, 4, 6, 8]):
        buggy = nums[:]
        for x in buggy:                       # 错误做法：一边遍历一边删
            if x % 2 == 0:
                buggy.remove(x)
        safe = [x for x in nums if x % 2]    # 安全做法：推导式生成新列表
        left = [x for x in buggy if x % 2 == 0]
        print(f"  循环删偶数 {nums} -> {buggy}，残留偶数 {left}；安全做法 -> {safe}")


def task2():
    trials = [
        ("(1, 2, 3)", (1, 2, 3), True, "元素全是可哈希 int"),
        ("(1, [2, 3])", (1, [2, 3]), False, "元组内含 list，整体不可哈希"),
        ("[1, 2]", [1, 2], False, "list 可变，不可哈希"),
        ("frozenset({1,2})", frozenset({1, 2}), True, "不可变集合，可哈希"),
        ("{1, 2}", {1, 2}, False, "普通 set 可变，不可哈希"),
    ]
    for expr, obj, expect_ok, why in trials:
        try:
            set().add(obj)
            ok, result = True, "成功"
        except TypeError as e:
            ok, result = False, type(e).__name__
        guess = "成功" if expect_ok else "TypeError"
        mark = "[OK]" if ok == expect_ok else "[差异]"
        print(f"  s.add({expr})".ljust(36), f"-> {result:<10} 预判={guess} {mark} | {why}")

    t = (1, [2, 3])
    t[1].append(4)
    try:
        {t}
    except TypeError as e:
        print("  t[1].append(4) ->", t, "合法；但 {t} ->", type(e).__name__, "（引用没变，内容变了）")
    print("  集合里放集合要用 frozenset：", {frozenset({1, 2}), frozenset({3})})


def task3():
    A, B = {2, 4, 6, 8, 10, 12}, {3, 6, 9, 12, 15}
    for name, value in [("交集 A&B", A & B), ("并集 A|B", A | B), ("差 A-B", A - B),
                        ("差 B-A", B - A), ("对称差 A^B", A ^ B)]:
        print(f"  {name:<12} = {sorted(value)}")
    print("  恒等式 (A&B)|(A-B) == A :", (A & B) | (A - B) == A)
    print("  恒等式 (A|B)-(A&B) == A^B :", (A | B) - (A & B) == A ^ B)
    comp = {x for x in range(1, 31) if x % 4 == 0}
    print("  集合推导式 1~30 中 4 的倍数 :", sorted(comp))


def task4():
    data = [5, 2, 7, 2, 5, 9, 7, 3, 9, 1]
    a = list(set(data))
    b = []
    for x in data:                            # 按题目提示：不在新列表才 append
        if x not in b:
            b.append(x)
    c = list(dict.fromkeys(data))
    print("  原始数据 :", data)
    print("  方案1 list(set(data)) :", a, " 保序?", a == b)
    print("  方案2 手写循环保序   :", b)
    print("  方案3 dict.fromkeys  :", c)
    print("  方案2 == 方案3 :", b == c, "| 首次出现顺序 =", b)


def task5():
    class1 = [101, 103, 105, 107, 109, 103, 101]
    class2 = [102, 104, 106, 108, 109, 107, 102]
    c1, c2 = keep_order(class1), keep_order(class2)
    s1, s2 = set(c1), set(c2)
    both, only_one, only_c1 = s1 & s2, s1 ^ s2, s1 - s2
    print("  ① 1班保序去重 :", c1)
    print("    2班保序去重 :", c2)
    print("  ② 同时选两门 :", sorted(both))
    print("  ③ 只选一门(对称差) :", sorted(only_one))
    print("  ④ 选1班没选2班 :", sorted(only_c1))
    t_both = tuple(sorted(both))
    print("  ⑤ 交集转元组 :", t_both, "-> 再放进集合 :", {t_both})
    try:
        {set(both)}
    except TypeError as e:
        print("     反例：普通 set 不能当集合元素 ->", type(e).__name__)
    print("     原因：交集元素都是可哈希 int，且 tuple 不可变 => 整体可哈希")


def extra():
    nest = [[1, 2], [3, 4], [1, 2], [5, 6]]
    result = [list(t) for t in keep_order(tuple(x) for x in nest)]
    print("  嵌套列表 :", nest)
    print("  list -> tuple 去重 -> 转回 list :", result)


def main():
    sections = [
        ("任务1 切片删除：手写预判 vs 实测", task1),
        ("任务2 嵌套容器与可哈希辨析", task2),
        ("任务3 集合四则运算与集合推导式", task3),
        ("任务4 去重算法对比（保序 vs 无序）", task4),
        ("任务5 综合设计：两班选课统计", task5),
        ("拓展 嵌套列表去重", extra),
    ]
    print("实验3 Python 列表、元组、集合 —— 运行结果")
    for title, fn in sections:
        print("\n===== " + title + " =====")
        fn()


if __name__ == "__main__":
    main()
