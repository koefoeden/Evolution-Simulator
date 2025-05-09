use rand::Rng;
use std::collections::HashSet;

pub struct AnimalData {
    pub id: String,
    pub age: u32,
    pub speed: u32,
    pub father: Option<String>,
    pub mother: Option<String>,
    pub location: (i32, i32),
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
        Owl {
            data: AnimalData { id, age, speed, father, mother, location },
        }
    }
}

impl Mouse {
    pub fn new(id: String, age: u32, speed: u32, father: Option<String>, mother: Option<String>, location: (i32, i32)) -> Self {
        Mouse {
            data: AnimalData { id, age, speed, father, mother, location },
        }
    }
}

// Implement a "board" that the animals can move on
pub struct Board {
    width: i32,
    height: i32,
    animals: Vec<Box<dyn Animal>>,
}
impl Board {
    pub fn new(width: i32, height: i32) -> Self {
        Board { width, height, animals: Vec::new() }
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
                let mut found = false;
                for a in &self.animals {
                    if let Some((x, y)) = a.location() {
                        if (x as usize, y as usize) == (col, row) {
                            print!("{}", a.symbol());
                            found = true;
                            break;
                        }
                    }
                }
                if !found {
                    print!(".");
                }
            }
            println!();
        }
    }
}

fn main() {
    let n_owls = 5;
    let n_mice = 10;
    let mut board = Board::new(20, 10);
    let n_ticks = 50;
    let sleep_time_sec = 0.1;
    
    let mut rng = rand::thread_rng();
    // add random owls
    for i in 0..n_owls {
        let x = rng.gen_range(0..=board.width);
        let y = rng.gen_range(0..=board.height);
        let id = format!("Owl{}", i + 1);
        board.add_animal(Box::new(Owl::new(id, 0, 10, None, None, (x, y))));
    }
    // add random mice
    for i in 0..n_mice {
        let x = rng.gen_range(0..=board.width);
        let y = rng.gen_range(0..=board.height);
        let id = format!("Mouse{}", i + 1);
        board.add_animal(Box::new(Mouse::new(id, 0, 5, None, None, (x, y))));
    }
    
    for i in 0..n_ticks {
        print!("\x1b[2J\x1b[1;1H");  // clear screen
        println!("Tick: {}", i);
        println!("Board:");
        board.print();
        // work with decimal seconds
        std::thread::sleep(std::time::Duration::from_secs_f64(sleep_time_sec));  // sleep
        
        // move animals: owls chase nearest mouse, mice move randomly
        let (w, h) = (board.width, board.height);
        // snapshot all mouse positions
        let mouse_positions: Vec<(i32, i32)> = board
            .animals
            .iter()
            .filter_map(|a| match a.species() {
                Species::Mouse => a.location(),
                _ => None,
            })
            .collect();

        for animal in board.animals.iter_mut() {
            match animal.species() {
                Species::Owl => {
                    // find nearest mouse
                    if let (Some(&(mx, my)), Some((x, y))) = (
                        mouse_positions.iter().min_by_key(|&&(mx, my)| {
                            let (ax, ay) = animal.location().unwrap();
                            (mx - ax).abs() + (my - ay).abs()
                        }),
                        animal.location(),
                    ) {
                        let (ax, ay) = (x, y);
                        let dx = (mx - ax).signum();
                        let dy = (my - ay).signum();
                        animal.move_by(dx, dy, w, h);
                    }
                }
                Species::Mouse => {
                    // mouse: random move
                    let dx = rng.gen_range(-1..=1);
                    let dy = rng.gen_range(-1..=1);
                    animal.move_by(dx, dy, w, h);
                }
            }
        }
        // remove any mice caught by owls
        let owl_positions: HashSet<(i32, i32)> = board.animals
            .iter()
            .filter_map(|a| match a.species() {
                Species::Owl => a.location(),
                _ => None,
            })
            .collect();
        board.animals.retain(|a| {
            match a.species() {
                Species::Mouse => a.location().map_or(true, |pos| !owl_positions.contains(&pos)),
                _ => true,
            }
        });
    }
    
}

