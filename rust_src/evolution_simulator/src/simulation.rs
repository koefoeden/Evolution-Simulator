use chrono::Local;
use rand::{rng, Rng};
use rand::seq::SliceRandom;
use std::fs::OpenOptions;
use std::io::Write;
use std::time::Instant;

use crate::animal::{next_mouse_move, next_owl_move, Mouse, Owl, Sex};
use crate::board::{Board, Position};
use crate::config::Config;

/// Encapsulates simulation parameters, state, and loop
pub struct Simulation {
    pub sim_id: String,
    pub config: Config,
    pub display: bool,
    pub board: Board,
    pub rng: rand::prelude::ThreadRng,
    pub pregnancies: Vec<(String, u32)>,
    pub mouse_id_counter: usize,
    pub results_file: std::fs::File,
    pub current_tick: u32,    // new: how many ticks have been executed
}

impl Simulation {
    /// Create and initialize a new simulation instance
    pub fn new(display: bool, config: Config) -> Self {
        let sim_id = Local::now().format("%Y%m%d%H%M%S").to_string();
        
        // open or create results file and write header if empty
        let mut file = OpenOptions::new().create(true).append(true).open("../results.tsv").unwrap();
        if file.metadata().unwrap().len() == 0 {
            writeln!(file, "sim_id\treport_interval\tN_OWLS\tN_MICE\tMOUSE_PREG_TIME\ttick\tmice\towls").unwrap();
        }
        
        // initialize board and RNG
        let mut board = Board::new(config.board.width, config.board.height);
        let mut rng = rng();
        
        // randomly assign initial positions
        let total = (config.owls.count + config.mice.count) as usize;
        let mut all_positions: Vec<Position> = (0..=config.board.width)
        .flat_map(|x| (0..=config.board.height).map(move |y| (x, y)))
        .collect();
        all_positions.shuffle(&mut rng);
        let chosen = &all_positions[..total];
        
        // spawn owls and mice
        for &pos in chosen.iter().take(config.owls.count as usize) {
            board.add_owl(Owl::new(pos));
        }
        for (j, &pos) in chosen.iter().enumerate().skip(config.owls.count as usize) {
            let id = format!("Mouse{}", j - config.owls.count as usize + 1);
            let sex = if rng.random_bool(0.5) { Sex::Male } else { Sex::Female };
            board.add_mouse(Mouse::new(id, pos, sex));
        }
        board.init_grass();
        
        Simulation {
            sim_id,
            config: config.clone(),
            display,
            board,
            rng,
            pregnancies: Vec::new(),
            mouse_id_counter: config.mice.count as usize,
            results_file: file,
            current_tick: 0, // initialize current tick
        }
    }
    
