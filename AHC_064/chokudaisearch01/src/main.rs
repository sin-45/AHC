use std::cmp::Ordering;
use std::collections::BinaryHeap;
use std::io::{self, Read};
use std::time::Instant;

const R: usize = 10;
const TIME_LIMIT_MS: u128 = 1850;
const MAX_CARS: usize = 100;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Move {
    m_type: i32,
    i: usize,
    j: usize,
    k: usize,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct State {
    score: i32,
    needed: [i32; R],
    tracks: Vec<Vec<i32>>,
    sidings: Vec<Vec<i32>>,
    history: Vec<Move>,
    total_completed: usize,
}

impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        other.score.cmp(&self.score)
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

fn get_heuristic(needed: &[i32; R], sidings: &Vec<Vec<i32>>, history_len: usize) -> i32 {
    let mut depth_sum = 0;
    let mut combo_bonus = 0;
    for i in 0..R {
        let target = needed[i];
        if target < (i as i32 * 10 + 10) {
            for j in 0..R {
                if let Some(pos) = sidings[j].iter().position(|&x| x == target) {
                    depth_sum += pos as i32;
                    if pos + 1 < sidings[j].len() && sidings[j][pos + 1] == target + 1 {
                        combo_bonus += 50;
                    }
                    break;
                }
            }
        }
    }
    (history_len as i32 * 50) + (depth_sum * 10) - combo_bonus
}

fn solve() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut words = input.split_whitespace();
    if words.next().is_none() { return; }

    let mut initial_tracks = vec![vec![]; R];
    for i in 0..R {
        for _ in 0..10 {
            initial_tracks[i].push(words.next().unwrap().parse().unwrap());
        }
    }

    let start_time = Instant::now();
    let mut queues: Vec<BinaryHeap<State>> = vec![BinaryHeap::new(); MAX_CARS + 1];

    let mut s0 = vec![vec![]; R];
    let mut t0 = initial_tracks.clone();
    let mut h0 = Vec::new();
    let mut n0 = [0; R];

    for i in 0..R {
        let base = i as i32 * 10;
        let mut keep = 0;
        while keep < t0[i].len() && t0[i][keep] == base + keep as i32 {
            keep += 1;
        }
        n0[i] = base + keep as i32;
        let to_move = 10 - keep;
        if to_move > 0 {
            let start = t0[i].len() - to_move;
            let cars: Vec<i32> = t0[i].drain(start..).collect();
            s0[i] = cars;
            h0.push(Move { m_type: 0, i, j: i, k: to_move });
        }
    }

    let initial_completed: usize = n0.iter().enumerate().map(|(i, &v)| (v as usize - i * 10)).sum();
    queues[initial_completed].push(State {
        score: get_heuristic(&n0, &s0, h0.len()),
        needed: n0,
        tracks: t0,
        sidings: s0,
        history: h0,
        total_completed: initial_completed,
    });

    let mut best_state: Option<State> = None;

    while start_time.elapsed().as_millis() < TIME_LIMIT_MS {
        for d in 0..MAX_CARS {
            let curr = if let Some(c) = queues[d].pop() { c } else { continue; };

            let mut candidates = Vec::new();
            for t_idx in 0..R {
                let target = curr.needed[t_idx];
                if target < (t_idx as i32 * 10 + 10) {
                    for j in 0..R {
                        if let Some(pos) = curr.sidings[j].iter().position(|&x| x == target) {
                            candidates.push((pos, j, t_idx));
                            break;
                        }
                    }
                }
            }
            candidates.sort_by_key(|x| x.0);

            for count in 1..=2 {
                let mut selected = Vec::new();
                let mut used_j = [false; R];
                let mut used_t = [false; R];
                let mut last_j = -1i32;

                for &(depth, j, t) in &candidates {
                    if !used_j[j] && !used_t[t] && (j as i32) > last_j {
                        if curr.tracks[t].len() + 1 <= 15 {
                            selected.push((depth, j, t));
                            used_j[j] = true;
                            used_t[t] = true;
                            last_j = j as i32;
                        }
                    }
                    if selected.len() == count { break; }
                }

                if selected.is_empty() { continue; }

                let mut next_s = curr.sidings.clone();
                let mut next_t = curr.tracks.clone();
                let mut next_n = curr.needed;
                let mut next_h = curr.history.clone();
                
                let mut can_execute_all = true;

                for (depth, j, t) in &selected {
                    let mut evac_info = None;
                    
                    // 退避
                    if *depth > 0 {
                        let mut buffer_idx = 100;
                        for bi in 0..R {
                            if !used_t[bi] && bi != *t && next_t[bi].len() + depth <= 15 {
                                buffer_idx = bi; break;
                            }
                        }
                        if buffer_idx < R {
                            let evac: Vec<i32> = next_s[*j].drain(0..*depth).collect();
                            next_t[buffer_idx].extend(evac);
                            next_h.push(Move { m_type: 1, i: buffer_idx, j: *j, k: *depth });
                            evac_info = Some((buffer_idx, *depth)); // 【修正箇所】ここで確実な履歴を変数に保存
                        } else {
                            can_execute_all = false;
                            break;
                        }
                    }
                    
                    // ターゲットの移動
                    let car = next_s[*j].remove(0);
                    next_t[*t].push(car);
                    next_h.push(Move { m_type: 1, i: *t, j: *j, k: 1 });
                    next_n[*t] += 1;
                    
                    // 退避の復元
                    if let Some((b_idx, k_evac)) = evac_info {
                        let start = next_t[b_idx].len() - k_evac;
                        let mut cars: Vec<i32> = next_t[b_idx].drain(start..).collect();
                        cars.extend(&next_s[*j]);
                        next_s[*j] = cars;
                        next_h.push(Move { m_type: 0, i: b_idx, j: *j, k: k_evac });
                    }
                }

                if !can_execute_all { continue; } // バッファが足りない場合はその手は無効

                let new_completed: usize = next_n.iter().enumerate().map(|(i, &v)| (v as usize - i * 10)).sum();
                let next_state = State {
                    score: get_heuristic(&next_n, &next_s, next_h.len()),
                    needed: next_n,
                    tracks: next_t,
                    sidings: next_s,
                    history: next_h,
                    total_completed: new_completed,
                };

                if new_completed == MAX_CARS {
                    if best_state.is_none() || next_state.history.len() < best_state.as_ref().unwrap().history.len() {
                        best_state = Some(next_state.clone());
                    }
                }
                queues[new_completed].push(next_state);
            }
        }
    }

    if let Some(final_state) = best_state {
        let compressed = compress_moves(final_state.history);
        println!("{}", compressed.len());
        for turn in compressed {
            println!("{}", turn.len());
            for m in turn {
                println!("{} {} {} {}", m.m_type, m.i, m.j, m.k);
            }
        }
    }
}

fn compress_moves(moves: Vec<Move>) -> Vec<Vec<Move>> {
    let mut compressed = Vec::new();
    let mut curr_turn = Vec::new();
    let mut u_d = [false; R];
    let mut u_s = [false; R];
    for m in moves {
        let intersect = curr_turn.iter().any(|tm: &Move| (m.i < tm.i && m.j > tm.j) || (m.i > tm.i && m.j < tm.j));
        if u_d[m.i] || u_s[m.j] || intersect {
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
    solve();
}