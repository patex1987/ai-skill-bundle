mod holds;

fn main() {
    let mut store = holds::HoldStore::new();
    let id = store.place("A1,A2", 3, false).expect("demo input is valid");
    println!("{id} {}", store.active().len());
}
