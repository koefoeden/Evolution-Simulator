use rand::rng;
use rand::Rng;
use rand::seq::SliceRandom; // <-- change from rand::prelude::SliceRandom to rand::seq::SliceRandom
use rand::prelude::IndexedRandom;
use chrono::Local;
use std::fs::OpenOptions;
use std::io::Write;
use std::time::Instant;


mod animal;
mod board;
mod controller;                      // new
use crate::animal::{Owl, Mouse, Sex};
use crate::board::{Board, Position};
use crate::config::{MiceConfig, OwlConfig, SimulationConfig, BoardConfig, Config, load_config};
use crate::controller::run_control_loop;  // new



fn main() {
    let args = Args::parse();
    let config = load_config(&args.config);
    let mut sim = Simulation::new(!args.quiet, config.clone());
    
    if config.simulation.enable_interactive {
        run_control_loop(&mut sim);   // interactive stepping
    } else {
        let (elapsed, ticks) = sim.run();  // batch run as before
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
        sim.config.board.width, sim.config.board.height,
        sim.sim_id, sim.config.owls.count, sim.config.mice.count, 
        ticks, total_secs, avg_secs).unwrap();
    }
}
