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

    fn id(&self) -> &str { &self.data().id }
    fn age(&self) -> u32 { self.data().age }
    fn speed(&self) -> u32 { self.data().speed }
    fn father(&self) -> Option<String> { self.data().father.clone() }
    fn mother(&self) -> Option<String> { self.data().mother.clone() }
    fn location(&self) -> Option<(i32, i32)> { Some(self.data().location) }

    fn set_location(&mut self, loc: (i32, i32)) {
        self.data_mut().location = loc;
    }

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
    pub data: AnimalData,
}

pub struct Mouse {
    pub data: AnimalData,
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
        Owl { data: AnimalData { id, age, speed, father, mother, location, ticks_since_last_eaten: 0 } }
    }
}

impl Mouse {
    pub fn new(id: String, age: u32, speed: u32, father: Option<String>, mother: Option<String>, location: (i32, i32)) -> Self {
        Mouse { data: AnimalData { id, age, speed, father, mother, location, ticks_since_last_eaten: 0 } }
    }
}
