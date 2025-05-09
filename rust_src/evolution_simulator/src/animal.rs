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
    pub age: u32,
}

#[derive(Clone)]
pub struct Owl {
    pub id: String,
    pub location: (i32, i32),
    pub ticks_since_last_eaten: u32,
    pub sex: Sex,
    pub age: u32,
}

impl Mouse {
    pub fn new(id: String, location: (i32, i32), sex: Sex) -> Self {
        Mouse { id, location, ticks_since_last_eaten: 0, sex, age: 0 }
    }
    pub fn symbol(&self) -> &str {
        match self.sex {
            Sex::Female => "\x1b[35mM\x1b[0m",
            Sex::Male => "\x1b[34mM\x1b[0m",
        }
    }
}

/// Compute the next move for a mouse.
fn next_mouse_move(
    idx: usize,
    board: &Board,
    mice_cfg: &MiceConfig,
    pregnancies: &Vec<(String,u32)>,
) -> Option<Position> {
    let (w, h) = (board.width, board.height);
    let current_location = board.mice[idx].location;
    let vision = mice_cfg.vision as i32;
    
    // new hunger check
    let hunger = board.mice[idx].ticks_since_last_eaten as i32;
    let threshold = mice_cfg.hunger_priority as i32;
    if hunger > threshold {
        // seek nearest grass within vision
        let grass_targets: Vec<_> = board.grass.iter()
        .filter(|&&(gx, gy)| {
            let d = (gx - current_location.0).abs()
            + (gy - current_location.1).abs();
            d <= vision
        })
        .map(|&pos| {
            let d = (pos.0 - current_location.0).abs()
            + (pos.1 - current_location.1).abs();
            (pos, d)
        })
        .collect();
        if grass_targets.is_empty() {
            return None;
        }
        let &(target_pos, dist) = grass_targets.iter().min_by_key(|(_, d)| *d).unwrap();
        if dist == 0 {
            return None;
        }
        let dx = (target_pos.0 - current_location.0).signum();
        let dy = (target_pos.1 - current_location.1).signum();
        let next = ((current_location.0 + dx).clamp(0, w),
        (current_location.1 + dy).clamp(0, h));
        let occupied = board.mice.iter().enumerate().any(|(j, a)| {
            j != idx && a.location == next
        });
        return if !occupied { Some(next) } else { None };
    }
    
    let my_sex = board.mice[idx].sex;
    // build set of pregnant IDs
    let pregnant_ids = pregnancies.iter().map(|(id,_)| id).collect::<Vec<_>>();
    // females do NOT seek; males seek only non-pregnant females
    let others: Vec<_> = if my_sex == Sex::Male {
        board.mice.iter()
        .enumerate()
        .filter(|(j, a)| *j != idx
        && a.sex == Sex::Female
        && !pregnant_ids.contains(&&a.id))
        .filter_map(|(_, a)| {
            let dist = (a.location.0 - current_location.0).abs()
            + (a.location.1 - current_location.1).abs();
            if dist <= vision { Some((a.location, dist)) } else { None }
        })
        .collect()
    } else {
        Vec::new()
    };
    
    if others.is_empty() {
        // seek nearest grass within vision
        let grass_targets: Vec<_> = board.grass.iter()
        .filter(|&&(gx, gy)| {
            let dist = (gx - current_location.0).abs()
            + (gy - current_location.1).abs();
            dist <= vision
        })
        .map(|&pos| {
            let dist = (pos.0 - current_location.0).abs()
            + (pos.1 - current_location.1).abs();
            (pos, dist)
        })
        .collect();
        if grass_targets.is_empty() {
            // no grass or partners in vision => random move
            let dirs = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1),
            ];
            let mut candidates: Vec<Position> = dirs
            .iter()
            .map(|&(dx, dy)| (current_location.0 + dx, current_location.1 + dy))
            .filter(|&(x, y)| x >= 0 && x <= w && y >= 0 && y <= h)
            .filter(|&pos| {
                !board.mice.iter().any(|a| a.location == pos)
            })
            .collect();
            return if candidates.is_empty() {
                None
            } else {
                let mut r = rng();            // use nondeprecated rng()
                Some(*candidates.choose(&mut r).unwrap())
            };
        } else {
            let &(target_pos, dist) = grass_targets.iter()
            .min_by_key(|(_, d)| *d)
            .unwrap();
            if dist == 0 {
                return None;
            }
            let dx = (target_pos.0 - current_location.0).signum();
            let dy = (target_pos.1 - current_location.1).signum();
            let next = (
                (current_location.0 + dx).clamp(0, w),
                (current_location.1 + dy).clamp(0, h),
            );
            let occupied = board.mice.iter().enumerate().any(|(j, a)| {
                j != idx && a.location == next
            });
            return if !occupied { Some(next) } else { None };
        }
    }
    
    let &(target_pos, dist) = others.iter().min_by_key(|(_, d)| *d).unwrap();
    
    if dist == 1 {
        return None;
    }
    
    let dx = (target_pos.0 - current_location.0).signum();
    let dy = (target_pos.1 - current_location.1).signum();
    let next = ((current_location.0 + dx).clamp(0, w), (current_location.1 + dy).clamp(0, h));
    
    let occupied = board.mice.iter().enumerate().any(|(j, a)| {
        j != idx && a.location == next
    });
    if !occupied {
        Some(next)
    } else {
        None
    }
}


impl Owl {
    pub fn new(id: String, location: (i32, i32), sex: Sex) -> Self {
        Owl { id, location, ticks_since_last_eaten: 0, sex, age: 0 }
    }
    pub fn symbol(&self) -> &str {
        "\x1b[31mO\x1b[0m"
    }
}


/// Compute the next move for an owl.
/// If the direct path is blocked by another owl, try a random adjacent unoccupied tile.
fn next_owl_move(
    idx: usize,
    board: &Board,
    all_mice: &[Position],
    rng: &mut rand::prelude::ThreadRng,
) -> Option<Position> {
    let (w, h) = (board.width, board.height);
    let current_location = board.owls[idx].location;
    if let Some(&(mx, my)) = all_mice.iter().min_by_key(|&&(mx, my)| {
        let (ax, ay) = current_location;
        (mx - ax).abs() + (my - ay).abs()
    }) {
        let (ax, ay) = current_location;
        let dx = (mx - ax).signum();
        let dy = (my - ay).signum();
        let target = ((ax + dx).clamp(0, w), (ay + dy).clamp(0, h));
        let occupied = board.owls.iter().enumerate().any(|(j, a)| {
            j != idx && a.location == target
        });
        if !occupied {
            Some(target)
        } else {
            // Try a random adjacent unoccupied tile (including diagonals)
            let mut candidates = vec![
            (ax + 1, ay), (ax - 1, ay), (ax, ay + 1), (ax, ay - 1),
            (ax + 1, ay + 1), (ax - 1, ay - 1), (ax + 1, ay - 1), (ax - 1, ay + 1)
            ];
            candidates.retain(|&(x, y)| x >= 0 && x <= w && y >= 0 && y <= h);
            candidates.retain(|&pos| !board.owls.iter().any(|a| a.location == pos));
            if let Some(choice) = candidates.choose(rng) {
                Some(*choice)
            } else {
                None
            }
        }
    } else {
        None
    }
}

