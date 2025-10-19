import sys
import heapq

sys.setrecursionlimit(10**6)

class Solve:
    def __init__(self, N, H, C, A):
        self.n = N
        self.initial_h = H[:]
        self.initial_c = C[:]
        self.total_initial_h = sum(self.initial_h)
        self.a = A
        self.actions = []

    def solve(self):
        self.beam_search()
        self.output()

    def score_func(self, state):
        """
        状態を評価してスコアを返す。スコアが高いほど良い状態。
        """
        # ✨ stateタプルから opened_count を受け取る
        h, c, opened_chests, actions, total_overkill, opened_count = state
        
        SCORE_PER_CHEST = 100_000
        TOTAL_DAMAGE_WEIGHT = 10
        OVERKILL_PENALTY = 30
        
        # ✨ O(N)の計算から O(1)の直接参照になり高速化
        score = opened_count * SCORE_PER_CHEST
        
        current_hp_sum = sum(hp for hp in h if hp > 0)
        total_damage_dealt = self.total_initial_h - current_hp_sum
        score += total_damage_dealt * TOTAL_DAMAGE_WEIGHT
        
        score -= (total_overkill - 1000) * OVERKILL_PENALTY
        
        return score

    def beam_search(self):
        BEAM_WIDTH = 6

        # ✨ 状態に `opened_count` (開けた宝箱の数) を追加
        initial_state = (
            self.initial_h[:],
            self.initial_c[:],
            [False] * self.n,
            [],
            0, # total_overkill
            0  # opened_count
        )
        
        beam = [initial_state]
        best_solution_actions = None

        max_turns = sum(self.initial_h)

        for t in range(max_turns):
            if not beam:
                break

            next_candidates = []
            
            # ✨ opened_count をループで受け取る
            for h, c, opened_chests, actions, total_overkill, opened_count in beam:
                # 1. 武器での攻撃
                for weapon_idx in range(self.n):
                    if opened_chests[weapon_idx] and c[weapon_idx] > 0:
                        best_chest_for_weapon = -1
                        max_damage = 0
                        for chest_idx in range(self.n):
                            if not opened_chests[chest_idx]:
                                if self.a[weapon_idx][chest_idx] > max_damage:
                                    max_damage = self.a[weapon_idx][chest_idx]
                                    best_chest_for_weapon = chest_idx
                        
                        if best_chest_for_weapon != -1:
                            # ✨ opened_count を next_state に渡す
                            next_candidates.append(self.next_state(
                                h, c, opened_chests, actions, total_overkill, opened_count, weapon_idx, best_chest_for_weapon
                            ))

                # 2. 素手での攻撃
                min_hp = float('inf')
                best_chest_for_bare_hand = -1
                for chest_idx in range(self.n):
                    if not opened_chests[chest_idx] and h[chest_idx] < min_hp:
                        min_hp = h[chest_idx]
                        best_chest_for_bare_hand = chest_idx
                
                if best_chest_for_bare_hand != -1:
                    # ✨ opened_count を next_state に渡す
                    next_candidates.append(self.next_state(
                        h, c, opened_chests, actions, total_overkill, opened_count, -1, best_chest_for_bare_hand
                    ))

            # 評価関数を使ってソートする
            next_candidates.sort(key=self.score_func, reverse=True)
            
            next_beam = []
            seen = set()
            # ✨ opened_count をループで受け取る
            for h, c, opened_chests, actions, total_overkill, opened_count in next_candidates:
                state_tuple = (tuple(h), tuple(c))
                if state_tuple not in seen:
                    # ✨ 6要素のタプルを次のビームに追加
                    next_beam.append((h, c, opened_chests, actions, total_overkill, opened_count))
                    seen.add(state_tuple)
                
                # ✨ opened_count を使って完了チェック
                if opened_count == self.n:
                    if best_solution_actions is None or len(actions) < len(best_solution_actions):
                        best_solution_actions = actions
                
                if len(next_beam) >= BEAM_WIDTH:
                    break
            
            beam = next_beam
            
            if best_solution_actions and t >= len(best_solution_actions):
                break
        
        if best_solution_actions:
            self.actions = best_solution_actions

    # ✨ opened_count を受け取り、更新して返すように修正
    def next_state(self, h, c, opened_chests, actions, total_overkill, opened_count, weapon_idx, chest_idx):
        new_h = h[:]
        new_c = c[:]
        new_actions = actions[:]
        new_total_overkill = total_overkill
        new_opened_count = opened_count # ✨ コピー
        
        if weapon_idx == -1:
            damage = 1
        else:
            damage = self.a[weapon_idx][chest_idx]
            new_c[weapon_idx] -= 1

        hp_before_damage = new_h[chest_idx]
        new_h[chest_idx] -= damage
        new_actions.append((weapon_idx, chest_idx))

        opened_list = list(opened_chests)
        if hp_before_damage > 0 and new_h[chest_idx] <= 0:
            opened_list[chest_idx] = True
            new_total_overkill += -new_h[chest_idx]
            new_opened_count += 1 # ✨ カウンタをインクリメント
        
        # ✨ 6要素のタプルを返す
        return (new_h, new_c, tuple(opened_list), new_actions, new_total_overkill, new_opened_count)

    def output(self):
        if not self.actions:
            print("0")
            return
        print(len(self.actions))
        for w, b in self.actions:
            print(f"{w} {b}")

    def greedy(self): pass
    def next_func(self): pass
    def yaki(self): pass


if "__main__" == __name__:
    N = int(input())
    H = list(map(int, input().split()))
    C = list(map(int, input().split()))
    A = [list(map(int, input().split())) for _ in range(N)]

    solver = Solve(N, H, C, A)
    solver.solve()