import sys
import heapq

class Solve:
    def __init__(self, N, H, C, A):
        self.n = N
        self.initial_h = H[:]
        self.initial_c = C[:]
        self.a = A
        self.actions = []

    def solve(self):
        self.beam_search()
        self.output()

    def beam_search(self):
        BEAM_WIDTH = 5

        initial_state = (
            self.initial_h[:],
            self.initial_c[:],
            [False] * self.n,
            []
        )
        
        beam = [initial_state]
        best_solution_actions = None

        max_turns = sum(self.initial_h)

        for t in range(max_turns):
            if not beam:
                break

            next_candidates = []
            
            for h, c, opened_chests, actions in beam:
                # --- ここからが改善ロジック ---

                # 1. 各武器について、最もダメージ効率の良い攻撃を1つだけ候補に入れる
                for weapon_idx in range(self.n):
                    if opened_chests[weapon_idx] and c[weapon_idx] > 0:
                        best_chest_for_weapon = -1
                        max_damage = 0
                        # この武器で最もダメージを与えられる宝箱を探す
                        for chest_idx in range(self.n):
                            if not opened_chests[chest_idx]:
                                if self.a[weapon_idx][chest_idx] > max_damage:
                                    max_damage = self.a[weapon_idx][chest_idx]
                                    best_chest_for_weapon = chest_idx
                        
                        # 最適な攻撃対象が見つかったら候補に追加
                        if best_chest_for_weapon != -1:
                            next_candidates.append(self.next_state
                    (
                                h, c, opened_chests, actions, weapon_idx, best_chest_for_weapon
                            ))

                # 2. 素手での攻撃候補を追加 (最もHPが低い宝箱を狙う)
                min_hp = float('inf')
                best_chest_for_bare_hand = -1
                for chest_idx in range(self.n):
                    if not opened_chests[chest_idx] and h[chest_idx] < min_hp:
                        min_hp = h[chest_idx]
                        best_chest_for_bare_hand = chest_idx
                
                if best_chest_for_bare_hand != -1:
                    next_candidates.append(self.next_state
            (
                        h, c, opened_chests, actions, -1, best_chest_for_bare_hand
                    ))

            # --- 改善ロジックはここまで ---

            # はるかに小さくなった候補リストをソートする
            next_candidates.sort(key=lambda state: (sum(state[2]), -len(state[3])), reverse=True)
            
            next_beam = []
            seen = set()
            for h, c, opened_chests, actions in next_candidates:
                state_tuple = (tuple(h), tuple(c))
                if state_tuple not in seen:
                    next_beam.append((h, c, opened_chests, actions))
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

    def next_state(self, h, c, opened_chests, actions, weapon_idx, chest_idx):
        new_h = h[:]
        new_c = c[:]
        new_actions = actions[:]
        
        if weapon_idx == -1:
            damage = 1
        else:
            damage = self.a[weapon_idx][chest_idx]
            new_c[weapon_idx] -= 1

        new_h[chest_idx] -= damage
        new_actions.append((weapon_idx, chest_idx))

        opened_list = list(opened_chests)
        if new_h[chest_idx] <= 0 and not opened_list[chest_idx]:
            opened_list[chest_idx] = True
        
        return (new_h, new_c, tuple(opened_list), new_actions)


    def output(self):
        if not self.actions:
            print("0")
            return
        # print(len(self.actions))
        for w, b in self.actions:
            print(f"{w} {b}")

    def greedy(self): pass
    def next_func(self): pass
    def score_func(self): pass
    def yaki(self): pass


if "__main__" == __name__:
    N = int(input())
    H = list(map(int, input().split()))
    C = list(map(int, input().split()))
    A = [list(map(int, input().split())) for _ in range(N)]

    solver = Solve(N, H, C, A)
    solver.solve()