import sys

def solve():
    # 入力の読み込み
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    
    R = int(input_data[0])
    
    # 盤面の状態管理
    # D[i]: 出発線 i の状態（インデックス0が先頭、末尾に追加/削除していく）
    # S[i]: 待避線 i の状態（インデックス0が先頭、先頭に追加/削除していく）
    D = [[] for _ in range(R)]
    S = [[] for _ in range(R)]
    
    idx = 1
    for i in range(R):
        for j in range(10):
            D[i].append(int(input_data[idx]))
            idx += 1
            
    moves = [] # (type, i, j, k) のタプルを記録
    
    def do_move(type_val, i, j, k):
        """盤面の状態を更新し、操作を記録する関数"""
        moves.append((type_val, i, j, k))
        if type_val == 0:
            # Type 0: 出発線 i の末尾から k 両を取り出し、待避線 j の先頭に連結
            cars = D[i][-k:]
            del D[i][-k:]
            S[j] = cars + S[j]
        else:
            # Type 1: 待避線 j の先頭から k 両を取り出し、出発線 i の末尾に連結
            cars = S[j][:k]
            del S[j][:k]
            D[i].extend(cars)

    # ==========================================
    # フェーズ 1: 全ての車両を待避線に退避する
    # ==========================================
    for i in range(R):
        # 10両まとめて一気に移動させるとターン数を節約できる
        do_move(0, i, i, 10)

    # ==========================================
    # フェーズ 2: ID 0 から 99 まで順番に所定の位置へ
    # ==========================================
    for target in range(10 * R):
        r = target // 10 # ターゲットが最終的に向かうべき出発線
        
        # ターゲットが現在の待避線のどこにあるかを探す
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
                
        # ターゲットの上に被さっている邪魔な車両を退避させる（掘り起こし）
        for _ in range(found_depth):
            # ターゲットの目的地(r)ではない適当な出発線をバッファとして使う
            buffer_d = (r + 1) % R
            
            # 容量オーバーを防ぐため、車両数が一番少ない待避線を選ぶ
            min_len = float('inf')
            buffer_s = -1
            for s in range(R):
                if s != found_s and len(S[s]) < min_len:
                    min_len = len(S[s])
                    buffer_s = s
                    
            # 邪魔な車両を1両取り出し、バッファ出発線を経由して別の待避線へ逃がす
            do_move(1, buffer_d, found_s, 1) # S -> D
            do_move(0, buffer_d, buffer_s, 1) # D -> S
            
        # ターゲットが待避線(found_s)の先頭に来たので、目的の出発線に移動させる
        do_move(1, r, found_s, 1)

    # ==========================================
    # 出力
    # ==========================================
    print(len(moves))
    for m in moves:
        print("1") # 1ターンに1回の移動しか行わない（交差制約を絶対満たす）
        print(f"{m[0]} {m[1]} {m[2]} {m[3]}")

if __name__ == '__main__':
    solve()