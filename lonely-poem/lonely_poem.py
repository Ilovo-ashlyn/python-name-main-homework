# -*- coding: utf-8 -*-
"""教材 P205 实例 6A：孤独的古诗词 + 思考与练习 6.1 / 6.2 / 6.3"""


def clean(poem):
    """去掉逗号句号，只留下汉字。"""
    return poem.replace("，", "").replace("。", "")


def is_lonely(poem):
    """每个汉字都只出现一次 -> 孤独的古诗词（代码 6A 的思路）。"""
    s = clean(poem)
    return len(s) == len(set(s))


def main():
    # 代码 6A：李白《独坐敬亭山》，被誉为唐诗中最孤独的一首
    poem = "众鸟高飞尽，孤云独去闲。相看两不厌，只有敬亭山。"
    print(f"《独坐敬亭山》孤独吗？ {is_lonely(poem)}")

    # 练习 6.3：换一首不孤独的诗，看看是哪些字重复了
    poem = "床前明月光，疑是地上霜。举头望明月，低头思故乡。"
    s = clean(poem)
    dup = sorted({c for c in s if s.count(c) > 1})
    print(f"《静夜思》孤独吗？ {is_lonely(poem)}，重复的字：{'、'.join(dup)}")

    # 练习 6.1：列表 <-> 集合互相转换
    a = [3, 1, 2, 3, 2]
    print("列表", a, "-> 集合", set(a), "-> 列表", list(set(a)))

    # 练习 6.2：集合的并、交、对称差、差
    s1, s2 = {1, 3, 5, 6}, {2, 5, 6}
    print("S1 | S2 =", s1 | s2, "   S1 & S2 =", s1 & s2)
    print("S1 ^ S2 =", s1 ^ s2, "   S1 - S2 =", s1 - s2)


if __name__ == "__main__":
    main()
