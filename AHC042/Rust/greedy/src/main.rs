use std::io::{self, BufRead};

/// ビームサーチで管理する各状態を表す構造体
/// Pythonコードの [盤面, スコア, コマンドリスト] に相当します
#[derive(Clone)]
struct State {
    board: Vec<Vec<char>>,
    score: i32,
    commands: Vec<(char, usize)>,
}

/// 問題解決のロジック全体を管理する構造体
/// Pythonの Solve クラスに相当します
struct Solver {
    n: usize,
    initial_board: Vec<Vec<char>>,
    oni_cnt: i32,
    beam_width: usize,
}

impl Solver {
    /// コンストラクタ (Pythonの __init__ に相当)
    fn new(n: usize, initial_board: Vec<Vec<char>>) -> Self {
        Self {
            n,
            initial_board,
            oni_cnt: 10,
            beam_width: 100,
        }
    }

    /// 問題を解くメインの関数 (Pythonの solve に相当)
    /// 最終的に最善と判断されたコマンドリストを返します
    fn solve(&self) -> Vec<(char, usize)> {
        self.beam_search()
    }

    /// ビームサーチ本体
    fn beam_search(&self) -> Vec<(char, usize)> {
        let initial_score = self.score_func(&self.initial_board);
        let initial_state = State {
            board: self.initial_board.clone(),
            score: initial_score,
            commands: Vec::new(),
        };

        // ビームを初期状態から開始
        let mut beam = vec![initial_state];

        for _ in 0..120 {
            let (next_beam, end) = self.generate_next_states(&beam);
            beam = next_beam;

            // 探索する候補がなくなったり、スコアが0になったら終了
            if end || beam.is_empty() {
                break;
            }
        }

        // 最終的に最もスコアが良かった（低かった）解のコマンドを返す
        if beam.is_empty() {
            Vec::new()
        } else {
            beam[0].commands.clone()
        }
    }

    /// 現在のビームから次のターンの候補を生成する (Pythonの next_func に相当)
    fn generate_next_states(&self, current_beam: &[State]) -> (Vec<State>, bool) {
        let mut next_candidates = Vec::new();

        for state in current_beam {
            let s_list = &state.board;
            let com_list = &state.commands;
            
            // Pythonコードの `range(20)` に合わせてサイズを20で固定
            let board_size = 20;

            for i in 0..board_size {
                // 左シフト (L)
                if s_list[i][0] != 'o' {
                    let mut temp_list = s_list.clone();
                    for j in 0..board_size - 1 {
                        temp_list[i][j] = s_list[i][j + 1];
                    }
                    temp_list[i][board_size - 1] = '.';
                    let mut new_com = com_list.clone();
                    new_com.push(('L', i));
                    next_candidates.push(State { score: self.score_func(&temp_list), board: temp_list, commands: new_com });
                }

                // 右シフト (R)
                if s_list[i][board_size - 1] != 'o' {
                    let mut temp_list = s_list.clone();
                    for j in (1..board_size).rev() {
                        temp_list[i][j] = s_list[i][j - 1];
                    }
                    temp_list[i][0] = '.';
                    let mut new_com = com_list.clone();
                    new_com.push(('R', i));
                    next_candidates.push(State { score: self.score_func(&temp_list), board: temp_list, commands: new_com });
                }

                // 上シフト (U)
                if s_list[0][i] != 'o' {
                    let mut temp_list = s_list.clone();
                    for j in 0..board_size - 1 {
                        temp_list[j][i] = s_list[j + 1][i];
                    }
                    temp_list[board_size - 1][i] = '.';
                    let mut new_com = com_list.clone();
                    new_com.push(('U', i));
                    next_candidates.push(State { score: self.score_func(&temp_list), board: temp_list, commands: new_com });
                }

                // 下シフト (D)
                if s_list[board_size - 1][i] != 'o' {
                    let mut temp_list = s_list.clone();
                    for j in (1..board_size).rev() {
                        temp_list[j][i] = s_list[j - 1][i];
                    }
                    temp_list[0][i] = '.';
                    let mut new_com = com_list.clone();
                    new_com.push(('D', i));
                    next_candidates.push(State { score: self.score_func(&temp_list), board: temp_list, commands: new_com });
                }
            }
        }
        
        // スコアが低い順にソート (昇順)
        next_candidates.sort_unstable_by_key(|s| s.score);
        // ビーム幅に候補を絞る
        next_candidates.truncate(self.beam_width);

        // 終了条件の判定
        let end = next_candidates.is_empty() || next_candidates[0].score == 0;
        
        (next_candidates, end)
    }

    /// 盤面のスコアを計算する (Pythonの score_func に相当)
    fn score_func(&self, board: &Vec<Vec<char>>) -> i32 {
        let mut cnt = 0;
        for i in 0..self.n {
            for j in 0..self.n {
                if board[i][j] == 'x' {
                    // Pythonコードのロジックをそのまま移植
                    let temp_i = if i < 10 { i + 1 } else { 20 - i };
                    let temp_j = if j < 10 { j + 1 } else { 20 - j };
                    let temp = std::cmp::min(temp_i, temp_j);
                    cnt += temp as i32 + self.oni_cnt;
                }
            }
        }
        cnt
    }
}

/// メイン関数 (Pythonの if __name__ == "__main__": に相当)
fn main() {
    // 標準入力からデータを読み込む
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();

    let n: usize = lines.next().unwrap().unwrap().parse().unwrap();
    let mut inp_list = Vec::with_capacity(n);
    for _ in 0..n {
        let line = lines.next().unwrap().unwrap();
        inp_list.push(line.chars().collect());
    }
    
    // Solverを初期化
    let solver = Solver::new(n, inp_list);
    // 解法を実行して最良のコマンドリストを取得
    let best_commands = solver.solve();
    
    // 結果を出力 (Pythonの output に相当)
    for (dir, index) in &best_commands {
        println!("{} {}", dir, index);
    }
    // Pythonコードにはありませんでしたが、手数を表示する部分も再現
    // println!("{}", best_commands.len());
}