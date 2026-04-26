use std::io::{self, Read};
use std::time::Instant;

const R: usize = 10;
const TIME_LIMIT_MS: f64 = 1990.0;

#[derive(Clone, Copy, Debug)]
struct Move {
    m_type: i32, // 0: Track->Siding, 1: Siding->Track
    i: usize,    // Track index
    j: usize,    // Siding index
    k: usize,    // Num cars
}

// 評価用: (ターン数, 内部コスト, 操作列)
fn run_simulation_with_cost(initial_d: &Vec<Vec<i32>>, p: &[usize]) -> (usize, i32, Vec<Vec<Move>>) {
    let mut d = initial_d.clone();
    let mut s: Vec<Vec<i32>> = vec![vec![]; R];
    let mut seq_moves = Vec::new();
    let mut needed = [0; R];
    let mut internal_cost = 0;

    // --- 1. 初期化: 先頭から正しい順序で並んでいる車両を特定し、動かさない ---
    for i in 0..R {
        let base_id = i as i32 * 10;
        let mut keep_count = 0;
        // 出発線の先頭（インデックス0）からチェック
        while keep_count < d[i].len() && d[i][keep_count] == base_id + keep_count as i32 {
            keep_count += 1;
        }
        // 次に必要なIDをセット
        needed[i] = base_id + keep_count as i32;
        
        // 正しくない残りの車両（末尾側）だけを待避線へ送る
        let to_move = 10 - keep_count;
        if to_move > 0 {
            let start_idx = d[i].len() - to_move;
            let mut cars: Vec<i32> = d[i].drain(start_idx..).collect();
            // 待避線の先頭へ連結 (LIFO)
            cars.extend(&s[p[i]]);
            s[p[i]] = cars;
            seq_moves.push(Move { m_type: 0, i, j: p[i], k: to_move });
        }
    }

    // ソート実行用クロージャ
    let mut solve_phase = |target_range: std::ops::Range<usize>, buffers: &[usize]| {
        while target_range.clone().any(|t| needed[t] < (t as i32 * 10 + 10)) {
            let mut candidates = Vec::new();
            for t in target_range.clone() {
                if needed[t] >= (t as i32 * 10 + 10) { continue; }
                for j in 0..R {
                    if let Some(pos) = s[j].iter().position(|&x| x == needed[t]) {
                        // タイブレーク: 距離が近いものを優先
                        let dist = (j as i32 - t as i32).abs();
                        candidates.push((pos, j, t, dist));
                        break;
                    }
                }
            }
            
            // 内部コストの加算（ターゲットが深いほど悪い）
            for cand in &candidates { internal_cost += cand.0 as i32; }

            // 深さ優先、次に物理的距離
            candidates.sort_by_key(|x| (x.0, x.3));
            let mut selected = Vec::new();
            let mut used_j = [false; R];
            let mut used_t = [false; 10];
            
            for &(depth, j, t, _) in &candidates {
                // 後半戦の容量制限考慮（バッファは5両まで）
                if target_range.start >= 5 && depth > 5 { continue; }
                if !used_j[j] && !used_t[t] {
                    selected.push((depth, j, t));
                    used_j[j] = true;
                    used_t[t] = true;
                }
            }
            
            if selected.is_empty() && !candidates.is_empty() {
                selected.push((candidates[0].0, candidates[0].1, candidates[0].2));
            }
            if selected.is_empty() { break; }
            selected.sort_by_key(|x| x.1); // 交差防止のためSiding番号でソート

            let mut plan_evac = Vec::new();
            for (idx, &(depth, j, _)) in selected.iter().enumerate() {
                if idx >= buffers.len() { break; }
                let b = buffers[idx];
                let take = depth.min(15 - d[b].len());
                if take > 0 {
                    let cars: Vec<i32> = s[j].drain(0..take).collect();
                    d[b].extend(cars);
                    seq_moves.push(Move { m_type: 1, i: b, j, k: take });
                    plan_evac.push((b, j, take));
                }
            }
            for &(_, j, t) in &selected {
                let car = s[j].remove(0);
                d[t].push(car);
                seq_moves.push(Move { m_type: 1, i: t, j, k: 1 });
                needed[t] += 1;
            }
            for &(b, j, depth) in plan_evac.iter().rev() {
                let start = d[b].len() - depth;
                let mut cars: Vec<i32> = d[b].drain(start..).collect();
                cars.extend(&s[j]);
                s[j] = cars;
                seq_moves.push(Move { m_type: 0, i: b, j, k: depth });
            }
        }
    };

    // 2. 前半戦 (0-4) と 3. 後半戦 (5-9)
    solve_phase(0..5, &[5, 6, 7, 8, 9]);
    solve_phase(5..10, &[0, 1, 2, 3, 4]);

    // 4. 圧縮器
    let mut compressed = Vec::new();
    let mut curr_turn: Vec<Move> = Vec::new();
    let mut u_d = [false; R]; let mut u_s = [false; R];
    for m in seq_moves {
        let mut conflict = u_d[m.i] || u_s[m.j];
        if !conflict {
            for tm in &curr_turn {
                if (m.i < tm.i && m.j > tm.j) || (m.i > tm.i && m.j < tm.j) {
                    conflict = true; break;
                }
            }
        }
        if conflict {
            compressed.push(curr_turn);
            curr_turn = vec![m]; u_d = [false; R]; u_s = [false; R];
            u_d[m.i] = true; u_s[m.j] = true;
        } else {
            u_d[m.i] = true; u_s[m.j] = true; curr_turn.push(m);
        }
    }
    if !curr_turn.is_empty() { compressed.push(curr_turn); }
    (compressed.len(), internal_cost, compressed)
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut words = input.split_whitespace();
    words.next(); // R=10
    let mut initial_d = vec![vec![]; R];
    for i in 0..R {
        for _ in 0..10 { initial_d[i].push(words.next().unwrap().parse().unwrap()); }
    }

    let start_instant = Instant::now();
    let mut seed = 5555u64;
    let mut xorshift = || { seed ^= seed << 13; seed ^= seed >> 7; seed ^= seed << 17; seed };

    let mut current_p: Vec<usize> = (0..R).collect();
    let (mut current_turns, mut current_icost, mut current_res) = run_simulation_with_cost(&initial_d, &current_p);
    
    let mut best_res = current_res.clone();
    let mut min_turns = current_turns;

    // 焼きなましパラメータ
    let t_start: f64 = 300.0; // ソフトコスト導入により高めに設定
    let t_end: f64 = 0.1;

    let mut iter_count = 0;
    while start_instant.elapsed().as_millis() < 1850 {
        let elapsed_ratio = start_instant.elapsed().as_millis() as f64 / 1850.0;
        let temp = t_start * (t_end / t_start).powf(elapsed_ratio);
        
        let old_p = current_p.clone();
        let i = (xorshift() % R as u64) as usize;
        let j = (xorshift() % R as u64) as usize;
        
        // 近傍: 80% Swap, 20% Insert
        if (xorshift() % 100) < 20 {
            let val = current_p.remove(i); current_p.insert(j, val);
        } else {
            current_p.swap(i, j);
        }

        let (next_turns, next_icost, next_res) = run_simulation_with_cost(&initial_d, &current_p);
        
        // エネルギー = ターン数 * 100 + 内部的な深さコスト
        let current_energy = (current_turns * 100) as i32 + current_icost;
        let next_energy = (next_turns * 100) as i32 + next_icost;
        let diff = (current_energy - next_energy) as f64;

        // 焼きなまし受理判定
        if diff >= 0.0 || (xorshift() as f64 / u64::MAX as f64) < (diff / temp).exp() {
            current_turns = next_turns;
            current_icost = next_icost;
            if current_turns < min_turns {
                min_turns = current_turns;
                best_res = next_res;
            }
        } else {
            current_p = old_p;
        }
        iter_count += 1;
    }

    // 結果出力
    println!("{}", best_res.len());
    for turn in best_res {
        println!("{}", turn.len());
        for m in turn { println!("{} {} {} {}", m.m_type, m.i, m.j, m.k); }
    }
}