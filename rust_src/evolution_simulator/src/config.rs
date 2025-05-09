use clap::Parser;
use serde::Deserialize;

/// top‐level simulation settings
#[derive(Debug, Deserialize, Clone)]
pub struct SimulationConfig {
    pub report_interval: u32,
    pub n_ticks: u32,
    pub sleep_time: f64,
    pub enable_interactive: bool,
}
/// board dimensions
#[derive(Debug, Deserialize, Clone)]
pub struct BoardConfig {
    pub width: i32,
    pub height: i32,
}
/// mouse parameters
#[derive(Debug, Deserialize, Clone)]
pub struct MiceConfig {
    pub count: u32,
    pub preg_time: u32,
    pub vision: u32,
    pub hunger_priority: u32,
    pub max_age: u32,
}
/// owl parameters
#[derive(Debug, Deserialize, Clone)]
pub struct OwlsConfig {
    pub count: u32,
    pub max_age: u32,
}
/// entire config
#[derive(Debug, Deserialize, Clone)]
pub struct Config {
    pub simulation: SimulationConfig,
    pub board: BoardConfig,
    pub mice: MiceConfig,
    pub owls: OwlsConfig,
}
/// load from TOML
pub fn load_config(path: &str) -> Config {
    let s = std::fs::read_to_string(path).unwrap_or_default();
    toml::from_str(&s).unwrap()
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
