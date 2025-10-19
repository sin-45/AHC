use std::collections::HashSet;
use std::io::{self, BufRead};

struct Solve {
    n: usize,
    initial_h: Vec<i64>,
    initial_c: Vec<i64>,
    total_initial_h: i64,
    a: Vec<Vec<i64>>,
    actions: Vec<(i32, usize)>,
}

// Pythonのタプルに対応するRustの型エイリアスを定義
type State = (
    Vec<i64>,          // h
    Vec<i64>,          // c
    Vec<bool>,         // opened_chests
    Vec<(i32, usize)>, // actions
    i64,               // total_overkill
    usize,             // opened_count
);

impl Solve {
    fn new(n: usize, h: Vec<i64>, c: Vec<i64>, a: Vec<Vec<i64>>) -> Self {
        let total_initial_h = h.iter().sum();
        Solve {
            n,
            initial_h: h,
            initial_c: c,
            total_initial_h,
            a,
            actions: Vec::new(),
        }
    }

    fn solve(&mut self) {
        self.beam_search();
        self.output();
    }

    // Pythonの評価関数を忠実に再現
    fn score_func(&self, state: &State) -> i64 {
        let (h, _c, _opened_chests, _actions, total_overkill, opened_count) = state;
        
        const SCORE_PER_CHEST: i64 = 100_000;
        const TOTAL_DAMAGE_WEIGHT: i64 = 10;
        const OVERKILL_PENALTY: i64 = 20;

        let score = *opened_count as i64 * SCORE_PER_CHEST;
        
        let current_hp_sum: i64 = h.iter().filter(|&&hp| hp > 0).sum();
        let total_damage_dealt = self.total_initial_h - current_hp_sum;
        
        score + total_damage_dealt * TOTAL_DAMAGE_WEIGHT - (*total_overkill - 1000) * OVERKILL_PENALTY
    }

    fn beam_search(&mut self) {
        const BEAM_WIDTH: usize = 5;

        let initial_state: State = (
            self.initial_h.clone(),
            self.initial_c.clone(),
            vec![false; self.n],
            Vec::new(),
            0, // total_overkill
            0, // opened_count
        );
        
        let mut beam = vec![initial_state];
        let mut best_solution_actions: Option<Vec<(i32, usize)>> = None;
        let max_turns = self.total_initial_h as usize;

        for t in 0..max_turns {
            if beam.is_empty() {
                break;
            }

            let mut next_candidates = Vec::new();
            
            for (h, c, opened_chests, actions, total_overkill, opened_count) in &beam {
                // 1. 武器での攻撃
                for weapon_idx in 0..self.n {
                    if opened_chests[weapon_idx] && c[weapon_idx] > 0 {
                        let mut best_chest_for_weapon = -1;
                        let mut max_damage = 0;
                        for chest_idx in 0..self.n {
                            if !opened_chests[chest_idx] && self.a[weapon_idx][chest_idx] > max_damage {
                                max_damage = self.a[weapon_idx][chest_idx];
                                best_chest_for_weapon = chest_idx as i32;
                            }
                        }
                        if best_chest_for_weapon != -1 {
                            next_candidates.push(self.next_state(h, c, opened_chests, actions, *total_overkill, *opened_count, weapon_idx as i32, best_chest_for_weapon as usize));
                        }
                    }
                }

                // 2. 素手での攻撃
                let mut min_hp = i64::MAX;
                let mut best_chest_for_bare_hand = -1;
                for chest_idx in 0..self.n {
                    if !opened_chests[chest_idx] && h[chest_idx] < min_hp {
                        min_hp = h[chest_idx];
                        best_chest_for_bare_hand = chest_idx as i32;
                    }
                }
                if best_chest_for_bare_hand != -1 {
                    next_candidates.push(self.next_state(h, c, opened_chests, actions, *total_overkill, *opened_count, -1, best_chest_for_bare_hand as usize));
                }
            }
            
            next_candidates.sort_by_cached_key(|state| self.score_func(state));
            next_candidates.reverse();
            
            let mut next_beam = Vec::new();
            let mut seen: HashSet<(Vec<i64>, Vec<i64>)> = HashSet::new();
            for state in next_candidates {
                // state.0はh, state.1はc
                let state_tuple = (state.0.clone(), state.1.clone());
                if !seen.contains(&state_tuple) {
                    // state.4はopened_count
                    if state.5 == self.n {
                        // state.3はactions
                        if best_solution_actions.is_none() || state.3.len() < best_solution_actions.as_ref().unwrap().len() {
                            best_solution_actions = Some(state.3.clone());
                        }
                    }
                    seen.insert(state_tuple);
                    next_beam.push(state);
                }
                
                if next_beam.len() >= BEAM_WIDTH {
                    break;
                }
            }
            beam = next_beam;
            
            if let Some(sol) = &best_solution_actions {
                if t >= sol.len() {
                    break;
                }
            }
        }
        
        if let Some(sol) = best_solution_actions {
            self.actions = sol;
        }
    }

    // Pythonのnext_stateと同様に、毎回Vecをクローンして新しい状態を返す
    fn next_state(&self, h: &[i64], c: &[i64], opened_chests: &[bool], actions: &[(i32, usize)], total_overkill: i64, opened_count: usize, weapon_idx: i32, chest_idx: usize) -> State {
        let mut new_h = h.to_vec();
        let mut new_c = c.to_vec();
        let mut new_actions = actions.to_vec();
        let mut new_opened_chests = opened_chests.to_vec();
        let mut new_total_overkill = total_overkill;
        let mut new_opened_count = opened_count;
        
        let damage = if weapon_idx == -1 { 1 } else {
            new_c[weapon_idx as usize] -= 1;
            self.a[weapon_idx as usize][chest_idx]
        };

        let hp_before_damage = new_h[chest_idx];
        new_h[chest_idx] -= damage;
        new_actions.push((weapon_idx, chest_idx));

        if hp_before_damage > 0 && new_h[chest_idx] <= 0 {
            new_opened_chests[chest_idx] = true;
            new_total_overkill += -new_h[chest_idx];
            new_opened_count += 1;
        }
        
        (new_h, new_c, new_opened_chests, new_actions, new_total_overkill, new_opened_count)
    }

    fn output(&self) {
        if self.actions.is_empty() {
            println!("0");
            return;
        }
        for (w, b) in &self.actions {
            println!("{} {}", w, b);
        }
    }
}

fn main() {
    let stdin = io::stdin();
    let mut lines = stdin.lock().lines();
    let n: usize = lines.next().unwrap().unwrap().trim().parse().unwrap();
    let h: Vec<i64> = lines.next().unwrap().unwrap().split_whitespace().map(|s| s.parse().unwrap()).collect();
    let c: Vec<i64> = lines.next().unwrap().unwrap().split_whitespace().map(|s| s.parse().unwrap()).collect();
    let mut a: Vec<Vec<i64>> = Vec::with_capacity(n);
    for _ in 0..n {
        a.push(lines.next().unwrap().unwrap().split_whitespace().map(|s| s.parse().unwrap()).collect());
    }

    let mut solver = Solve::new(n, h, c, a);
    solver.solve();
}