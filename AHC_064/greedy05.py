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
    # フェーズ 1: 全ての車両を待避線に退避
    # ==========================================
    for i in range(R):
        do_move(0, i, i, 10)

    # ==========================================
    # フェーズ 2: 上半分（0〜4）の同時構築
    # 5つのゴールを同時に追いかけます
    # ==========================================
    # needed[t] は「出発線tが次に欲しがっているID」
    needed = {t: t * 10 for t in range(5)}
    
    # 0〜4のすべてが10両揃うまでループ
    while any(needed[t] < t * 10 + 10 for t in range(5)):
        moved_any = False
        
        # ① 5つのゴールのうち、待避線の「先頭」にあるものがあれば即座に入れる
        for t in range(5):
            if needed[t] >= t * 10 + 10: continue
            for j in range(R):
                if S[j] and S[j][0] == needed[t]:
                    do_move(1, t, j, 1)
                    needed[t] += 1 # 次のターゲットへ更新
                    moved_any = True
                    break
            if moved_any: break # 盤面が変わったので最初からチェックし直す
            
        if moved_any:
            continue
            
        # ② 先頭に何もなければ、「一番浅い位置」にあるターゲットを探す
        best_t, best_j, best_depth = -1, -1, float('inf')
        for t in range(5):
            if needed[t] >= t * 10 + 10: continue
            target = needed[t]
            for j in range(R):
                for d in range(len(S[j])):
                    if S[j][d] == target:
                        if d < best_depth:
                            best_depth = d
                            best_j = j
                            best_t = t
                        break # この待避線の中では一番浅いものだけ見ればOK

        # ③ 一番浅いターゲットの上に乗っている邪魔な車両を「1両だけ」どかす
        car = S[best_j][0]
        if car >= 50:
            # 下半分の車両なら、下半分の出発線(5~9)へ投げ捨てる
            best_d = min(range(5, 10), key=lambda x: len(D[x]))
            do_move(1, best_d, best_j, 1)
        else:
            # 上半分の車両なら、他の待避線へ退避
            best_s = min([x for x in range(R) if x != best_j], key=lambda x: len(S[x]))
            transit_d = best_t # 現在構築中の出発線を「一時的な経由地」として使う
            do_move(1, transit_d, best_j, 1)
            do_move(0, transit_d, best_s, 1)

    # ==========================================
    # フェーズ 3: ゴミ箱（5〜9）のリセット
    # ==========================================
    for d_idx in range(5, 10):
        while len(D[d_idx]) > 0:
            best_s = min(range(R), key=lambda x: len(S[x]))
            do_move(0, d_idx, best_s, 1)

    # ==========================================
    # フェーズ 4: 下半分（5〜9）の同時構築
    # 同様に5つのゴールを同時に追いかけます
    # ==========================================
    needed = {t: t * 10 for t in range(5, 10)}
    while any(needed[t] < t * 10 + 10 for t in range(5, 10)):
        moved_any = False
        
        for t in range(5, 10):
            if needed[t] >= t * 10 + 10: continue
            for j in range(R):
                if S[j] and S[j][0] == needed[t]:
                    do_move(1, t, j, 1)
                    needed[t] += 1
                    moved_any = True
                    break
            if moved_any: break
            
        if moved_any:
            continue
            
        best_t, best_j, best_depth = -1, -1, float('inf')
        for t in range(5, 10):
            if needed[t] >= t * 10 + 10: continue
            target = needed[t]
            for j in range(R):
                for d in range(len(S[j])):
                    if S[j][d] == target:
                        if d < best_depth:
                            best_depth = d
                            best_j = j
                            best_t = t
                        break

        # 下半分を作る時は、ゴミ箱が使えないので全て他の待避線へ退避
        best_s = min([x for x in range(R) if x != best_j], key=lambda x: len(S[x]))
        transit_d = best_t
        do_move(1, transit_d, best_j, 1)
        do_move(0, transit_d, best_s, 1)

    # ==========================================
    # フェーズ 5: ターンの並列化（圧縮）
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