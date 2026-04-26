import sys

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

    # ==========================================
    # 1. 超高速分配（1-Turn Dump）
    # ==========================================
    for i in range(R):
        do_move(0, i, i, 10)

    # ==========================================
    # 2. 前半戦（0〜4） - ユーザー提供の「一番いいコード」
    # ==========================================
    buffers_avail = [5, 6, 7, 8, 9]
    needed = {t: t * 10 for t in range(5)}
    
    while any(needed[t] < t * 10 + 10 for t in range(5)):
        candidates = []
        for t in range(5):
            if needed[t] >= t * 10 + 10: continue
            for j in range(R):
                for d in range(len(S[j])):
                    if S[j][d] == needed[t]:
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

    # ==========================================
    # 3. 後半戦（5〜9） - 前半戦をお手本にした並列ロジック
    # バッファとして完成済みのD0〜D4の空き（各5両分）を使用
    # ==========================================
    buffers_avail = [0, 1, 2, 3, 4]
    needed = {t: t * 10 for t in range(5, 10)}
    
    while any(needed[t] < t * 10 + 10 for t in range(5, 10)):
        candidates = []
        for t in range(5, 10):
            if needed[t] >= t * 10 + 10: continue
            for j in range(R):
                for d in range(len(S[j])):
                    if S[j][d] == needed[t]:
                        candidates.append((d, j, t))
                        break
        
        candidates.sort(key=lambda x: x[0])
        
        selected = []
        used_j, used_t = set(), set()
        for d, j, t in candidates:
            # D0-D4には5両分の隙間があるため、深さ5以下のものを優先的に並列処理
            if j not in used_j and t not in used_t and d <= 5:
                selected.append((d, j, t))
                used_j.add(j); used_t.add(t)
        
        # もし深さ5以下で取れるものが1つもない場合は、単一の掘り出しを実行（安全策）
        if not selected and candidates:
            d, j, t = candidates[0]
            selected.append((d, j, t))

        if not selected: break
        selected.sort(key=lambda x: x[1])
        
        plan_evacuate, plan_target = [], []
        for idx_sel, (depth, j, t) in enumerate(selected):
            # 最大5つのバッファを割り当て
            if idx_sel < 5:
                b = buffers_avail[idx_sel]
                # 避難先（D0-D4）の容量を超えないように制御
                take = min(depth, 15 - len(D[b]))
                if take > 0: plan_evacuate.append((b, j, take))
                plan_target.append((t, j))
            
        for b, j, k in plan_evacuate: do_move(1, b, j, k)
        for t, j in plan_target: do_move(1, t, j, 1); needed[t] += 1
        for b, j, k in reversed(plan_evacuate): do_move(0, b, j, k)

    # ==========================================
    # 4. ターンの並列化（解の圧縮器）
    # ==========================================
    compressed = []
    curr = []
    u_d, u_s = set(), set()
    for m in seq_moves:
        v, i, j, k = m
        if i in u_d or j in u_s or any((i<ti and j>tj) or (i>ti and j<tj) for _,ti,tj,_ in curr):
            compressed.append(curr)
            curr, u_d, u_s = [m], {i}, {j}
        else:
            curr.append(m); u_d.add(i); u_s.add(j)
    if curr: compressed.append(curr)

    # 出力
    print(len(compressed))
    for turn in compressed:
        print(len(turn))
        for m in turn: print(f"{m[0]} {m[1]} {m[2]} {m[3]}")

if __name__ == '__main__':
    solve()