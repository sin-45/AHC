import sys
import heapq

class Solve:
    def __init__(self, N, H, C, A):
        self.n = N
        self.initial_h = H[:]
        self.initial_c = C[:]
        # ✨ 総ダメージ量の計算を簡単にするため、初期HPの合計を保持
        self.total_initial_h = sum(self.initial_h)
        self.a = A
        self.actions = []

    def solve(self):
        self.beam_search()
        self.output()

    # ✨ 新しい評価関数
    def score_func(self, state):
        """
        状態を評価してスコアを返す。スコアが高いほど良い状態。
        評価要素：開けた宝箱の数、総ダメージ量、超過ダメージ
        """
        h, c, opened_chests, actions, total_overkill = state
        
        # --- パラメータ（重み）---
        SCORE_PER_CHEST = 100_000
        TOTAL_DAMAGE_WEIGHT = 10
        OVERKILL_PENALTY = 30
        
        # 1. 開けた宝箱の数に基づくスコア
        score = sum(opened_chests) * SCORE_PER_CHEST
        
        # 2. 与えた総ダメージ量に基づくスコア
        current_hp_sum = sum(hp for hp in h if hp > 0)
        total_damage_dealt = self.total_initial_h - current_hp_sum
        score += total_damage_dealt * TOTAL_DAMAGE_WEIGHT
        
        # 3. 超過ダメージ（オーバーキル）に基づくペナルティ
        score -= (total_overkill-1000) * OVERKILL_PENALTY
        
        return score

    def beam_search(self):
        BEAM_WIDTH = 10

        # ✨ 状態に `total_overkill` (超過ダメージ合計) を追加
        initial_state = (
            self.initial_h[:],
            self.initial_c[:],
            [False] * self.n,
            [],
            0,  # 初期超過ダメージは0
        )
        
        beam = [initial_state]
        best_solution_actions = None

        max_turns = sum(self.initial_h)

        for t in range(max_turns):
            if not beam:
                break

            next_candidates = []
            
            # ✨ total_overkill をループで受け取る
            for h, c, opened_chests, actions, total_overkill in beam:
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
                            # ✨ total_overkill を next_state に渡す
                            next_candidates.append(self.next_state(
                                h, c, opened_chests, actions, total_overkill, weapon_idx, best_chest_for_weapon
                            ))

                # 2. 素手での攻撃
                min_hp = float('inf')
                best_chest_for_bare_hand = -1
                for chest_idx in range(self.n):
                    if not opened_chests[chest_idx] and h[chest_idx] < min_hp:
                        min_hp = h[chest_idx]
                        best_chest_for_bare_hand = chest_idx
                
                if best_chest_for_bare_hand != -1:
                    # ✨ total_overkill を next_state に渡す
                    next_candidates.append(self.next_state(
                        h, c, opened_chests, actions, total_overkill, -1, best_chest_for_bare_hand
                    ))

            # ✨ 評価関数を使ってソートする
            next_candidates.sort(key=self.score_func, reverse=True)
            
            next_beam = []
            seen = set()
            # ✨ total_overkill をループで受け取る
            for h, c, opened_chests, actions, total_overkill in next_candidates:
                state_tuple = (tuple(h), tuple(c))
                if state_tuple not in seen:
                    # ✨ 5要素のタプルを次のビームに追加
                    next_beam.append((h, c, opened_chests, actions, total_overkill))
                    seen.add(state_tuple)
                
                if sum(opened_chests) == self.n:
                    if best_solution_actions is None or len(actions) < len(best_solution_actions):
                        best_solution_actions = actions
                
                if len(next_beam) >= BEAM_WIDTH:
                    break
            
            beam = next_beam
            
            if best_solution_actions and t >= len(best_solution_actions):
                break
        
        if best_solution_actions:
            self.actions = best_solution_actions

        # print("->", total_overkill)

    # ✨ 超過ダメージを計算・管理するように修正
    def next_state(self, h, c, opened_chests, actions, total_overkill, weapon_idx, chest_idx):
        new_h = h[:]
        new_c = c[:]
        new_actions = actions[:]
        new_total_overkill = total_overkill
        
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
            # ✨ 超過ダメージを計算して加算
            new_total_overkill += -new_h[chest_idx]
        
        # ✨ 5要素のタプルを返す
        return (new_h, new_c, tuple(opened_list), new_actions, new_total_overkill)

    def output(self):
        if not self.actions:
            print("0")
            return
        # print(len(self.actions))
        for w, b in self.actions:
            print(f"{w} {b}")

    def greedy(self): pass
    def next_func(self): pass
    # score_funcは上で定義済みのため、passのままにしておく
    def yaki(self): pass


if "__main__" == __name__:
    N = int(input())
    H = list(map(int, input().split()))
    C = list(map(int, input().split()))
    A = [list(map(int, input().split())) for _ in range(N)]

    solver = Solve(N, H, C, A)
    solver.solve()