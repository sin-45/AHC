import sys

class AHC_Solver:
    def __init__(self):
        """入力の受け取りや、変数の初期化など"""
        # --- ここに入力処理 ---
        pass

    def solve(self):
        """メインの処理"""
        # パラメータ設定
        beam_width = 50
        max_turn = 100
        
        # 初期状態の作成
        initial_state = 0 # 例

        # ビームサーチを実行
        best_solution = self.beam_search(initial_state, beam_width, max_turn)
        
        # 結果を出力
        self.output(best_solution)

    def beam_search(self, initial_state, beam_width, max_turn):
        """ビームサーチ本体"""
        # (シーケンス, スコア) を管理
        beam = [([initial_state], 0.0)] 

        for _ in range(max_turn):
            candidates = []
            for seq, score in beam:
                # 現在の状態から次の状態候補をすべて取得
                next_states = self.get_next_states(seq[-1])
                
                for state in next_states:
                    new_seq = seq + [state]
                    new_score = self.score_func(new_seq)
                    candidates.append((new_seq, new_score))
            
            if not candidates:
                break
            
            # スコア順にソートして、上位を次のビームにする
            candidates.sort(key=lambda x: x[1], reverse=True)
            beam = candidates[:beam_width]

        # 最終的に一番スコアが良かったものを返す
        return beam[0][0]

    def get_next_states(self, current_state):
        """現在の状態から次の状態の候補リストを返す"""
        # --- ここに次の手を生成するロジックを記述 ---
        return [current_state + 1, current_state + 2] # 例

    def score_func(self, sequence):
        """スコアを計算する"""
        # --- ここにスコア評価関数を記述 ---
        return float(sum(sequence)) # 例

    def output(self, solution):
        """解を出力する"""
        # --- ここに出力処理を記述 ---
        print(" ".join(map(str, solution)))


# --- メイン処理 ---
if __name__ == "__main__":
    solver = AHC_Solver()
    solver.solve()