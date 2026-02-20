use pyo3::prelude::*;

mod enums;
mod errors;
mod geometry;
mod layout;
mod node;
mod style;
mod tree;
mod values;

#[pymodule]
fn _waxy(m: &Bound<'_, PyModule>) -> PyResult<()> {
    errors::register(m)?;
    geometry::register(m)?;
    values::register(m)?;
    enums::register(m)?;
    style::register(m)?;
    node::register(m)?;
    layout::register(m)?;
    tree::register(m)?;
    Ok(())
}
