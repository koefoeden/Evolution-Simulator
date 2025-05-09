use std::collections::HashSet;
use crate::animal::{Mouse, Owl};

/// Board holds all simulation state for animals and grass.
pub type Position = (i32, i32);

pub struct Board {
    pub width: i32,
    pub height: i32,
    pub mice: Vec<Mouse>,
    pub owls: Vec<Owl>,
    pub grass: HashSet<Position>,
    pub dead_mice_total: usize,
    pub dead_mice_starved: usize,
    pub dead_mice_eaten: usize,
    pub dead_mice_old_age: usize,  // new
    pub dead_owls_old_age: usize,  // new
}

impl Board {
    pub fn new(width: i32, height: i32) -> Self {
        Board {
            width,
            height,
            mice: Vec::new(),
            owls: Vec::new(),
            grass: HashSet::new(),
            dead_mice_total: 0,
            dead_mice_starved: 0,
            dead_mice_eaten: 0,
            dead_mice_old_age: 0,
            dead_owls_old_age: 0,
        }
    }

    pub fn init_grass(&mut self) {
        self.grass.clear();
        for x in 0..=self.width {
            for y in 0..=self.height {
                let pos = (x, y);
                if !self.mice.iter().any(|a| a.location == pos)
                    && !self.owls.iter().any(|a| a.location == pos)
                {
                    self.grass.insert(pos);
                }
            }
        }
    }

    pub fn add_mouse(&mut self, mouse: Mouse) {
        self.mice.push(mouse);
    }
    pub fn add_owl(&mut self, owl: Owl) {
        self.owls.push(owl);
    }

    pub fn print(&self) {
        use std::io::{self, Write};
        let mut output = String::new();
        for row in (0..=self.height as usize).rev() {
            for col in 0..=self.width as usize {
                let pos = (col as i32, row as i32);
                if let Some(a) = self.mice.iter().find(|a| a.location == pos) {
                    output.push_str(a.symbol());
                } else if let Some(a) = self.owls.iter().find(|a| a.location == pos) {
                    output.push_str(a.symbol());
                } else if self.grass.contains(&pos) {
                    output.push_str("\x1b[32m-\x1b[0m");
                } else {
                    output.push(' ');
                }
            }
            output.push('\n');
        }

        let mice_count = self.mice.len();
        let owl_count  = self.owls.len();

        let stats = format!(
            "Mice - alive: {mice_count}, starved: {mice_starved}, eaten: {mice_eaten}, old: {mice_old_age}\n\
             Owls - alive: {owl_count}, old: {owls_old_age}\n",
            mice_starved   = self.dead_mice_starved,
            mice_eaten     = self.dead_mice_eaten,
            mice_old_age  = self.dead_mice_old_age,
            owls_old_age  = self.dead_owls_old_age,
        );
        output.push_str(&stats);

        print!("{}", output);
        io::stdout().flush().unwrap();
    }

    /// Return a fresh Vec of all mouse locations.
    pub fn mouse_positions(&self) -> Vec<Position> {
        self.mice.iter().map(|m| m.location).collect()
    }

    pub fn owl_positions(&self) -> HashSet<Position> {
        self.owls.iter().map(|a| a.location).collect()
    }

    /// increment age, then cull any animals past max_age
    pub fn age_and_remove_old(&mut self, max_mouse_age: u32, max_owl_age: u32) {
        // mice
        for m in &mut self.mice { m.age += 1; }
        let before_m = self.mice.len();
        self.mice.retain(|m| m.age < max_mouse_age);
        let removed_m = before_m.saturating_sub(self.mice.len());
        self.dead_mice_total     += removed_m;
        self.dead_mice_old_age   += removed_m;

        // owls
        for o in &mut self.owls { o.age += 1; }
        let before_o = self.owls.len();
        self.owls.retain(|o| o.age < max_owl_age);
        let removed_o = before_o.saturating_sub(self.owls.len());
        self.dead_owls_old_age    += removed_o;
    }

    pub fn apply_moves(&mut self, moves: &[Option<Position>]) {
        let mut occupied_owl_positions: HashSet<Position> = self.owl_positions();
        let mut idx = 0;
        // Mice
        for mouse in &mut self.mice {
            if let Some(target) = moves.get(idx).and_then(|m| *m) {
                let ate = self.grass.remove(&target);
                mouse.location = target;
                if ate {
                    mouse.ticks_since_last_eaten = 0;
                } else {
                    mouse.ticks_since_last_eaten += 1;
                }
            } else {
                // no movement => still counts as starvation
                mouse.ticks_since_last_eaten += 1;
            }
            idx += 1;
        }
        // Owls
        for owl in &mut self.owls {
            if let Some(target) = moves.get(idx).and_then(|m| *m) {
                if !occupied_owl_positions.contains(&target) {
                    owl.location = target;
                    occupied_owl_positions.insert(target);
                }
            }
            idx += 1;
        }
    }

    pub fn remove_caught_mice(&mut self) {
        let owl_positions = self.owl_positions();
        let before = self.mice.len();
        self.mice.retain(|a| !owl_positions.contains(&a.location));
        let after = self.mice.len();
        let killed = before.saturating_sub(after);
        self.dead_mice_total += killed;
        self.dead_mice_eaten += killed;
    }

    pub fn remove_starved_mice(&mut self) {
        let before = self.mice.len();
        self.mice.retain(|a| a.ticks_since_last_eaten < 10);
        let after = self.mice.len();
        let starved = before.saturating_sub(after);
        self.dead_mice_total += starved;
        self.dead_mice_starved += starved;
    }
}
