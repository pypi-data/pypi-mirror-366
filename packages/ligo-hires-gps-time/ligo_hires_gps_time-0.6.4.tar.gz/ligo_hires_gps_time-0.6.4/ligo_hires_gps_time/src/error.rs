use thiserror::Error;


#[derive(Error, Debug, Clone)]
pub enum Error {
    #[cfg(feature = "hifitime")]
    #[error("Could not initialize system time")]
    SystemTimeInitError,
}

#[cfg(feature = "python")]
impl From<Error> for pyo3::PyErr {
    fn from(value: Error) -> Self {
        pyo3::exceptions::PyRuntimeError::new_err(value.to_string())
    }
}