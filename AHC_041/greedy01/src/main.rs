use std::io::{self, Read};

struct Input {
    n: usize,
    m: usize,
    h: usize,
    a: Vec<i64>,
    edges: Vec<(usize, usize)>,
    coords: Vec<(i32, i32)>,
}

struct State {
    p: Vec<i32>,
}

impl State {
    fn new(n: usize) -> Self {
        let mut p = vec![-1; n];
        State { p }
    }
    
    fn solve(&self, input: &Input) -> i64 {
        0
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
    let coords: Vec<(i32, i32)> = (0..h)
        .map(|_| {
            let x: i32 = takens.next().unwrap().parse().unwrap();
            let y: i32 = takens.next().unwrap().parse().unwrap();
            (x, y)
        })
        .collect();

    let input = Input { n, m, h, a, edges, coords };
    let state = State::new(n);
    let _ = state.solve(&input);
    state.output();
}
