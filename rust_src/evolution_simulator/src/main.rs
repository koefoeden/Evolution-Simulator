use rand::Rng;
use rand::seq::SliceRandom;
use rand::rng;  // new random generator function
use chrono::Local;
use std::fs::OpenOptions;
use std::io::Write;
use std::time::Instant;
use clap::Parser;

mod animal;
mod board;
use crate::animal::{Animal, Creature, Owl, Mouse, Species};
use crate::board::{Board, Position};

/// Command-line arguments
#[derive(Parser)]
#[command(author, version, about)]
struct Args {
    /// disable per-tick board and stats display
    #[arg(long)]
    quiet: bool,
}

fn next_move(
    animal: &dyn Animal,
    idx: usize,
    board: &Board,
    all_mice: &[Position],
    eligible_mice: &[Position],
    rng: &mut rand::prelude::ThreadRng,
) -> Option<Position> {
    let (w, h) = (board.width, board.height);
    let current_location = animal.location().unwrap();
    match animal.species() {
        Species::Owl => {
            if let Some(&(mx, my)) = all_mice.iter().min_by_key(|&&(mx, my)| {
                let (ax, ay) = current_location;
                (mx - ax).abs() + (my - ay).abs()
            }) {
                let (ax, ay) = current_location;
                let dx = (mx - ax).signum();
                let dy = (my - ay).signum();
                let target = ((ax + dx).clamp(0, w), (ay + dy).clamp(0, h));
                let occupied = board.animals.iter().enumerate().any(|(j, a)| {
                    j != idx && a.species() == Species::Owl && a.location().unwrap() == target
                });
                if !occupied {
                    Some(target)
                } else {
                    None
                }
            } else {
                None
            }
        }
        Species::Mouse => {
            // move toward closest non-pregnant mouse, or if adjacent, stay to breed
            let others: Vec<Position> = eligible_mice.iter().cloned().filter(|&p| p != current_location).collect();
            if others.is_empty() {
                return None;
            }
            // find closest
            let &(ox, oy) = others.iter().min_by_key(|&&(ox, oy)| {
                let (ax, ay) = current_location;
                (ox - ax).abs() + (oy - ay).abs()
            }).unwrap();
            let dist = (ox - current_location.0).abs() + (oy - current_location.1).abs();
            if dist == 1 {
                // adjacent: skip moving to allow breeding
                return None;
            }
            // step toward other
            let dx = (ox - current_location.0).signum();
            let dy = (oy - current_location.1).signum();
            let target = ((current_location.0 + dx).clamp(0, w), (current_location.1 + dy).clamp(0, h));
            // avoid colliding with another mouse
            let occupied = board.animals.iter().enumerate().any(|(j, a)| {
                j != idx && a.species() == Species::Mouse && a.location().unwrap() == target
            });
            if !occupied {
                Some(target)
            } else {
                None
            }
        }
    }
}

/// Encapsulates simulation parameters, state, and loop
pub struct Simulation {
    pub sim_id: String,
    pub report_interval: u32,
    pub n_owls: u32,
    pub n_mice: u32,
    pub mouse_preg_time: u32,
    pub board_width: i32,
    pub board_height: i32,
    pub n_ticks: u32,
    display: bool,
    sleep_time: f64,
    board: Board,
    rng: rand::prelude::ThreadRng,
    pregnancies: Vec<(String, u32)>,
    mouse_id_counter: usize,
    results_file: std::fs::File,
}

impl Simulation {
    /// Create and initialize a new simulation instance
    pub fn new(display: bool) -> Self {
        // IDs and constants
        let sim_id = Local::now().format("%Y%m%d%H%M%S").to_string();
        const REPORT_INTERVAL: u32 = 10;
        const N_OWLS: u32 = 10;
        const N_MICE: u32 = 30;
        const MOUSE_PREG_TIME: u32 = 10;
        const BOARD_WIDTH: i32 = 100;
        const BOARD_HEIGHT: i32 = 50;
        const N_TICKS: u32 = 10000;
        const SLEEP_TIME_SEC: f64 = 0.1;

        // open or create results file and write header if empty
        let mut file = OpenOptions::new().create(true).append(true).open("results.tsv").unwrap();
        if file.metadata().unwrap().len() == 0 {
            writeln!(file, "sim_id\treport_interval\tN_OWLS\tN_MICE\tMOUSE_PREG_TIME\ttick\tmice\towls").unwrap();
        }

        // initialize board and RNG
        let mut board = Board::new(BOARD_WIDTH, BOARD_HEIGHT);
        let mut rng = rng();

        // randomly assign initial positions
        let total = (N_OWLS + N_MICE) as usize;
        let mut all_positions: Vec<Position> = (0..=BOARD_WIDTH)
            .flat_map(|x| (0..=BOARD_HEIGHT).map(move |y| (x, y)))
            .collect();
        all_positions.shuffle(&mut rng);
        let chosen = &all_positions[..total];

        // spawn owls and mice
        for (i, &pos) in chosen.iter().enumerate().take(N_OWLS as usize) {
            let id = format!("Owl{}", i + 1);
            board.add_animal(Creature::Owl(Owl::new(id, 0, 10, None, None, pos)));
        }
        for (j, &pos) in chosen.iter().enumerate().skip(N_OWLS as usize) {
            let id = format!("Mouse{}", j - N_OWLS as usize + 1);
            board.add_animal(Creature::Mouse(Mouse::new(id, 0, 5, None, None, pos)));
        }
        board.init_grass();

        Simulation {
            sim_id,
            report_interval: REPORT_INTERVAL,
            n_owls: N_OWLS,
            n_mice: N_MICE,
            mouse_preg_time: MOUSE_PREG_TIME,
            board_width: BOARD_WIDTH,
            board_height: BOARD_HEIGHT,
            n_ticks: N_TICKS,
            display,
            sleep_time: SLEEP_TIME_SEC,
            board,
            rng,
            pregnancies: Vec::new(),
            mouse_id_counter: N_MICE as usize,
            results_file: file,
        }
    }

