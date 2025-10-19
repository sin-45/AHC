class Solve:
    def __init__(self):
        pass

    def solve(self):
        pass
    
    def beam_search(self):
        pass

    def next_func(self):
        pass
    
    def score_func(self):
        pass

    def yaki(self):
        pass

    def output(self):
        pass


if "__main__" == __name__:
    solve = Solve()
    solve.solve()
    s_list = [list(range(10)) for i in range(10)]
    temp = [p[:] for p in s_list]
    for i in temp:
        print(i)