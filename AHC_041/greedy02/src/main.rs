use std::io::{self, Read};
use std::collections::VecDeque;

struct Input {
    n: usize,
    m: usize,
    h: usize,
    a: Vec<i64>,
    adj: Vec<Vec<usize>>,
    coords: Vec<(i32, i32)>,
}

struct State {
    p: Vec<i32>,
}

impl State {
    fn new(n: usize) -> Self {
        let mut p = vec![-2; n];
        State { p }
    }
    
    fn solve(&mut self, input: &Input) {
        self.greedy(input);
        self.output();
    }

    fn greedy(&mut self, input: &Input) {
        let n = input.n;
        let h_max = input.h;
        let mut used = vec![false; n];
        let mut vec: Vec<usize> = (0..n).collect();
        for &root in &vec {
            if self.p[root] != -2 {
                continue;
            }
            self.p[root] = -1;
            let mut queue = VecDeque::new();
            queue.push_back((root, 0));
            while let Some((u, h)) = queue.pop_front() {
                if h >= h_max {
                    break;
                }
                for &v in &input.adj[u] {
                    if self.p[v] == -2 {
                        self.p[v] = u as i32;
                        queue.push_back((v, h + 1));
                    }
                }
            }
        }
        for i in 0..n {
            if self.p[i] == -2 {
                self.p[i] = -1;
            }
        }
    }

    fn get_height(&self, v: usize, input: &Input) -> Option<i32> {
        let mut curr = v;
        let mut h = 0;
        for _ in 0..100 {
            if self.p[curr] == -1 { return Some(h); }
            curr = self.p[curr] as usize;
            h += 1;
        }
        None
    }

    fn output(&self) {
        let res: Vec<String> = self.p.iter().map(|&x| x.to_string()).collect();
        println!("{}", res.join(" "));
    }

}

fn main() {
    let mut inp = String::new();
    io::stdin().read_to_string(&mut inp).unwrap();
    let mut takens = inp.split_ascii_whitespace();

    let n: usize = takens.next().unwrap().parse().unwrap();
    let m: usize = takens.next().unwrap().parse().unwrap();
    let h: usize = takens.next().unwrap().parse().unwrap();
    let a: Vec<i64> = (0..n)
        .map(|_| takens.next().unwrap().parse().unwrap())
        .collect();
    let edges: Vec<(usize, usize)> = (0..m)
        .map(|_| {
            let u: usize = takens.next().unwrap().parse().unwrap();
            let v: usize = takens.next().unwrap().parse().unwrap();
            (u, v)
        })
        .collect();
    let mut adj = vec![vec![]; n];
    for &(u, v) in &edges {
        adj[u].push(v);
        adj[v].push(u);
    }
    let coords: Vec<(i32, i32)> = (0..n)
        .map(|_| {
            let x: i32 = takens.next().unwrap().parse().unwrap();
            let y: i32 = takens.next().unwrap().parse().unwrap();
            (x, y)
        })
        .collect();
    
    
    let input = Input { n, m, h, a, adj, coords };
    let mut state = State::new(n);
    let _ = state.solve(&input);
}
