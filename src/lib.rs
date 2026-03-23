use pyo3::prelude::*;
use pyo3::types::PyList;
use rand::{Rng, RngCore, SeedableRng};
use rand_chacha::ChaCha20Rng;
use std::sync::Mutex;

lazy_static::lazy_static! {
    static ref RNG: Mutex<ChaCha20Rng> = Mutex::new(ChaCha20Rng::from_entropy());
}

#[pyfunction]
fn random_float() -> f64 {
    let mut rng = RNG.lock().unwrap();
    let val: u64 = rng.next_u64();
    (val >> 11) as f64 / (1u64 << 53) as f64
}

#[pyfunction]
fn random_array(size: usize) -> Vec<f64> {
    let mut rng = RNG.lock().unwrap();
    // Memory Management: Pre-allocate full capacity to avoid re-allocations
    let mut v = Vec::with_capacity(size);
    for _ in 0..size {
        let val: u64 = rng.next_u64();
        v.push((val >> 11) as f64 / (1u64 << 53) as f64);
    }
    v
}

#[pyfunction]
fn shuffle_list(list: &Bound<'_, PyList>) -> PyResult<()> {
    let mut rng = RNG.lock().unwrap();
    let len = list.len();
    if len < 2 { return Ok(()); }

    // High-performance Fisher-Yates shuffle directly on Python references
    for i in (1..len).rev() {
        let j = rng.gen_range(0..=i);
        if i != j {
            let item_i = list.get_item(i)?;
            let item_j = list.get_item(j)?;
            list.set_item(i, item_j)?;
            list.set_item(j, item_i)?;
        }
    }
    Ok(())
}

#[pymodule]
fn _hyrandom_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(random_float, m)?)?;
    m.add_function(wrap_pyfunction!(random_array, m)?)?;
    m.add_function(wrap_pyfunction!(shuffle_list, m)?)?;
    Ok(())
}