use rand::rng;
use rand::Rng;
use rand::seq::SliceRandom; // <-- change from rand::prelude::SliceRandom to rand::seq::SliceRandom
use rand::prelude::IndexedRandom;
use chrono::Local;
use std::fs::OpenOptions;
use std::io::Write;
use std::time::Instant;
use clap::Parser;
use serde::Deserialize;

mod animal;
mod board;
use crate::animal::{Owl, Mouse, Sex};
use crate::board::{Board, Position};

#[derive(Debug, Deserialize, Clone)]
pub struct SimulationConfig {
    pub report_interval: u32,
    pub n_ticks: u32,
    pub sleep_time: f64,
}

#[derive(Debug, Deserialize, Clone)]
pub struct BoardConfig {
    pub width: i32,
    pub height: i32,
}

#[derive(Debug, Deserialize, Clone)]
pub struct MiceConfig {
    pub count: u32,
    pub preg_time: u32,
    pub vision: u32,
    pub hunger_priority: u32, // new: tick threshold to prioritize grass
}

#[derive(Debug, Deserialize, Clone)]
pub struct OwlsConfig {
    pub count: u32,
}

#[derive(Debug, Deserialize, Clone)]
pub struct Config {
    pub simulation: SimulationConfig,
    pub board: BoardConfig,
    pub mice: MiceConfig,
    pub owls: OwlsConfig,
}

fn load_config(path: &str) -> Config {
    use std::fs;
    let content = fs::read_to_string(path).unwrap_or_default();
    toml::from_str(&content).unwrap()
}

/// Command-line arguments
#[derive(Parser)]
#[command(author, version, about)]
struct Args {
    /// disable per-tick board and stats display
    #[arg(long)]
    quiet: bool,
    /// path to config file
    #[arg(long, default_value = "../config.toml")]
    config: String,
}

/// Compute the next move for an owl.
/// If the direct path is blocked by another owl, try a random adjacent unoccupied tile.
fn next_owl_move(
    idx: usize,
    board: &Board,
    all_mice: &[Position],
    rng: &mut rand::prelude::ThreadRng,
) -> Option<Position> {
    let (w, h) = (board.width, board.height);
    let current_location = board.owls[idx].location;
    if let Some(&(mx, my)) = all_mice.iter().min_by_key(|&&(mx, my)| {
        let (ax, ay) = current_location;
        (mx - ax).abs() + (my - ay).abs()
    }) {
        let (ax, ay) = current_location;
        let dx = (mx - ax).signum();
        let dy = (my - ay).signum();
        let target = ((ax + dx).clamp(0, w), (ay + dy).clamp(0, h));
        let occupied = board.owls.iter().enumerate().any(|(j, a)| {
            j != idx && a.location == target
        });
        if !occupied {
            Some(target)
        } else {
            // Try a random adjacent unoccupied tile (including diagonals)
            let mut candidates = vec![
                (ax + 1, ay), (ax - 1, ay), (ax, ay + 1), (ax, ay - 1),
                (ax + 1, ay + 1), (ax - 1, ay - 1), (ax + 1, ay - 1), (ax - 1, ay + 1)
            ];
            candidates.retain(|&(x, y)| x >= 0 && x <= w && y >= 0 && y <= h);
            candidates.retain(|&pos| !board.owls.iter().any(|a| a.location == pos));
            if let Some(choice) = candidates.choose(rng) {
                Some(*choice)
            } else {
                None
            }
        }
    } else {
        None
    }
}

