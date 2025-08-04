//! Python modules
#![cfg(any(feature = "python-pipe", feature = "python"))]

use crate::errors::DTTError;

pub mod dttlib;
pub mod dtt_types;

#[cfg(feature = "python-pipe")]
use dtt_types::dtt_types_init;

pub (crate) fn python_init() -> Result<(), DTTError> {
    #[cfg(feature = "python-pipe")]
    {
        dtt_types_init()?;
        pyo3::prepare_freethreaded_python();
    }
    Ok(())
}

