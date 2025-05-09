use rand::Rng;
use rand::seq::SliceRandom;
use rand::rng;  // new random generator function
use chrono::Local;
use std::fs::OpenOptions;
use std::io::Write;

mod animal;
mod board;
use crate::animal::{Animal, Creature, Owl, Mouse, Species};
use crate::board::{Board, Position};

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

fn main() {
    // generate a unique simulation ID based on current timestamp
    let sim_id = Local::now().format("%Y%m%d%H%M%S").to_string();
    const REPORT_INTERVAL: u32 = 10;
    // open (or create) results file and write header if empty
    let file_path = "results.tsv";
    let mut file = OpenOptions::new().create(true).append(true).open(file_path).unwrap();
    if file.metadata().unwrap().len() == 0 {
        writeln!(file, "sim_id\treport_interval\tN_OWLS\tN_MICE\tMOUSE_PREG_TIME\ttick\tmice\towls").unwrap();
    }
    const N_OWLS:u32 = 10;
    const N_MICE:u32 = 30;
    const MOUSE_PREG_TIME: u32 = 10;
    const BOARD_WITH:i32 = 100;
    const BOARD_HEIGHT:i32 = 50;
    let mut board = Board::new(BOARD_WITH, BOARD_HEIGHT);
    const N_TICKS:u32 = 10000;
    const SLEEP_TIME_SEC:f64 = 0.1;
    
    let mut rng = rng();
    // randomly pick unique positions for owls and mice
    let total = (N_OWLS + N_MICE) as usize;
    let mut all_positions: Vec<Position> = (0..=board.width)
        .flat_map(|x| (0..=board.height).map(move |y| (x, y)))
        .collect();
    all_positions.shuffle(&mut rng);
    let chosen = &all_positions[..total];
    // spawn owls
    for (i, &pos) in chosen.iter().enumerate().take(N_OWLS as usize) {
        let id = format!("Owl{}", i + 1);
        board.add_animal(Creature::Owl(Owl::new(id, 0, 10, None, None, pos)));
    }
    // spawn mice
    for (j, &pos) in chosen.iter().enumerate().skip(N_OWLS as usize) {
        let id = format!("Mouse{}", j - N_OWLS as usize + 1);
        board.add_animal(Creature::Mouse(Mouse::new(id, 0, 5, None, None, pos)));
    }
    // initialize grass after initial placement
    board.init_grass();
    // track counter for generating new mouse IDs
    let mut mouse_id_counter = N_MICE as usize;
    // pregnancy records: (parent_id, ticks_until_birth)
    let mut pregnancies: Vec<(String, u32)> = Vec::new();

    for tick in 0..N_TICKS {
        print!("\x1b[2J\x1b[1;1H");
        println!("Tick: {}", tick);
        println!("Board:");
        board.print();
        // display number of pending mouse pregnancies
        println!("Pregnancies: {}", pregnancies.len());
        // record counts every REPORT_INTERVAL ticks
        if tick % REPORT_INTERVAL == 0 {
            let mice_count = board.animals.iter().filter(|a| a.species() == Species::Mouse).count();
            let owl_count = board.animals.iter().filter(|a| a.species() == Species::Owl).count();
            writeln!(file, "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}", sim_id, REPORT_INTERVAL, N_OWLS, N_MICE, MOUSE_PREG_TIME, tick, mice_count, owl_count).unwrap();
        }
        std::thread::sleep(std::time::Duration::from_secs_f64(SLEEP_TIME_SEC));

        let mouse_positions = board.mouse_positions();
        // compute non-pregnant mouse positions
        let nonpreg: Vec<Position> = board.animals.iter()
            .filter(|a| a.species() == Species::Mouse)
            .filter(|a| !pregnancies.iter().any(|(id, _)| id == a.id()))
            .filter_map(|a| a.location())
            .collect();
        let moves: Vec<Option<Position>> = board.animals.iter().enumerate()
            .map(|(idx, animal)| next_move(animal, idx, &board, &mouse_positions, &nonpreg, &mut rng))
            .collect();
        board.apply_moves(moves);
        // Mice breeding: detect adjacency and register pregnancy
        let current_mouse_positions = board.mouse_positions();
        for a in board.animals.iter().filter(|a| a.species() == Species::Mouse) {
            if let Some(pos) = a.location() {
                let id = a.id().to_string();
                // if not already pregnant
                if !pregnancies.iter().any(|(pid, _)| pid == &id) {
                    // find nearest other mouse
                    if let Some(&other) = current_mouse_positions.iter()
                        .filter(|&&p| p != pos)
                        .min_by_key(|&&(mx, my)| (mx - pos.0).abs() + (my - pos.1).abs())
                    {
                        let dist = (other.0 - pos.0).abs() + (other.1 - pos.1).abs();
                        if dist == 1 {
                            pregnancies.push((id, MOUSE_PREG_TIME));
                        }
                    }
                }
            }
        }
        // progress pregnancies and spawn offspring when ready
        let mut births = Vec::new();
        for (parent_id, ticks) in pregnancies.iter_mut() {
            *ticks = ticks.saturating_sub(1);
            if *ticks == 0 {
                births.push(parent_id.clone());
            }
        }
        // remove completed pregnancies
        pregnancies.retain(|(_, ticks)| *ticks > 0);
        // spawn offspring for each birth
        let dirs = [(0,1),(1,0),(0,-1),(-1,0)];
        for parent_id in births {
            if let Some(parent) = board.animals.iter().find(|a| a.id() == parent_id && a.species() == Species::Mouse) {
                if let Some(pos) = parent.location() {
                    // find empty adjacent tile
                    if let Some(spawn) = dirs.iter().map(|&(dx,dy)| (pos.0+dx, pos.1+dy))
                        .filter(|&(sx,sy)| 0 <= sx && sx <= board.width && 0 <= sy && sy <= board.height)
                        .find(|&c| !board.animals.iter().any(|a| a.location().unwrap() == c))
                     {
                         mouse_id_counter += 1;
                         let id = format!("Mouse{}", mouse_id_counter);
                         board.add_animal(Creature::Mouse(Mouse::new(id, 0, 5, None, None, spawn)));
                     }
                 }
             }
         }
        board.remove_caught_mice();
        // remove any mice that have starved (10+ ticks without eating)
        board.remove_starved_mice();
        // if no mice remain, log final state and terminate
        let mice_count = board.animals.iter().filter(|a| a.species() == Species::Mouse).count();
        if mice_count == 0 {
            let owl_count = board.animals.iter().filter(|a| a.species() == Species::Owl).count();
            writeln!(file, "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}", sim_id, REPORT_INTERVAL, N_OWLS, N_MICE, MOUSE_PREG_TIME, tick, mice_count, owl_count).unwrap();
            println!("All mice died at tick {}. Exiting.", tick);
            return;
        }
    }
}