/// Compute the next move for a mouse.
fn next_mouse_move(
    idx: usize,
    board: &Board,
    mice_cfg: &MiceConfig,
) -> Option<Position> {
    let (w, h) = (board.width, board.height);
    let current_location = board.mice[idx].location;
    let vision = mice_cfg.vision as i32;

    // new hunger check
    let hunger = board.mice[idx].ticks_since_last_eaten as i32;
    let threshold = mice_cfg.hunger_priority as i32;
    if hunger > threshold {
        // seek nearest grass within vision
        let grass_targets: Vec<_> = board.grass.iter()
            .filter(|&&(gx, gy)| {
                let d = (gx - current_location.0).abs()
                      + (gy - current_location.1).abs();
                d <= vision
            })
            .map(|&pos| {
                let d = (pos.0 - current_location.0).abs()
                      + (pos.1 - current_location.1).abs();
                (pos, d)
            })
            .collect();
        if grass_targets.is_empty() {
            return None;
        }
        let &(target_pos, dist) = grass_targets.iter().min_by_key(|(_, d)| *d).unwrap();
        if dist == 0 {
            return None;
        }
        let dx = (target_pos.0 - current_location.0).signum();
        let dy = (target_pos.1 - current_location.1).signum();
        let next = ((current_location.0 + dx).clamp(0, w),
                    (current_location.1 + dy).clamp(0, h));
        let occupied = board.mice.iter().enumerate().any(|(j, a)| {
            j != idx && a.location == next
        });
        return if !occupied { Some(next) } else { None };
    }

    let my_sex = board.mice[idx].sex;
    let others: Vec<_> = board.mice.iter()
        .enumerate()
        .filter(|(j, a)| *j != idx && a.sex != my_sex)
        .filter_map(|(_, a)| {
            let dist = (a.location.0 - current_location.0).abs()
                     + (a.location.1 - current_location.1).abs();
            if dist <= vision { Some((a.location, dist)) } else { None }
        })
        .collect();

    if others.is_empty() {
        // seek nearest grass within vision
        let grass_targets: Vec<_> = board.grass.iter()
            .filter(|&&(gx, gy)| {
                let dist = (gx - current_location.0).abs()
                         + (gy - current_location.1).abs();
                dist <= vision
            })
            .map(|&pos| {
                let dist = (pos.0 - current_location.0).abs()
                         + (pos.1 - current_location.1).abs();
                (pos, dist)
            })
            .collect();
        if grass_targets.is_empty() {
            return None;
        }
        let &(target_pos, dist) = grass_targets.iter()
            .min_by_key(|(_, d)| *d)
            .unwrap();
        if dist == 0 {
            return None;
        }
        let dx = (target_pos.0 - current_location.0).signum();
        let dy = (target_pos.1 - current_location.1).signum();
        let next = (
            (current_location.0 + dx).clamp(0, w),
            (current_location.1 + dy).clamp(0, h),
        );
        let occupied = board.mice.iter().enumerate().any(|(j, a)| {
            j != idx && a.location == next
        });
        return if !occupied { Some(next) } else { None };
    }

    let &(target_pos, dist) = others.iter().min_by_key(|(_, d)| *d).unwrap();

    if dist == 1 {
        return None;
    }

    let dx = (target_pos.0 - current_location.0).signum();
    let dy = (target_pos.1 - current_location.1).signum();
    let next = ((current_location.0 + dx).clamp(0, w), (current_location.1 + dy).clamp(0, h));

    let occupied = board.mice.iter().enumerate().any(|(j, a)| {
        j != idx && a.location == next
    });
    if !occupied {
        Some(next)
    } else {
        None
    }
}

/// Encapsulates simulation parameters, state, and loop
pub struct Simulation {
    pub sim_id: String,
    pub config: Config,
    display: bool,
    board: Board,
    rng: rand::prelude::ThreadRng,
    pregnancies: Vec<(String, u32)>,
    mouse_id_counter: usize,
    results_file: std::fs::File,
}

impl Simulation {
    /// Create and initialize a new simulation instance
    pub fn new(display: bool, config: Config) -> Self {
        let sim_id = Local::now().format("%Y%m%d%H%M%S").to_string();

        // open or create results file and write header if empty
        let mut file = OpenOptions::new().create(true).append(true).open("results.tsv").unwrap();
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
        for (i, &pos) in chosen.iter().enumerate().take(config.owls.count as usize) {
            let id = format!("Owl{}", i + 1);
            board.add_owl(Owl::new(id, pos, Sex::Male));
        }
        for (j, &pos) in chosen.iter().enumerate().skip(config.owls.count as usize) {
            let id = format!("Mouse{}", j - config.owls.count as usize + 1);
            let sex = if rng.gen_bool(0.5) { Sex::Male } else { Sex::Female };
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

            let mouse_positions = self.board.mouse_positions();

            // Prepare moves for all mice and owls
            let mut moves: Vec<Option<Position>> = Vec::new();
            for idx in 0..self.board.mice.len() {
                moves.push(next_mouse_move(idx, &self.board, &self.config.mice));
            }
            for idx in 0..self.board.owls.len() {
                moves.push(next_owl_move(idx, &self.board, mouse_positions, &mut self.rng));
            }
            self.board.apply_moves(&moves);

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
                        let sex = if self.rng.gen_bool(0.5) { Sex::Male } else { Sex::Female };
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
}

fn main() {
    let args = Args::parse();
    let config = load_config(&args.config);
    let mut sim = Simulation::new(!args.quiet, config.clone());
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
        sim.sim_id, sim.config.owls.count, sim.config.mice.count, sim.config.board.width, sim.config.board.height,
        ticks, total_secs, avg_secs).unwrap();
}
