use rand::Rng;
use rand::seq::SliceRandom;
use rand::rng;  // new random generator function
use chrono::Local;
use std::fs::OpenOptions;
use std::io::Write;
use std::collections::HashSet;

pub struct AnimalData {
    pub id: String,
    pub age: u32,
    pub speed: u32,
    pub father: Option<String>,
    pub mother: Option<String>,
    pub location: (i32, i32),
    pub ticks_since_last_eaten: u32,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Species {
    Owl,
    Mouse,
}


pub trait Animal {
    fn data(&self) -> &AnimalData;
    fn data_mut(&mut self) -> &mut AnimalData;
    
    // default methods delegate to data()
    fn id(&self) -> &str              { &self.data().id }
    fn age(&self) -> u32              { self.data().age }
    fn speed(&self) -> u32            { self.data().speed }
    fn father(&self) -> Option<String>{ self.data().father.clone() }
    fn mother(&self) -> Option<String>{ self.data().mother.clone() }
    // you can still override or add more
    fn location(&self) -> Option<(i32, i32)> { Some(self.data().location) }
    
    // setter for location
    fn set_location(&mut self, loc: (i32, i32)) {
        self.data_mut().location = loc;
    }
    
    // move by (dx, dy), clamped to given bounds
    fn move_by(&mut self, dx: i32, dy: i32, max_x: i32, max_y: i32) {
        let (x, y) = self.data().location;
        let new_x = (x + dx).clamp(0, max_x);
        let new_y = (y + dy).clamp(0, max_y);
        self.set_location((new_x, new_y));
    }
    fn symbol(&self) -> &str;
    fn species(&self) -> Species;
}

pub struct Owl {
    data: AnimalData,
}

pub struct Mouse {
    data: AnimalData,
}

impl Animal for Owl {
    fn data(&self) -> &AnimalData { &self.data }
    fn data_mut(&mut self) -> &mut AnimalData { &mut self.data }
    fn symbol(&self) -> &str { "\x1b[31mO\x1b[0m" }
    fn species(&self) -> Species { Species::Owl }
}

impl Animal for Mouse {
    fn data(&self) -> &AnimalData { &self.data }
    fn data_mut(&mut self) -> &mut AnimalData { &mut self.data }
    fn symbol(&self) -> &str { "\x1b[34mM\x1b[0m" }
    fn species(&self) -> Species { Species::Mouse }
}

impl Owl {
    pub fn new(id: String, age: u32, speed: u32, father: Option<String>, mother: Option<String>, location: (i32, i32)) -> Self {
        Owl { data: AnimalData { id, age, speed, father, mother, location, ticks_since_last_eaten: 0 }, }
    }
}

impl Mouse {
    pub fn new(id: String, age: u32, speed: u32, father: Option<String>, mother: Option<String>, location: (i32, i32)) -> Self {
        Mouse { data: AnimalData { id, age, speed, father, mother, location, ticks_since_last_eaten: 0 }, }
    }
}

// Implement a "board" that the animals can move on
pub struct Board {
    width: i32,
    height: i32,
    animals: Vec<Box<dyn Animal>>,
    grass: HashSet<Position>,
}
type Position = (i32, i32);

impl Board {
    pub fn new(width: i32, height: i32) -> Self {
        Board { width, height, animals: Vec::new(), grass: HashSet::new() }
    }
    // initialize grass on all empty cells
    pub fn init_grass(&mut self) {
        self.grass.clear();
        for x in 0..=self.width {
            for y in 0..=self.height {
                let pos = (x, y);
                if !self.animals.iter().any(|a| a.location().unwrap() == pos) {
                    self.grass.insert(pos);
                }
            }
        }
    }
    pub fn add_animal(&mut self, a: Box<dyn Animal>) {
        self.animals.push(a);
    }
    pub fn animals(&self) -> &Vec<Box<dyn Animal>> {
        &self.animals
    }
    pub fn print(&self) {
        for row in (0..=self.height as usize).rev() {
            for col in 0..=self.width as usize {
                let pos = (col as i32, row as i32);
                if let Some(a) = self.animals.iter().find(|a| a.location() == Some(pos)) {
                    print!("{}", a.symbol());
                } else if self.grass.contains(&pos) {
                    // green grass
                    print!("\x1b[32m-\x1b[0m");
                } else {
                    print!(" ");
                }
            }
            println!();
        }
        // Print counts of alive mice and owls
        let mice_count = self.animals.iter().filter(|a| a.species() == Species::Mouse).count();
        let owl_count = self.animals.iter().filter(|a| a.species() == Species::Owl).count();
        println!("Mice: {}  Owls: {}", mice_count, owl_count);
    }
    pub fn mouse_positions(&self) -> Vec<Position> {
        self.animals.iter()
            .filter_map(|a| if a.species() == Species::Mouse { a.location() } else { None })
            .collect()
    }
    pub fn owl_positions(&self) -> HashSet<Position> {
        self.animals.iter()
            .filter_map(|a| if a.species() == Species::Owl { a.location() } else { None })
            .collect()
    }
    pub fn apply_moves(&mut self, moves: Vec<Option<Position>>) {
        // Prevent owls from moving onto a field already occupied by another owl
        let mut occupied_owl_positions: HashSet<Position> = self.owl_positions();
        for (animal, mov) in self.animals.iter_mut().zip(moves.into_iter()) {
            if let Some(target) = mov {
                match animal.species() {
                    Species::Owl => {
                        if !occupied_owl_positions.contains(&target) {
                            animal.set_location(target);
                            occupied_owl_positions.insert(target);
                        }
                    }
                    Species::Mouse => {
                        // Mouse moves: eat grass if present, reset or increment starvation counter
                        let ate = self.grass.remove(&target);
                        animal.set_location(target);
                        let data = animal.data_mut();
                        if ate {
                            data.ticks_since_last_eaten = 0;
                        } else {
                            data.ticks_since_last_eaten += 1;
                        }
                    }
                    _ => {}
                }
            }
        }
    }
    pub fn remove_caught_mice(&mut self) {
        let owl_positions = self.owl_positions();
        self.animals.retain(|a| {
            match a.species() {
                Species::Mouse => a.location().map_or(true, |pos| !owl_positions.contains(&pos)),
                _ => true,
            }
        });
    }
    pub fn remove_starved_mice(&mut self) {
        self.animals.retain(|a| {
            match a.species() {
                Species::Mouse => a.data().ticks_since_last_eaten < 10,
                _ => true,
            }
        });
    }
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
        board.add_animal(Box::new(Owl::new(id, 0, 10, None, None, pos)));
    }
    // spawn mice
    for (j, &pos) in chosen.iter().enumerate().skip(N_OWLS as usize) {
        let id = format!("Mouse{}", j - N_OWLS as usize + 1);
        board.add_animal(Box::new(Mouse::new(id, 0, 5, None, None, pos)));
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
            .map(|(idx, animal)| next_move(&**animal, idx, &board, &mouse_positions, &nonpreg, &mut rng))
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
                         board.add_animal(Box::new(Mouse::new(id, 0, 5, None, None, spawn)));
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

