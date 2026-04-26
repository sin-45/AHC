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

    # 1. 全車両を待避線へ (1ターン)
    for i in range(R):
        do_move(0, i, i, 10)

    def sort_range(target_range, buffer_range):
        needed = {t: t * 10 for t in target_range}
        while any(needed[t] < t * 10 + 10 for t in target_range):
            candidates = []
            for t in target_range:
                if needed[t] >= t * 10 + 10: continue
                # 現在のターゲットがどこにあるか探す
                found = False
                for j in range(R):
                    for d in range(len(S[j])):
                        if S[j][d] == needed[t]:
                            candidates.append((d, j, t))
                            found = True; break
                    if found: break
            
            # 交差を防ぐため、source_j でソートして並列化可能なものを選ぶ
            candidates.sort(key=lambda x: x[1])
            selected = []
            last_j = -1
            used_t = set()
            
            for d, j, t in candidates:
                if j > last_j and t not in used_t:
                    # バッファの空き容量チェック (Track cap=15)
                    b = buffer_range[len(selected)]
                    if len(D[b]) + d <= 15:
                        selected.append((d, j, t))
                        last_j = j
                        used_t.add(t)
                if len(selected) >= len(buffer_range): break

            if not selected: break

            # 3ステップ移動 (退避 -> 移動 -> 復元)
            # 1. 退避
            for idx_sel, (depth, j, t) in enumerate(selected):
                if depth > 0: do_move(1, buffer_range[idx_sel], j, depth)
            # 2. ターゲット移動
            for idx_sel, (depth, j, t) in enumerate(selected):
                do_move(1, t, j, 1)
                needed[t] += 1
            # 3. 復元 (逆順で行う)
            for idx_sel in reversed(range(len(selected))):
                depth, j, t = selected[idx_sel]
                if depth > 0: do_move(0, buffer_range[idx_sel], j, depth)

    # 前半戦: 0-4 を完成させる (5-9 をバッファに使用)
    sort_range(range(5), range(5, 10))

    # 完成した 0-4 を、5-9 の作業を邪魔しないよう待避線へ一時移動
    # 容量に余裕（計15両以下）がある待避線に逃がす
    for i in range(5):
        for j in range(R):
            if len(S[j]) <= 10:
                do_move(0, i, j, 10)
                break

    # 後半戦: 5-9 を完成させる (空いた 0-4 をバッファに使用)
    sort_range(range(5, 10), range(5))

    # 最後に待避線にある 0-4 の完成ブロックを戻す
    for t in range(5):
        target_val = t * 10
        for j in range(R):
            if len(S[j]) >= 10 and S[j][0] == target_val:
                do_move(1, t, j, 10)
                break

    # 解の圧縮器
    compressed = []
    curr = []
    used_d, used_s = set(), set()
    for m in seq_moves:
        t_val, i, j, k = m
        conflict = (i in used_d or j in used_s)
        if not conflict:
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

    print(len(compressed))
    for turn in compressed:
        print(len(turn))
        for m in turn: print(f"{m[0]} {m[1]} {m[2]} {m[3]}")

if __name__ == '__main__':
    solve()