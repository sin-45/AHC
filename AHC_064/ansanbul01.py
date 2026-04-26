import sys
import itertools
import copy
import time
import random

def run_simulation(R, initial_D, p):
    """
    ユーザーの「一番いいコード」のロジックでシミュレーションを実行する
    p: 出発線 i をどの待避線 p[i] に入れるかのリスト
    """
    D = [d[:] for d in initial_D]
    S = [[] for _ in range(R)]
    seq_moves = []

    def do_move(type_val, i, j, k):
        if k <= 0: return
        seq_moves.append((type_val, i, j, k))
        if type_val == 0:
            cars = D[i][-k:]
            del D[i][-k:]
            S[j] = cars + S[j]
        else:
            cars = S[j][:k]
            del S[j][:k]
            D[i].extend(cars)

    # 1. 初期分配 (指定された p に基づく)
    for i in range(R):
        do_move(0, i, p[i], 10)

    # 2. 前半戦 (0〜4)
    buffers_avail = [5, 6, 7, 8, 9]
    needed = {t: t * 10 for t in range(5)}
    while any(needed[t] < t * 10 + 10 for t in range(5)):
        candidates = []
        for t in range(5):
            if needed[t] >= t * 10 + 10: continue
            for j in range(R):
                if needed[t] in S[j]:
                    d = S[j].index(needed[t])
                    candidates.append((d, j, t))
                    break
        candidates.sort(key=lambda x: x[0])
        selected = []
        used_j, used_t = set(), set()
        for d, j, t in candidates:
            if j not in used_j and t not in used_t:
                selected.append((d, j, t))
                used_j.add(j); used_t.add(t)
        if not selected: break
        selected.sort(key=lambda x: x[1])
        plan_evacuate, plan_target = [], []
        for idx_sel, (depth, j, t) in enumerate(selected):
            b = buffers_avail[idx_sel]
            if depth > 0: plan_evacuate.append((b, j, depth))
            plan_target.append((t, j))
        for b, j, depth in plan_evacuate: do_move(1, b, j, depth)
        for t, j in plan_target: do_move(1, t, j, 1); needed[t] += 1
        for b, j, depth in reversed(plan_evacuate): do_move(0, b, j, depth)

    # 3. 後半戦 (5〜9)
    buffers_avail = [0, 1, 2, 3, 4]
    needed_2 = {t: t * 10 for t in range(5, 10)}
    while any(needed_2[t] < t * 10 + 10 for t in range(5, 10)):
        candidates = []
        for t in range(5, 10):
            if needed_2[t] >= t * 10 + 10: continue
            for j in range(R):
                if needed_2[t] in S[j]:
                    d = S[j].index(needed_2[t])
                    candidates.append((d, j, t))
                    break
        candidates.sort(key=lambda x: x[0])
        selected = []
        used_j, used_t = set(), set()
        for d, j, t in candidates:
            if j not in used_j and t not in used_t and d <= 5:
                selected.append((d, j, t))
                used_j.add(j); used_t.add(t)
        if not selected and candidates:
            d, j, t = candidates[0]
            selected.append((d, j, t))
        if not selected: break
        selected.sort(key=lambda x: x[1])
        plan_evacuate, plan_target = [], []
        for idx_sel, (depth, j, t) in enumerate(selected):
            if idx_sel < 5:
                b = buffers_avail[idx_sel]
                take = min(depth, 15 - len(D[b]))
                if take > 0: plan_evacuate.append((b, j, take))
                plan_target.append((t, j))
        for b, j, k in plan_evacuate: do_move(1, b, j, k)
        for t, j in plan_target: do_move(1, t, j, 1); needed_2[t] += 1
        for b, j, k in reversed(plan_evacuate): do_move(0, b, j, k)

    # 4. 圧縮器
    compressed = []
    curr = []
    u_d, u_s = set(), set()
    for m in seq_moves:
        v, i, j, k = m
        intersect = any((i<ti and j>tj) or (i>ti and j<tj) for _,ti,tj,_ in curr)
        if i in u_d or j in u_s or intersect:
            compressed.append(curr); curr, u_d, u_s = [m], {i}, {j}
        else:
            curr.append(m); u_d.add(i); u_s.add(j)
    if curr: compressed.append(curr)
    return compressed

def solve():
    start_time = time.time()
    input_data = sys.stdin.read().split()
    if not input_data: return
    R = int(input_data[0])
    initial_D = [[] for _ in range(R)]
    idx = 1
    for i in range(R):
        for j in range(10):
            initial_D[i].append(int(input_data[idx]))
            idx += 1

    # --- 戦略の準備 ---
    strategies = []
    
    # 1. オリジナル (Identity mapping)
    strategies.append(list(range(R)))

    # 2. マッチング最適化 (Greedy assignment for speed)
    cost_matrix = [[0]*R for _ in range(R)]
    for i in range(R):
        for j in range(R):
            cost_matrix[i][j] = sum(abs(j - (car_id // 10)) for car_id in initial_D[i])
    
    # 簡易的な最小コスト割り当て (10!は重いのでGreedyに)
    best_match = [-1]*R
    siding_used = [False]*R
    for i in range(R):
        best_j = -1
        min_c = float('inf')
        for j in range(R):
            if not siding_used[j] and cost_matrix[i][j] < min_c:
                min_c = cost_matrix[i][j]
                best_j = j
        best_match[i] = best_j
        siding_used[best_j] = True
    strategies.append(best_match)

    # --- 実行と選別 ---
    best_res = None
    min_turns = float('inf')

    # 時間の許す限りランダムな並び替えも試す
    # (最初は確実に戦略1と2を試す)
    idx_strat = 0
    while time.time() - start_time < 1.8: # 2秒制限を考慮
        if idx_strat < len(strategies):
            p = strategies[idx_strat]
        else:
            p = list(range(R))
            random.shuffle(p)
        
        res = run_simulation(R, initial_D, p)
        if len(res) < min_turns:
            min_turns = len(res)
            best_res = res
        
        idx_strat += 1
        if idx_strat > 100_000: break # 最大100回試行

    # 出力
    print(len(best_res))
    for turn in best_res:
        print(len(turn))
        for m in turn: print(f"{m[0]} {m[1]} {m[2]} {m[3]}")

if __name__ == '__main__':
    solve()

