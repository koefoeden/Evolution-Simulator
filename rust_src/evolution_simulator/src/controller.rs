use crossterm::{
    event::{self, Event, KeyCode},
    terminal::{self, ClearType},
    ExecutableCommand,
};
use std::io::stdout;
use std::time::Duration;
use crate::simulation::Simulation;  // fixed path

/// Listen for right/left arrow keys to step simulation forward/back.
/// Press 'q' to exit.
pub fn run_control_loop(sim: &mut Simulation) {
    let mut out = stdout();
    terminal::enable_raw_mode().unwrap();
    out.execute(terminal::Clear(ClearType::All)).ok();
    loop {
        // poll every 100ms
        if event::poll(Duration::from_millis(100)).unwrap() {
            if let Event::Key(k) = event::read().unwrap() {
                match k.code {
                    KeyCode::Right => sim.step_forward(),      // advance one tick
                    KeyCode::Left  => sim.step_backward(),     // backtrack one tick
                    KeyCode::Char('q') | KeyCode::Esc => break,
                    _ => {}
                }
                // redraw board after each action
                out.execute(terminal::Clear(ClearType::All)).ok();
                println!("Tick: {}", sim.current_tick());
                sim.board.print();
            }
        }
    }
    terminal::disable_raw_mode().unwrap();
}
