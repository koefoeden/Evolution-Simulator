use std::collections::HashSet;
use crate::animal::{Animal, AnimalData, Species};

pub type Position = (i32, i32);

pub struct Board {
    pub width: i32,
    pub height: i32,
    pub animals: Vec<Box<dyn Animal>>,
    pub grass: HashSet<Position>,
}

impl Board {
    pub fn new(width: i32, height: i32) -> Self {
        Board { width, height, animals: Vec::new(), grass: HashSet::new() }
    }

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

    pub fn print(&self) {
        for row in (0..=self.height as usize).rev() {
            for col in 0..=self.width as usize {
                let pos = (col as i32, row as i32);
                if let Some(a) = self.animals.iter().find(|a| a.location() == Some(pos)) {
                    print!("{}", a.symbol());
                } else if self.grass.contains(&pos) {
                    print!("\x1b[32m-\x1b[0m");
                } else {
                    print!(" ");
                }
            }
            println!();
        }

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
        let mut occupied_owl_positions: HashSet<Position> = self.owl_positions();
        for (animal, mov) in self.animals.iter_mut().zip(moves) {
            if let Some(target) = mov {
                match animal.species() {
                    Species::Owl => {
                        if !occupied_owl_positions.contains(&target) {
                            animal.set_location(target);
                            occupied_owl_positions.insert(target);
                        }
                    }
                    Species::Mouse => {
                        let ate = self.grass.remove(&target);
                        animal.set_location(target);
                        let data = animal.data_mut();
                        if ate {
                            data.ticks_since_last_eaten = 0;
                        } else {
                            data.ticks_since_last_eaten += 1;
                        }
                    }
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
