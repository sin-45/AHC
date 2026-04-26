import sys

def solve():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    
    R = int(input_data[0])
    
    # 盤面の状態管理
    # D[i]: 出発線 i の状態（インデックス0が先頭/出口側、末尾に追加・削除していく）
    # S[i]: 待避線 i の状態（インデックス0が先頭、先頭に追加・削除していく）
    D = [[] for _ in range(R)]
    S = [[] for _ in range(R)]
    
    idx = 1
    for i in range(R):
        for j in range(10):
            D[i].append(int(input_data[idx]))
            idx += 1
            
    moves = []
    
    def do_move(type_val, i, j, k):
        moves.append((type_val, i, j, k))
        if type_val == 0:
            # Type 0: 出発線 i の末尾 -> 待避線 j の先頭
            cars = D[i][-k:]
            del D[i][-k:]
            S[j] = cars + S[j]
        else:
            # Type 1: 待避線 j の先頭 -> 出発線 i の末尾
            cars = S[j][:k]
            del S[j][:k]
            D[i].extend(cars)

    # ==========================================
    # フェーズ 1: バケツソート（IDの十の位で仕分け）
    # ==========================================
    # 各出発線の車両を、所属すべき待避線へ送る
    for i in range(R):
        while len(D[i]) > 0:
            v = D[i][-1]
            target_s = v // 10 # IDから目的の待避線を決定
            do_move(0, i, target_s, 1)
            
    # ==========================================
    # フェーズ 2: 各出発線を順番に完成させる
    # ==========================================
    for t in range(R):
        # 邪魔な車両を一時的に避難させる隣の待避線をバッファとして使う
        # （各待避線には10両しか入っていないため、追加で9両入れても容量20を超えない）
        s_buf = (t + 1) % R
        
        for step in range(10):
            target_v = t * 10 + step
            
            moved_to_buf = 0 # バッファに逃がした車両数
            
            # ターゲットが見つかるまで待避線 t を掘る
            while True:
                front_v = S[t][0]
                if front_v == target_v:
                    # ターゲット発見！出発線の末尾に入れる
                    do_move(1, t, t, 1)
                    break
                else:
                    # 違う車両は、出発線 t を「経由」してバッファ待避線へ逃がす
                    do_move(1, t, t, 1)      # S[t] -> D[t]
                    do_move(0, t, s_buf, 1)  # D[t] -> s_buf
                    moved_to_buf += 1
                    
            # ターゲットを配置し終わったら、バッファに逃がした車両を元に戻す
            if moved_to_buf > 0:
                # まとめて移動（k両）させることで、ターン数を節約しつつ順番も維持！
                do_move(1, t, s_buf, moved_to_buf) # s_buf -> D[t]
                do_move(0, t, t, moved_to_buf)     # D[t] -> S[t]

    # ==========================================
    # 出力
    # ==========================================
    print(len(moves))
    for m in moves:
        # 交差制約を回避するため、安全に1ターン1回の移動を行う
        print("1")
        print(f"{m[0]} {m[1]} {m[2]} {m[3]}")

if __name__ == '__main__':
    solve()