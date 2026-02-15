use pyo3::prelude::*;

mod dimensions;
mod enums;
mod errors;
mod geometry;
mod grid;
mod helpers;
mod layout;
mod node;
pub mod style;
mod tree;

#[pymodule]
fn _waxy(m: &Bound<'_, PyModule>) -> PyResult<()> {
    errors::register(m)?;
    geometry::register(m)?;
    dimensions::register(m)?;
    enums::register(m)?;
    grid::register(m)?;
    style::register(m)?;
    node::register(m)?;
    layout::register(m)?;
    tree::register(m)?;
    helpers::register(m)?;
    Ok(())
}
