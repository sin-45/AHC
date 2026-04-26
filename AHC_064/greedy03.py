import sys

def solve():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    
    R = int(input_data[0])
    
    D = [[] for _ in range(R)]
    S = [[] for _ in range(R)]
    
    idx = 1
    for i in range(R):
        for j in range(10):
            D[i].append(int(input_data[idx]))
            idx += 1
            
    # 一旦、すべての移動を「1ターン1移動」の前提でリストに溜め込む
    sequential_moves = []
    
    def do_move(type_val, i, j, k):
        sequential_moves.append((type_val, i, j, k))
        if type_val == 0:
            cars = D[i][-k:]
            del D[i][-k:]
            S[j] = cars + S[j]
        else:
            cars = S[j][:k]
            del S[j][:k]
            D[i].extend(cars)

    # ==========================================
    # フェーズ 1: 全ての車両を待避線に退避する
    # ==========================================
    for i in range(R):
        do_move(0, i, i, 10)

    # ==========================================
    # フェーズ 2: ID 0 から 99 まで順番に所定の位置へ（初めの貪欲法）
    # ==========================================
    for target in range(10 * R):
        r = target // 10
        
        found_s = -1
        found_depth = -1
        for s in range(R):
            for depth in range(len(S[s])):
                if S[s][depth] == target:
                    found_s = s
                    found_depth = depth
                    break
            if found_s != -1:
                break
                
        # 邪魔な車両を退避させる（1両ずつ）
        for _ in range(found_depth):
            buffer_d = (r + 1) % R
            min_len = float('inf')
            buffer_s = -1
            for s in range(R):
                if s != found_s and len(S[s]) < min_len:
                    min_len = len(S[s])
                    buffer_s = s
                    
            do_move(1, buffer_d, found_s, 1) # S -> D
            do_move(0, buffer_d, buffer_s, 1) # D -> S
            
        # ターゲットを配置
        do_move(1, r, found_s, 1)

    # ==========================================
    # フェーズ 3: 解の圧縮（ターンのパッキング）
    # ==========================================
    compressed_turns = []
    current_turn = []
    used_d = set()
    used_s = set()
    
    for m in sequential_moves:
        type_val, i, j, k = m
        conflict = False
        
        # 条件1: 同じ出発線・待避線を1ターンに2回使ってはいけない
        if i in used_d or j in used_s:
            conflict = True
        else:
            # 条件2: すでに今のターンに登録されている移動と交差してはいけない
            for tm in current_turn:
                ti, tj = tm[1], tm[2]
                if (i < ti and j > tj) or (i > ti and j < tj):
                    conflict = True
                    break
        
        if conflict:
            # 衝突する場合は、今のターンを確定させて次のターンへ
            compressed_turns.append(current_turn)
            current_turn = [m]
            used_d = {i}
            used_s = {j}
        else:
            # 衝突しない場合は、同じターンに相乗り（圧縮）
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