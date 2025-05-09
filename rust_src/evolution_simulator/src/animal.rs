/// Sex of an animal.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Sex {
    Male,
    Female,
}

/// Mouse animal.
#[derive(Clone)]
pub struct Mouse {
    pub id: String,
    pub location: (i32, i32),
    pub ticks_since_last_eaten: u32,
    pub sex: Sex,
}

#[derive(Clone)]
pub struct Owl {
    pub id: String,
    pub location: (i32, i32),
    pub ticks_since_last_eaten: u32,
    pub sex: Sex,
}

impl Mouse {
    pub fn new(id: String, location: (i32, i32), sex: Sex) -> Self {
        Mouse { id, location, ticks_since_last_eaten: 0, sex }
    }
    pub fn symbol(&self) -> &str {
        match self.sex {
            Sex::Female => "\x1b[35mM\x1b[0m",
            Sex::Male => "\x1b[34mM\x1b[0m",
        }
    }
}

impl Owl {
    pub fn new(id: String, location: (i32, i32), sex: Sex) -> Self {
        Owl { id, location, ticks_since_last_eaten: 0, sex }
    }
    pub fn symbol(&self) -> &str {
        "\x1b[31mO\x1b[0m"
    }
}
