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
    # フェーズ 2: 上半分（0〜4）の完成
    # 下半分（5〜9）の出発線を「巨大なゴミ箱」としてフル活用する
    # ==========================================
    for t in range(5):
        for step in range(10):
            target = t * 10 + step
            
            # ターゲットが待避線のどこにあるか探す
            s_idx, depth = -1, -1
            for j in range(R):
                for d in range(len(S[j])):
                    if S[j][d] == target:
                        s_idx, depth = j, d
                        break
                if s_idx != -1: break
            
            # ターゲットの上に被さっている車両をどかす
            for _ in range(depth):
                car = S[s_idx][0]
                
                if car >= 50:
                    # 【アイデアの核心】下半分の車両なら、下半分の出発線(5~9)へ投げ捨てる！
                    # 一番空いている下半分の線路を選ぶ
                    best_d = min(range(5, 10), key=lambda x: len(D[x]))
                    do_move(1, best_d, s_idx, 1)
                else:
                    # 上半分の車両なら、他の待避線へ一時避難（出発線tを経由）
                    best_s = min([x for x in range(R) if x != s_idx], key=lambda x: len(S[x]))
                    do_move(1, t, s_idx, 1)  # S -> D
                    do_move(0, t, best_s, 1) # D -> S
            
            # ターゲットを目的地に配置
            do_move(1, t, s_idx, 1)

    # ==========================================
    # フェーズ 3: 下半分のリセット
    # ゴミ箱として使っていた下半分の出発線から、一旦待避線へ全て戻す
    # ==========================================
    for d_idx in range(5, 10):
        while len(D[d_idx]) > 0:
            best_s = min(range(R), key=lambda x: len(S[x]))
            do_move(0, d_idx, best_s, 1)

    # ==========================================
    # フェーズ 4: 下半分（5〜9）の完成
    # ==========================================
    for t in range(5, 10):
        for step in range(10):
            target = t * 10 + step
            
            s_idx, depth = -1, -1
            for j in range(R):
                for d in range(len(S[j])):
                    if S[j][d] == target:
                        s_idx, depth = j, d
                        break
                if s_idx != -1: break

            for _ in range(depth):
                # 邪魔な車両は他の待避線へ適当に散らす
                best_s = min([x for x in range(R) if x != s_idx], key=lambda x: len(S[x]))
                do_move(1, t, s_idx, 1)
                do_move(0, t, best_s, 1)

            do_move(1, t, s_idx, 1)

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