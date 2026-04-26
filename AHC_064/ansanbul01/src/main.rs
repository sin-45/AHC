use std::io::{self, Read};
use std::time::Instant;

const R: usize = 10;
const TIME_LIMIT_MS: u128 = 1950; // 1.8秒

#[derive(Clone, Copy, Debug)]
struct Move {
    m_type: i32,
    i: usize,
    j: usize,
    k: usize,
}

fn run_simulation(initial_d: &Vec<Vec<i32>>, p: &[usize]) -> Vec<Vec<Move>> {
    let mut d = initial_d.clone();
    let mut s: Vec<Vec<i32>> = vec![vec![]; R];
    let mut seq_moves = Vec::new();

    // 1. 初期分配 (p に基づく)
    for i in 0..R {
        let k = 10;
        let start = d[i].len() - k;
        let mut cars: Vec<i32> = d[i].drain(start..).collect();
        // S[j] の先頭に連結
        cars.extend(&s[p[i]]);
        s[p[i]] = cars;
        seq_moves.push(Move { m_type: 0, i, j: p[i], k });
    }

    // 2. 前半戦 (0〜4)
    let buffers_avail = [5, 6, 7, 8, 9];
    let mut needed = [0; 5];
    for t in 0..5 { needed[t] = t as i32 * 10; }

    while needed.iter().enumerate().any(|(t, &n)| n < (t as i32 * 10 + 10)) {
        let mut candidates = Vec::new();
        for t in 0..5 {
            let target = needed[t];
            if target >= (t as i32 * 10 + 10) { continue; }
            'find_car: for j in 0..R {
                if let Some(pos) = s[j].iter().position(|&x| x == target) {
                    candidates.push((pos, j, t));
                    break 'find_car;
                }
            }
        }
        
        candidates.sort_by_key(|x| x.0);
        let mut selected = Vec::new();
        let mut used_j = [false; R];
        let mut used_t = [false; 5];
        
        for &(depth, j, t) in &candidates {
            if !used_j[j] && !used_t[t] {
                selected.push((depth, j, t));
                used_j[j] = true;
                used_t[t] = true;
            }
        }
        if selected.is_empty() { break; }
        selected.sort_by_key(|x| x.1);

        let mut plan_evacuate = Vec::new();
        for (idx, &(depth, j, _t)) in selected.iter().enumerate() {
            let b = buffers_avail[idx];
            if depth > 0 {
                let cars: Vec<i32> = s[j].drain(0..depth).collect();
                d[b].extend(cars);
                seq_moves.push(Move { m_type: 1, i: b, j, k: depth });
                plan_evacuate.push((b, j, depth));
            }
        }
        for &(_depth, j, t) in &selected {
            let car = s[j].remove(0);
            d[t].push(car);
            seq_moves.push(Move { m_type: 1, i: t, j, k: 1 });
            needed[t] += 1;
        }
        for &(b, j, depth) in plan_evacuate.iter().rev() {
            let start = d[b].len() - depth;
            let mut cars: Vec<i32> = d[b].drain(start..).collect();
            cars.extend(&s[j]);
            s[j] = cars;
            seq_moves.push(Move { m_type: 0, i: b, j, k: depth });
        }
    }

    // 3. 後半戦 (5〜9)
    let buffers_avail_2 = [0, 1, 2, 3, 4];
    let mut needed_2 = [0; 10];
    for t in 5..10 { needed_2[t] = t as i32 * 10; }

    while (5..10).any(|t| needed_2[t] < (t as i32 * 10 + 10)) {
        let mut candidates = Vec::new();
        for t in 5..10 {
            let target = needed_2[t];
            if target >= (t as i32 * 10 + 10) { continue; }
            'find_car: for j in 0..R {
                if let Some(pos) = s[j].iter().position(|&x| x == target) {
                    candidates.push((pos, j, t));
                    break 'find_car;
                }
            }
        }
        candidates.sort_by_key(|x| x.0);
        let mut selected = Vec::new();
        let mut used_j = [false; R];
        let mut used_t = [false; 10];
        for &(depth, j, t) in &candidates {
            if !used_j[j] && !used_t[t] && depth <= 5 {
                selected.push((depth, j, t));
                used_j[j] = true;
                used_t[t] = true;
            }
        }
        if selected.is_empty() && !candidates.is_empty() {
            selected.push(candidates[0]);
        }
        if selected.is_empty() { break; }
        selected.sort_by_key(|x| x.1);

        let mut plan_evacuate = Vec::new();
        for (idx, &(depth, j, _t)) in selected.iter().enumerate() {
            if idx < 5 {
                let b = buffers_avail_2[idx];
                let space = 15 - d[b].len();
                let take = depth.min(space);
                if take > 0 {
                    let cars: Vec<i32> = s[j].drain(0..take).collect();
                    d[b].extend(cars);
                    seq_moves.push(Move { m_type: 1, i: b, j, k: take });
                    plan_evacuate.push((b, j, take));
                }
            }
        }
        for &(_depth, j, t) in &selected {
            let car = s[j].remove(0);
            d[t].push(car);
            seq_moves.push(Move { m_type: 1, i: t, j, k: 1 });
            needed_2[t] += 1;
        }
        for &(b, j, take) in plan_evacuate.iter().rev() {
            let start = d[b].len() - take;
            let mut cars: Vec<i32> = d[b].drain(start..).collect();
            cars.extend(&s[j]);
            s[j] = cars;
            seq_moves.push(Move { m_type: 0, i: b, j, k: take });
        }
    }

    // 4. 圧縮器
    let mut compressed = Vec::new();
    let mut curr_turn: Vec<Move> = Vec::new();
    let mut u_d = [false; R];
    let mut u_s = [false; R];

    for m in seq_moves {
        let mut conflict = u_d[m.i] || u_s[m.j];
        if !conflict {
            for tm in &curr_turn {
                if (m.i < tm.i && m.j > tm.j) || (m.i > tm.i && m.j < tm.j) {
                    conflict = true;
                    break;
                }
            }
        }
        if conflict {
            compressed.push(curr_turn);
            curr_turn = vec![m];
            u_d = [false; R]; u_s = [false; R];
            u_d[m.i] = true; u_s[m.j] = true;
        } else {
            u_d[m.i] = true; u_s[m.j] = true;
            curr_turn.push(m);
        }
    }
    if !curr_turn.is_empty() { compressed.push(curr_turn); }
    compressed
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut words = input.split_whitespace();
    
    let r_val: usize = words.next().unwrap().parse().unwrap();
    let mut initial_d = vec![vec![]; r_val];
    for i in 0..r_val {
        for _ in 0..10 {
            initial_d[i].push(words.next().unwrap().parse().unwrap());
        }
    }

    let start_instant = Instant::now();
    let mut best_res = Vec::new();
    let mut min_turns = usize::MAX;

    // 戦略1: Identity
    let mut p: Vec<usize> = (0..R).collect();
    let res = run_simulation(&initial_d, &p);
    if res.len() < min_turns {
        min_turns = res.len();
        best_res = res;
    }

    // 擬似乱数用
    let mut seed = 123456789u64;
    let mut xorshift = || {
        seed ^= seed << 13;
        seed ^= seed >> 7;
        seed ^= seed << 17;
        seed
    };

    // 時間いっぱい試行
    while start_instant.elapsed().as_millis() < TIME_LIMIT_MS {
        // フィッシャー–イェーツのシャッフル
        for i in (1..R).rev() {
            let j = (xorshift() % (i as u64 + 1)) as usize;
            p.swap(i, j);
        }
        
        let res = run_simulation(&initial_d, &p);
        if !res.is_empty() && res.len() < min_turns {
            min_turns = res.len();
            best_res = res;
        }
    }

    // 出力
    println!("{}", best_res.len());
    for turn in best_res {
        println!("{}", turn.len());
        for m in turn {
            println!("{} {} {} {}", m.m_type, m.i, m.j, m.k);
        }
    }
}