    /// Run the simulation loop, returning total elapsed time
    pub fn run(&mut self) -> (std::time::Duration, u32) {
        let start = Instant::now();
        let mut ticks_executed = 0;
        for tick in 0..self.n_ticks {
            ticks_executed += 1;
            if self.display {
                print!("\x1b[2J\x1b[1;1H");
                println!("Tick: {}", tick);
                println!("Board:");
                self.board.print();
                // display number of pending mouse pregnancies
                println!("Pregnancies: {}", self.pregnancies.len());
            }
            // record counts every REPORT_INTERVAL ticks
            if tick % self.report_interval == 0 {
                let mice_count = self.board.animals.iter().filter(|a| a.species() == Species::Mouse).count();
                let owl_count = self.board.animals.iter().filter(|a| a.species() == Species::Owl).count();
                writeln!(self.results_file, "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}", self.sim_id, self.report_interval, self.n_owls, self.n_mice, self.mouse_preg_time, tick, mice_count, owl_count).unwrap();
            }
            std::thread::sleep(std::time::Duration::from_secs_f64(self.sleep_time));

            let mouse_positions = self.board.mouse_positions();
            // compute non-pregnant mouse positions
            let nonpreg: Vec<Position> = self.board.animals.iter()
                .filter(|a| a.species() == Species::Mouse)
                .filter(|a| !self.pregnancies.iter().any(|(id, _)| id == a.id()))
                .filter_map(|a| a.location())
                .collect();
            let moves: Vec<Option<Position>> = self.board.animals.iter().enumerate()
                .map(|(idx, animal)| next_move(animal, idx, &self.board, &mouse_positions, &nonpreg, &mut self.rng))
                .collect();
            self.board.apply_moves(moves);
            // Mice breeding: detect adjacency and register pregnancy
            let current_mouse_positions = self.board.mouse_positions();
            for a in self.board.animals.iter().filter(|a| a.species() == Species::Mouse) {
                if let Some(pos) = a.location() {
                    let id = a.id().to_string();
                    // if not already pregnant
                    if !self.pregnancies.iter().any(|(pid, _)| pid == &id) {
                        // find nearest other mouse
                        if let Some(&other) = current_mouse_positions.iter()
                            .filter(|&&p| p != pos)
                            .min_by_key(|&&(mx, my)| (mx - pos.0).abs() + (my - pos.1).abs())
                        {
                            let dist = (other.0 - pos.0).abs() + (other.1 - pos.1).abs();
                            if dist == 1 {
                                self.pregnancies.push((id, self.mouse_preg_time));
                            }
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
                if let Some(parent) = self.board.animals.iter().find(|a| a.id() == parent_id && a.species() == Species::Mouse) {
                    if let Some(pos) = parent.location() {
                        // find empty adjacent tile
                        if let Some(spawn) = dirs.iter().map(|&(dx,dy)| (pos.0+dx, pos.1+dy))
                            .filter(|&(sx,sy)| 0 <= sx && sx <= self.board.width && 0 <= sy && sy <= self.board.height)
                            .find(|&c| !self.board.animals.iter().any(|a| a.location().unwrap() == c))
                         {
                             self.mouse_id_counter += 1;
                             let id = format!("Mouse{}", self.mouse_id_counter);
                             self.board.add_animal(Creature::Mouse(Mouse::new(id, 0, 5, None, None, spawn)));
                         }
                     }
                 }
             }
            self.board.remove_caught_mice();
            // remove any mice that have starved (10+ ticks without eating)
            self.board.remove_starved_mice();
            // if no mice remain, log final state and terminate
            let mice_count = self.board.animals.iter().filter(|a| a.species() == Species::Mouse).count();
            let owl_count = self.board.animals.iter().filter(|a| a.species() == Species::Owl).count();
            if mice_count == 0 {
                writeln!(self.results_file, "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
                    self.sim_id, self.report_interval, self.n_owls, self.n_mice,
                    self.mouse_preg_time, tick, mice_count, owl_count).unwrap();
                println!("All mice died at tick {}. Exiting.", tick);
                break;
            }
        }
        (start.elapsed(), ticks_executed)
    }
}

fn main() {
    let args = Args::parse();
    let mut sim = Simulation::new(!args.quiet);
    let (elapsed, ticks) = sim.run();
    println!("Simulation completed in {:?} after {} ticks", elapsed, ticks);
    // record performance summary
    let perf_path = "simulation_performance.tsv";
    let mut perf_file = OpenOptions::new().create(true).append(true).open(perf_path).unwrap();
    if perf_file.metadata().unwrap().len() == 0 {
        writeln!(perf_file, "sim_id\tn_owls\tn_mice\tboard_width\tboard_height\tticks_elapsed\ttotal_time_s\tavg_tick_s").unwrap();
    }
    let total_secs = elapsed.as_secs_f64();
    let avg_secs = total_secs / ticks as f64;
    writeln!(perf_file, "{}\t{}\t{}\t{}\t{}\t{}\t{:.6}\t{:.6}",
        sim.sim_id, sim.n_owls, sim.n_mice, sim.board_width, sim.board_height,
        ticks, total_secs, avg_secs).unwrap();
}

