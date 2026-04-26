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
    # 交差しない真下への k=10 移動。圧縮器を通すと1ターンになります。
    # ==========================================
    for i in range(R):
        do_move(0, i, i, 10)

    # ==========================================
    # フェーズ 2: 5列ごとの同時ソート
    # phase: (0, 5) -> 上半分を作る, (5, 10) -> 下半分を作る
    # ==========================================
    for phase in [(0, 3), (3, 6), (6, 10)]:
        start_t, end_t = phase
        needed = {t: t * 10 for t in range(start_t, end_t)}
        
        while any(needed[t] < t * 10 + 10 for t in range(start_t, end_t)):
            moved_any = False
            
            # ① 先頭にあるターゲットは即座に回収
            for t in range(start_t, end_t):
                if needed[t] >= t * 10 + 10: continue
                for j in range(R):
                    if S[j] and S[j][0] == needed[t]:
                        do_move(1, t, j, 1)
                        needed[t] += 1
                        moved_any = True
                        break
            if moved_any:
                continue

            # ② 先頭になければ、5つのターゲットのうち「一番浅い位置」にあるものを探す
            best_t, best_j, best_depth = -1, -1, 999
            for t in range(start_t, end_t):
                if needed[t] >= t * 10 + 10: continue
                for j in range(R):
                    for d in range(len(S[j])):
                        if S[j][d] == needed[t]:
                            if d < best_depth:
                                best_depth = d
                                best_j = j
                                best_t = t
                            break # 同じ列の中では一番上だけ見ればOK

            # ③ ターゲットの上にある邪魔な車両を「まとめて」別の出発線に退避
            remaining = best_depth
            buffered = []
            
            # バッファには「今作っていない方の5列」をフル活用する！
            buffer_candidates = [b for b in range(R) if not (start_t <= b < end_t)]
            
            for b in buffer_candidates:
                space = 15 - len(D[b])
                if space > 0:
                    take = min(remaining, space)
                    do_move(1, b, best_j, take) # k両まとめて一瞬で退避
                    buffered.append((b, take))
                    remaining -= take
                if remaining == 0: break
                
            # ターゲットを配置
            do_move(1, best_t, best_j, 1)
            needed[best_t] += 1
            
            # ④ 退避させていた車両を「逆順」で戻す（待避線の中の順番が完璧に元通りになります）
            for b, take in reversed(buffered):
                do_move(0, b, best_j, take)

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