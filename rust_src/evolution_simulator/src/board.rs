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
        let owl_count = self.owls.len();
        output.push_str(&format!(
            "Mice: {}  Owls: {}  Dead mice: {} (starved: {}, eaten: {})\n",
            mice_count,
            owl_count,
            self.dead_mice_total,
            self.dead_mice_starved,
            self.dead_mice_eaten
        ));
        print!("{}", output);
        io::stdout().flush().unwrap();
    }

    pub fn mouse_positions(&self) -> &[Position] {
        // SAFETY: All mice always have a location.
        // This returns a slice of positions for all mice.
        unsafe {
            std::slice::from_raw_parts(self.mice.as_ptr() as *const Position, self.mice.len())
        }
    }

    pub fn owl_positions(&self) -> HashSet<Position> {
        self.owls.iter().map(|a| a.location).collect()
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::animal::{Mouse, Owl, Sex};

    #[test]
    fn test_add_animal_and_grass() {
        let mut board = Board::new(2, 2);
        let m = Mouse::new("M1".to_string(), 0, 5, None, None, (1, 1), Sex::Female);
        board.add_mouse(m);
        board.init_grass();
        assert!(board.grass.contains(&(0, 0)));
        assert!(!board.grass.contains(&(1, 1))); // occupied by mouse
    }

    #[test]
    fn test_remove_caught_and_starved_mice() {
        let mut board = Board::new(2, 2);
        let m1 = Mouse::new("M1".to_string(), 0, 5, None, None, (1, 1), Sex::Female);
        let m2 = Mouse::new("M2".to_string(), 0, 5, None, None, (2, 2), Sex::Male);
        let o = Owl::new("O1".to_string(), 0, 10, None, None, (1, 1), Sex::Male);
        board.add_mouse(m1);
        board.add_mouse(m2);
        board.add_owl(o);
        board.init_grass();

        board.remove_caught_mice();
        assert_eq!(board.mice.len(), 1);
        assert_eq!(board.dead_mice_total, 1);

        // starve the remaining mouse
        if let Some(mouse) = board.mice.iter_mut().next() {
            mouse.ticks_since_last_eaten = 10;
        }
        board.remove_starved_mice();
        assert_eq!(board.mice.len(), 0);
        assert_eq!(board.dead_mice_total, 2);
    }
}