    /// Run the simulation loop, returning total elapsed time
    pub fn run(&mut self) -> (std::time::Duration, u32) {
        let start = Instant::now();
        let mut ticks_executed = 0;
        if self.display {
            print!("\x1b[2J");
        }
        for tick in 0..self.config.simulation.n_ticks {
            ticks_executed += 1;
            if self.display {
                print!("\x1b[H");
                println!("Tick: {}", tick);
                println!("Board:");
                self.board.print();
                println!("Pregnancies: {}", self.pregnancies.len());
            }
            if tick % self.config.simulation.report_interval == 0 {
                let mice_count = self.board.mice.len();
                let owl_count = self.board.owls.len();
                writeln!(self.results_file, "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}", self.sim_id, self.config.simulation.report_interval, self.config.owls.count, self.config.mice.count, self.config.mice.preg_time, tick, mice_count, owl_count).unwrap();
            }
            std::thread::sleep(std::time::Duration::from_secs_f64(self.config.simulation.sleep_time));
            
            let mouse_positions = self.board.mouse_positions(); // Vec<Position>
            
            // Prepare moves for all mice and owls
            let mut moves: Vec<Option<Position>> = Vec::new();
            for idx in 0..self.board.mice.len() {
                moves.push(next_mouse_move(
                    idx,
                    &self.board,
                    &self.config.mice,
                    &self.pregnancies,
                ));
            }
            for idx in 0..self.board.owls.len() {
                moves.push(next_owl_move(idx, &self.board, &mouse_positions, &mut self.rng));
            }
            self.board.apply_moves(&moves);
            self.board.age_and_remove_old(
                self.config.mice.max_age,
                self.config.owls.max_age,
            );
            
            // then breeding, removals, etc.
            // Mice breeding: detect adjacency and register pregnancy
            for (idx, a) in self.board.mice.iter().enumerate() {
                let pos = a.location;
                let id = a.id.clone();
                if !self.pregnancies.iter().any(|(pid, _)| pid == &id) {
                    if let Some((_, other)) = self.board.mice.iter().enumerate()
                    .filter(|(j, b)| *j != idx && b.sex != a.sex)
                    .min_by_key(|(_, b)| {
                        let (mx, my) = b.location;
                        (mx - pos.0).abs() + (my - pos.1).abs()
                    })
                    {
                        let dist = (other.location.0 - pos.0).abs() + (other.location.1 - pos.1).abs();
                        if dist == 1 {
                            self.pregnancies.push((id, self.config.mice.preg_time));
                        }
                    }
                }
            }
            // progress pregnancies and spawn offspring when ready
            let mut births = Vec::new();
            for (parent_id, ticks) in self.pregnancies.iter_mut() {
                *ticks = ticks.saturating_sub(1);
                if *ticks == 0 {
                    births.push(parent_id.clone());
                }
            }
            // remove completed pregnancies
            self.pregnancies.retain(|(_, ticks)| *ticks > 0);
            // spawn offspring for each birth
            let dirs = [(0,1),(1,0),(0,-1),(-1,0)];
            for parent_id in births {
                if let Some(parent) = self.board.mice.iter().find(|a| a.id == parent_id) {
                    let pos = parent.location;
                    // find empty adjacent tile
                    if let Some(spawn) = dirs.iter().map(|&(dx,dy)| (pos.0+dx, pos.1+dy))
                    .filter(|&(sx,sy)| 0 <= sx && sx <= self.board.width && 0 <= sy && sy <= self.board.height)
                    .find(|&c| !self.board.mice.iter().any(|a| a.location == c)
                    && !self.board.owls.iter().any(|a| a.location == c))
                    {
                        self.mouse_id_counter += 1;
                        let id = format!("Mouse{}", self.mouse_id_counter);
                        let sex = if self.rng.random_bool(0.5) { Sex::Male } else { Sex::Female };
                        self.board.add_mouse(Mouse::new(id, spawn, sex));
                    }
                }
            }
            self.board.remove_caught_mice();
            self.board.remove_starved_mice();
            let mice_count = self.board.mice.len();
            let owl_count = self.board.owls.len();
            if mice_count == 0 {
                writeln!(self.results_file, "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
                self.sim_id, self.config.simulation.report_interval, self.config.owls.count, self.config.mice.count,
                self.config.mice.preg_time, tick, mice_count, owl_count).unwrap();
                println!("All mice died at tick {}. Exiting.", tick);
                break;
            }
        }
        (start.elapsed(), ticks_executed)
    }
    
    /// advance exactly one tick in interactive mode
    pub fn step_forward(&mut self) {
        // temporarily limit run() to a single tick
        let original_n = self.config.simulation.n_ticks;
        self.config.simulation.n_ticks = self.current_tick + 1; // run up to next tick
        let (_elapsed, ticks_done) = self.run();
        // restore full tick count
        self.config.simulation.n_ticks = original_n;
        // update an internal counter if you want to track current tick
        self.current_tick = ticks_done;
    }
    
    /// backtracking not yet implemented
    pub fn step_backward(&mut self) {
        // no-op
    }
    
    /// report how many ticks we've stepped through
    pub fn current_tick(&self) -> u32 {
        self.current_tick
    }
}
