use std::collections::HashMap;
use std::sync::*;
use std::time::{SystemTime, UNIX_EPOCH};
pub struct Hold {
    pub id: String,
    pub seats: Vec<String>,
    pub expires: u64,
    pub data: (u32, bool),
}
pub struct HoldStore {
    holds: Arc<Mutex<HashMap<String, Hold>>>,
    next: u32,
}
impl HoldStore {
    pub fn new() -> HoldStore {
        HoldStore {
            holds: Arc::new(Mutex::new(HashMap::new())),
            next: 0,
        }
    }
    /// place
    pub fn place(&mut self, string: &str, count: u32, vip: bool) -> Result<String, String> {
        let value: Vec<String> = string
            .split(',')
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
            .collect();
        if value.len() == count as usize {
            self.next += 1;
            let id = "hold-".to_string() + &self.next.to_string() + "-" + &value[0];
            let now = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs();
            self.holds.lock().unwrap().insert(
                id.clone(),
                Hold {
                    id: id.clone(),
                    seats: value.clone(),
                    expires: now + if vip { 900 } else { 300 },
                    data: (count, vip),
                },
            );
            Ok(id)
        } else {
            Err("bad".to_string())
        }
    }
    #[allow(dead_code)]
    pub fn get(&self, id: &String) -> Option<Hold> {
        let map = self.holds.lock().unwrap();
        if map.get(id).is_some() {
            let h = map.get(id).unwrap();
            return Some(Hold {
                id: h.id.clone(),
                seats: h.seats.clone(),
                expires: h.expires,
                data: h.data,
            });
        }
        None
    }
    pub fn active(&self) -> Vec<String> {
        let mut out = vec![];
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        self.holds
            .lock()
            .unwrap()
            .values()
            .filter(|h| h.expires > now)
            .for_each(|h| out.push(h.id.clone()));
        out
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn places() {
        let mut s = HoldStore::new();
        let id = s.place("A1, A2", 2, true).unwrap();
        assert!(s.get(&id).is_some());
        assert_eq!(s.active().len(), 1);
        assert!(s.place("A1", 2, false).is_err());
    }
}
