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
    # 全列で一斉に真下へ10両落とします（交差ゼロなので1ターンで完了）
    # ==========================================
    for i in range(R):
        do_move(0, i, i, 10)

    # ==========================================
    # 2. 前半戦（0〜4）の完全並列ソート
    # バッファとして 5〜9 の5列をフル活用します
    # ==========================================
    buffers_avail = [5, 6, 7, 8, 9]
    needed = {t: t * 10 for t in range(5)}
    
    while any(needed[t] < t * 10 + 10 for t in range(5)):
        candidates = []
        # 各ターゲットがどこにあるかを全てリストアップ
        for t in range(5):
            if needed[t] >= t * 10 + 10: continue
            for j in range(R):
                for d in range(len(S[j])):
                    if S[j][d] == needed[t]:
                        candidates.append((d, j, t))
                        break
                        
        # 掘りやすい（浅い）ものから優先的に選ぶ
        candidates.sort(key=lambda x: x[0])
        
        selected = []
        used_j, used_t = set(), set()
        for d, j, t in candidates:
            # 同じ待避線からは1回に1つしか掘らない
            if j not in used_j and t not in used_t:
                selected.append((d, j, t))
                used_j.add(j); used_t.add(t)
                
        if not selected: break
        
        # 【最重要】交差を防ぐため、待避線の番号(j)が小さい順に並べ替える
        selected.sort(key=lambda x: x[1])
        
        plan_evacuate, plan_target = [], []
        
        # 番号順に、空いているバッファを割り当てる（これで絶対に交差しない）
        for idx_sel, (depth, j, t) in enumerate(selected):
            b = buffers_avail[idx_sel]
            if depth > 0: plan_evacuate.append((b, j, depth))
            plan_target.append((t, j))
            
        # 一斉実行（圧縮器により1ターンにまとまる）
        for b, j, depth in plan_evacuate: do_move(1, b, j, depth)
        for t, j in plan_target: do_move(1, t, j, 1); needed[t] += 1
        for b, j, depth in reversed(plan_evacuate): do_move(0, b, j, depth)

    # ==========================================
    # 3. 前半終了のトランジション（Hide Blocks）
    # 0〜4の完成ブロック（10両）を、容量に空きのある待避線へ一時的に隠す
    # ==========================================
    hidden_blocks = []
    # 車両が10両以下の待避線を探す（数学的に必ず5つ以上存在する）
    avail_s = [j for j in range(R) if len(S[j]) <= 10]
    avail_s.sort()
    for i in range(5):
        t = i
        s = avail_s[i]
        do_move(0, t, s, 10)
        hidden_blocks.append((t, s))

    # ==========================================
    # 4. 後半戦（5〜9）の完全並列ソート
    # 空っぽになった 0〜4 の5列をバッファとしてフル活用します
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
    # 5. 後半終了のトランジション（Restore Blocks）
    # 隠しておいた 0〜4 の完成ブロックを元の場所に戻す
    # ==========================================
    for t, s in hidden_blocks:
        do_move(1, t, s, 10)

    # ==========================================
    # 6. ターンの並列化（解の圧縮器）
    # 上記で作られた「交差しない移動」を自動的に1ターンにまとめあげる
    # ==========================================
    compressed = []
    curr = []
    used_d, used_s = set(), set()
    for m in seq_moves:
        t_val, i, j, k = m
        conflict = False
        if i in used_d or j in used_s: conflict = True
        else:
            for tm in curr:
                ti, tj = tm[1], tm[2]
                if (i < ti and j > tj) or (i > ti and j < tj):
                    conflict = True; break
        if conflict:
            compressed.append(curr)
            curr, used_d, used_s = [m], {i}, {j}
        else:
            curr.append(m); used_d.add(i); used_s.add(j)
    if curr: compressed.append(curr)

    # 出力
    print(len(compressed))
    for turn in compressed:
        print(len(turn))
        for m in turn: print(f"{m[0]} {m[1]} {m[2]} {m[3]}")

if __name__ == '__main__':
    solve()