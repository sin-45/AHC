from random import randint, shuffle
import time

class Solve:
    def __init__(self, N, H, C, A, start):
        self.n = N
        self.initial_h = H[:]
        self.initial_c = C[:]
        self.a = A
        self.now_score = 1_000_000
        self.actions = []
        self.order_list = list(range(self.n))
        self.best_list = self.order_list[:]
        self.start = start
        self.end = 2

    def solve(self):
        t = self.greedy()
        self.yaki()
        self.output()
    
    def greedy(self):
        """
        シンプルな貪欲法。
        「今できる最もダメージの大きい攻撃」を繰り返す。
        """
        # 現在のゲーム状態をコピーして保持
        h = self.initial_h[:]
        # buki = dict()
        buki = [-1 for i in range(self.n)] # Ci 耐久値  (武器番号はindexで管理)
        self.act = []
        for i in self.order_list:
            while True:
                max_damage = 0 # damage
                max_num = -1
                for j in range(self.n):
                    if buki[j] > 0:
                        # print(max_damage < self.a[j][i], max_damage, self.a[j][i])
                        if max_damage < self.a[j][i]:
                            max_damage = self.a[j][i]
                            max_num = j

                if max_num != -1:
                    buki[max_num] -= 1
                    # print("YYY")

                else:
                    max_damage = 1

                h[i] -= max_damage
                self.act.append((max_num, i))
                if h[i] <= 0:
                    buki[i] = self.initial_c[i]
                    break

    def beam_search(self):
        pass

    def next_func(self):
        pass
    
    def score_func(self):
        pass

    def yaki(self):
        self.f = 0
        while time.time() - self.start < self.end:
            self.f += 1
            p, q = randint(0, 199), randint(0, 199)
            if p == q:
                continue
            self.order_list[p], self.order_list[q] = self.order_list[q], self.order_list[p]
            self.greedy()
            if len(self.act) < self.now_score:
                self.actions = self.act[:]
                self.best_list = self.order_list[:]

    def output(self):
        print(self.f, len(self.actions))
        print(self.best_list)
        cnt = 0
        for w, b in self.actions:
            if b == 0: cnt += 1
            print(f"{w} {b}") # , cnt)


if __name__ == "__main__":
    try:
        with open('input.txt', 'r', encoding="utf-8") as f:
            N = int(f.readline())
            H = list(map(int, f.readline().split()))
            C = list(map(int, f.readline().split()))
            A = [list(map(int, f.readline().split())) for _ in range(N)]
    
    except FileNotFoundError:
        N = int(input())
        H = list(map(int, input().split()))
        C = list(map(int, input().split()))
        A = [list(map(int, input().split())) for _ in range(N)]
    
    start = time.time()
    solver = Solve(N, H, C, A, start)
    solver.solve()