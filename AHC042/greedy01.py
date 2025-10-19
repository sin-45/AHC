class Solve:
    def __init__(self, n, inp_list):
        self.n = n
        self.inp_list = [i[:] for i in inp_list]
        self.oni_cnt = 10 # 鬼を消したボーナス
        self.beam_widht = 100

    def solve(self):
        # print(f"start score: {self.score_func(self.inp_list,log=True)}")
        self.beam_search()
    
    def beam_search(self):
        self.start_map = [[[k[:] for k in self.inp_list], 0, []]]
        for c in range(120):
            self.start_map, end = self.next_func(self.start_map)
            if end: break

    def next_func(self, inp_list):
        next_list = []
        for l in inp_list:
            s_list = l[0]
            com_list = l[2]
            for i in range(20):
                if s_list[i][0] != "o":
                    # print(s_list)
                    temp_list = [p[:] for p in s_list]
                    temp_list[i] = s_list[i][1:] + ["."]
                    next_list.append([
                        temp_list,
                        self.score_func(temp_list),
                        com_list[:] + [("L", i)]
                    ])

                if s_list[i][19] != "o":
                    temp_list = [p[:] for p in s_list]
                    temp_list[i] = ["."] + s_list[i][:-1]
                    next_list.append([
                        temp_list,
                        self.score_func(temp_list),
                        com_list[:] + [("R", i)]
                    ])

                if s_list[0][i] != "o":
                    temp_list = [p[:] for p in s_list]
                    for j in range(self.n-1):
                        temp_list[j][i] = s_list[j+1][i]

                    temp_list[self.n-1][i] = "."
                    next_list.append([
                        temp_list,
                        self.score_func(temp_list),
                        com_list[:] + [("U", i)]
                    ])

                if s_list[19][i] != "o":
                    temp_list = [p[:] for p in s_list]
                    for j in range(self.n-1):
                        temp_list[self.n-1-j][i] = s_list[self.n-2-j][i]

                    temp_list[0][i] = "."
                    next_list.append([
                        temp_list,
                        self.score_func(temp_list),
                        com_list[:] + [("D", i)]
                    ])

        next_list = sorted(next_list, key=lambda x: x[1])[:self.beam_widht]
        # for i in next_list:
        #     print(i[1], i[2])
        end = True if next_list[0][1] == 0 else False
        return next_list, end
        
    def score_func(self, s_list, log=False):
        cnt = 0
        for i in range(self.n):
            for j in range(self.n):
                if s_list[i][j] == "x":
                    if i < 10:
                        temp = i+1
                    else:
                        temp = 20-i

                    if j < 10:
                        temp = min(temp, j+1)
                    else:
                        temp = min(temp, 20-j)

                    if log:
                        print(i, j, temp)
                    cnt += temp + self.oni_cnt

        return cnt
    
    def yaki(self):
        pass

    def output(self):
        # print(self.start_map[0][1])
        for i in self.start_map[0][2]:
            print(*i)

        print(len(self.start_map[0][2]))
        # for i in self.start_map[0][0]:
        #     print("".join(i), end=" ")


if "__main__" == __name__:
    n = int(input())
    inp_list = [list(input()) for _ in range(n)]
    solve = Solve(n, inp_list)
    solve.solve()
    solve.output()
