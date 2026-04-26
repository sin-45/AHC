import sys
import itertools
import copy

def simulate(R, initial_D, use_matching=False):
    # 各シミュレーション用にデータをコピー
    D = copy.deepcopy(initial_D)
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

    # --- 1. 初期配置フェーズ ---
    if use_matching:
        # マッチング戦略
        cost_matrix = [[0] * R for _ in range(R)]
        for i in range(R):
            for j in range(R):
                cost = 0
                for car_id in D[i]:
                    target_track = car_id // 10
                    cost += abs(j - target_track)
                cost_matrix[i][j] = cost

        best_p = None
        min_total_cost = float('inf')
        for p in itertools.permutations(range(R)):
            current_cost = sum(cost_matrix[i][p[i]] for i in range(R))
            if current_cost < min_total_cost:
                min_total_cost = current_cost
                best_p = p
        for i in range(R):
            do_move(0, i, best_p[i], 10)
    else:
        # シンプルダンプ戦略
        for i in range(R):
            do_move(0, i, i, 10)

    # --- 2. 前半戦 (0-4) ---
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

    # --- 3. 後半戦 (5-9) ---
    buffers_avail = [0, 1, 2, 3, 4]
    needed = {t: t * 10 for t in range(5, 10)}
    while any(needed[t] < t * 10 + 10 for t in range(5, 10)):
        candidates = []
        for t in range(5, 10):
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
        for t, j in plan_target: do_move(1, t, j, 1); needed[t] += 1
        for b, j, k in reversed(plan_evacuate): do_move(0, b, j, k)

    # --- 4. 圧縮器 ---
    compressed = []
    curr = []
    u_d, u_s = set(), set()
    for m in seq_moves:
        v, i, j, k = m
        intersect = any((i < ti and j > tj) or (i > ti and j < tj) for _, ti, tj, _ in curr)
        if i in u_d or j in u_s or intersect:
            compressed.append(curr)
            curr, u_d, u_s = [m], {i}, {j}
        else:
            curr.append(m); u_d.add(i); u_s.add(j)
    if curr: compressed.append(curr)
    return compressed

def solve():
    input_data = sys.stdin.read().split()
    if not input_data: return
    R = int(input_data[0])
    initial_D = [[] for _ in range(R)]
    idx = 1
    for i in range(R):
        for j in range(10):
            initial_D[i].append(int(input_data[idx]))
            idx += 1
    
    # 両方の戦略を実行
    res_simple = simulate(R, initial_D, use_matching=False)
    res_matching = simulate(R, initial_D, use_matching=True)
    
    # ターン数が少ない方を採用
    final_res = res_simple if len(res_simple) < len(res_matching) else res_matching
    
    # 出力
    print(len(final_res))
    for turn in final_res:
        print(len(turn))
        for m in turn: print(f"{m[0]} {m[1]} {m[2]} {m[3]}")

if __name__ == '__main__':
    solve()
    
# min(10, 13)
