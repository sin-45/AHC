import sys

# 再帰深度の引き上げ（DP用）
sys.setrecursionlimit(2000)

def solve():
    input_data = sys.stdin.read().split()
    if not input_data: return
    R = int(input_data[0])
    
    D = [[] for _ in range(R)]
    S = [[] for _ in range(R)]
    
    idx = 1
    for i in range(R):
        for j in range(10):
            D[i].append(int(input_data[idx]))
            idx += 1
            
    seq_moves = []
    
    def do_move(t_val, i, j, k):
        if k <= 0: return
        seq_moves.append((t_val, i, j, k))
        if t_val == 0:
            cars = D[i][-k:]; del D[i][-k:]
            S[j] = cars + S[j]
        else:
            cars = S[j][:k]; del S[j][:k]
            D[i].extend(cars)

    # 交差制約 (i1 < i2 => j1 < j2) を満たす最大セットをDPで抽出
    def get_best_parallel_moves(candidates, max_buffers):
        # candidates: [(depth, siding_j, target_i), ...]
        candidates.sort(key=lambda x: x[2]) # target_i でソート
        n = len(candidates)
        memo = {}

        def dp(idx, last_j, used_b):
            state = (idx, last_j, used_b)
            if state in memo: return memo[state]
            if idx == n: return (0, [])
            
            # 選択しない場合
            res_c, res_l = dp(idx + 1, last_j, used_b)
            
            # 選択する場合 (交差せず、バッファが足りる)
            d, j, t = candidates[idx]
            cost = 1 if d > 0 else 0
            if j > last_j and used_b + cost <= max_buffers:
                c, l = dp(idx + 1, j, used_b + cost)
                if 1 + c > res_c:
                    res_c, res_l = 1 + c, [(d, j, t)] + l
            
            memo[state] = (res_c, res_l)
            return memo[state]

        return dp(0, -1, 0)[1]

    # 1. 初期化: 全車両を待避線へ
    for i in range(R): do_move(0, i, i, 10)

    def run_phase(target_range, buffer_range, max_depth_limit=15):
        needed = {t: t * 10 for t in target_range}
        while any(needed[t] < t * 10 + 10 for t in target_range):
            candidates = []
            for t in target_range:
                if needed[t] >= t * 10 + 10: continue
                for j in range(R):
                    if needed[t] in S[j]:
                        d = S[j].index(needed[t])
                        # バッファ容量に収まるものだけ候補にする
                        if d <= max_depth_limit:
                            candidates.append((d, j, t))
                        break
            
            selected = get_best_parallel_moves(candidates, len(buffer_range))
            
            # 候補があるのにLISで選べなかった、または深すぎる場合のフォールバック
            if not selected:
                # 最も浅いターゲットを1つだけ処理
                all_c = []
                for t in target_range:
                    if needed[t] >= t * 10 + 10: continue
                    for j in range(R):
                        if needed[t] in S[j]:
                            all_c.append((S[j].index(needed[t]), j, t))
                            break
                if not all_c: break
                all_c.sort(key=lambda x: x[0])
                selected = [all_c[0]]

            # 移動実行
            plan_evac = []
            for idx_sel, (depth, j, t) in enumerate(selected):
                if depth > 0:
                    # バッファは buffer_range を使い回す
                    b = buffer_range[idx_sel % len(buffer_range)]
                    # 実際のTrack空き容量を確認
                    actual_k = min(depth, 15 - len(D[b]))
                    if actual_k > 0:
                        do_move(1, b, j, actual_k)
                        plan_evac.append((b, j, actual_k))
            
            for d, j, t in selected:
                do_move(1, t, j, 1)
                needed[t] += 1
            
            for b, j, k in reversed(plan_evac):
                do_move(0, b, j, k)

    # 2. 前半戦 (0-4)
    run_phase(range(5), range(5, 10), 15)

    # 3. 後半戦 (5-9) 
    # D0-D4には既に10両あるため、バッファとして使えるのは「5両分」のみ
    run_phase(range(5, 10), range(5), 5)

    # 4. 圧縮
    compressed = []
    curr = []
    u_d, u_s = set(), set()
    for m in seq_moves:
        v, i, j, k = m
        # 交差判定
        intersect = any((i < ti and j > tj) or (i > ti and j < tj) for _, ti, tj, _ in curr)
        if i in u_d or j in u_s or intersect:
            compressed.append(curr)
            curr, u_d, u_s = [m], {i}, {j}
        else:
            curr.append(m); u_d.add(i); u_s.add(j)
    if curr: compressed.append(curr)

    print(len(compressed))
    for turn in compressed:
        print(len(turn))
        for m in turn: print(f"{m[0]} {m[1]} {m[2]} {m[3]}")

if __name__ == '__main__':
    solve()