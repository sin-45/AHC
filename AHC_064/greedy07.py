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
    # フェーズ 1: 超高速分配（1ターン完了）
    # 交差しない真下への k=10 移動。圧縮器により1ターンになります。
    # ==========================================
    for i in range(R):
        do_move(0, i, i, 10)

    # ==========================================
    # フェーズ 2: 5列ごとの同時ソート
    # ==========================================
    for phase in [(0, 5), (5, 10)]:
        start_t, end_t = phase
        needed = {t: t * 10 for t in range(start_t, end_t)}
        # 使っていない残りの5列をバッファとしてフル活用
        buffers_avail = [b for b in range(R) if not (start_t <= b < end_t)]
        
        while any(needed[t] < t * 10 + 10 for t in range(start_t, end_t)):
            # ① 直接ゴールできるものは即座に入れる
            moved_direct = False
            for t in range(start_t, end_t):
                if needed[t] >= t * 10 + 10: continue
                for j in range(R):
                    if S[j] and S[j][0] == needed[t]:
                        do_move(1, t, j, 1)
                        needed[t] += 1
                        moved_direct = True
                        break
            if moved_direct:
                continue

            # ② 一度動かしたい操作（掘り出すべきブロック）を全てリストアップする
            candidates = []
            for t in range(start_t, end_t):
                if needed[t] >= t * 10 + 10: continue
                for j in range(R):
                    for d in range(len(S[j])):
                        if S[j][d] == needed[t]:
                            candidates.append((d, j, t))
                            break
            
            # 掘りやすい（浅い）ものから優先的に計画に組み込む
            candidates.sort(key=lambda x: x[0]) 
            
            selected_to_dig = []
            used_j = set()
            total_buffer_space = sum(15 - len(D[b]) for b in buffers_avail)
            
            for d, j, t in candidates:
                # バッファの総容量に収まる範囲で、複数の列の掘り出しを同時に計画
                if j not in used_j and d <= total_buffer_space:
                    selected_to_dig.append((j, d, t))
                    used_j.add(j)
                    total_buffer_space -= d
            
            if not selected_to_dig:
                break

            # ③ 【最重要】交差しないようにバッファを割り当てる
            # 待避線のインデックス(j)を小さい順にソートする
            selected_to_dig.sort(key=lambda x: x[0])
            
            plan_evacuate = []
            plan_target = []
            
            b_idx = 0
            b_used = 0
            
            # jが小さいものから順に、番号の小さいバッファ(b)に割り当てる -> 交差ゼロ！
            for j, depth, t in selected_to_dig:
                remaining = depth
                while remaining > 0:
                    b = buffers_avail[b_idx]
                    space = (15 - len(D[b])) - b_used
                    if space <= 0:
                        b_idx += 1
                        b_used = 0
                        continue
                    
                    take = min(remaining, space)
                    plan_evacuate.append((b, j, take))
                    b_used += take
                    remaining -= take
                    
                plan_target.append((t, j))

            # ④ 計画を一斉に実行する
            # まず、邪魔なブロックを全てバッファへ（交差ゼロなので1ターンで一斉に動く）
            for b, j, take in plan_evacuate:
                do_move(1, b, j, take)
                
            # 次に、露出したターゲットを目的地へ
            for t, j in plan_target:
                do_move(1, t, j, 1)
                needed[t] += 1
                
            # 最後に、退避させていたブロックを「逆順」で戻す（元の並び順が完璧に復元される＆これも1ターンで動く）
            for b, j, take in reversed(plan_evacuate):
                do_move(0, b, j, take)

    # ==========================================
    # フェーズ 3: ターンの並列化（解の圧縮）
    # ==========================================
    compressed_turns = []
    current_turn = []
    used_d = set()
    used_s = set()
    
    for m in seq_moves:
        type_val, i, j, k = m
        conflict = False
        
        if i in used_d or j in used_s:
            conflict = True
        else:
            for tm in current_turn:
                ti, tj = tm[1], tm[2]
                if (i < ti and j > tj) or (i > ti and j < tj):
                    conflict = True
                    break
                    
        if conflict:
            compressed_turns.append(current_turn)
            current_turn = [m]
            used_d = {i}
            used_s = {j}
        else:
            current_turn.append(m)
            used_d.add(i)
            used_s.add(j)
            
    if current_turn:
        compressed_turns.append(current_turn)

    # ==========================================
    # 出力
    # ==========================================
    print(len(compressed_turns))
    for turn in compressed_turns:
        print(len(turn))
        for m in turn:
            print(f"{m[0]} {m[1]} {m[2]} {m[3]}")

if __name__ == '__main__':
    solve()