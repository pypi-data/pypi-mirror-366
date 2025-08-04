#![cfg(feature = "python")]
use pyo3::{pymodule, Bound, PyResult};
use pyo3::types::{PyModule, PyModuleMethods};
use crate::{PipDuration, PipInstant, ThumpDuration, ThumpInstant};

#[pymodule]
fn ligo_hires_gps_time(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_class::<PipInstant>()?;
    m.add_class::<PipDuration>()?;
    m.add_class::<ThumpInstant>()?;
    m.add_class::<ThumpDuration>()?;
    Ok(())
}

macro_rules! implement_pyunit {
    ($instant:ident, $duration:ident) => {
        #[gen_stub_pymethods]
        #[pymethods]
        impl $instant {
            fn __add__(&self, other: $duration) -> Self {
                self + other
            }

            /// Subtract a duration to get an instant,
            /// or subtract a instant to get the difference as a duration.
            fn __sub__(&self, py: Python<'_>, other: PyObject) -> PyResult<PyObject>
            {
                if let Ok(r) = other.extract::<$duration>(py) {
                    (self - r).into_pyobject(py).map(|x| x.into())
                } else if let Ok(r) = other.extract::<$instant>(py) {
                    (self - r).into_pyobject(py).map(|x| x.into())
                }
                else {
                    panic!("Got unexpected type in instant subtraction")
                }
            }
        }
    

        #[gen_stub_pymethods]
        #[pymethods]
        impl $duration {
            fn __sub__(&self, other: $duration) -> Self {
                self - other
            }
        
            /// Add a duration to get a combined duration
            /// or Add a instant to get a new instant
            fn __add__(&self, py: Python<'_>, other: PyObject) -> PyResult<PyObject>
            {
                if let Ok(r) = other.extract::<$duration>(py) {
                    (self + r).into_pyobject(py).map(|x| x.into())
                } else if let Ok(r) = other.extract::<$instant>(py) {
                    (self + r).into_pyobject(py).map(|x| x.into())
                }
                else {
                    Err(PyTypeError::new_err("Got unexpected type in duration addition"))
                }
            }
        
            /// Multiply by a number to get a scaled duration
            fn __mul__(&self, py: Python<'_>, other: PyObject) -> PyResult<PyObject>
            {
                if let Ok(r) = other.extract::<f64>(py) {
                    (self * r).into_pyobject(py).map(|x| x.into())
                }
                else if let Ok(r) = other.extract::<u64>(py) {
                    (self * r).into_pyobject(py).map(|x| x.into())
                }
                else if let Ok(r) = other.extract::<i64>(py) {
                    (self * r).into_pyobject(py).map(|x| x.into())
                }
                else {
                    Err(PyTypeError::new_err("Got unexpected type in duration multiplication"))
                }
            }

            fn __rmul__(&self, py: Python<'_>, other: PyObject) -> PyResult<PyObject>
            {
                self.__mul__(py, other)
            }
        
            /// Divide by a float or number to get a scaled duration
            /// Divide by a duration to get a ratio.
            fn __truediv__(&self, py: Python<'_>, other: PyObject) -> PyResult<PyObject>
            {
                if let Ok(r) = other.extract::<f64>(py) {
                    (self / r).into_pyobject(py).map(|x| x.into())
                }
                else if let Ok(r) = other.extract::<usize>(py) {
                    (self / r as f64).into_pyobject(py).map(|x| x.into())
                }
                else if let Ok(r) = other.extract::<u64>(py) {
                    (self / r as f64).into_pyobject(py).map(|x| x.into())
                }
                else if let Ok(r) = other.extract::<i64>(py) {
                    (self / r as f64).into_pyobject(py).map(|x| x.into())
                }
                else if let Ok(r) = other.extract::<$duration>(py) {
                    Ok((self.to_seconds() / r.to_seconds() as f64).into_pyobject(py).unwrap().into())
                }
                else {
                    Err(PyTypeError::new_err("Got unexpected type in duration true division"))
                }
            }
        
            /// Divide by a float or number to get a scaled duration
            /// Divide by a duration to get a ratio
            fn __floordiv__(&self, py: Python<'_>, other: PyObject) -> PyResult<PyObject>
            {
        
                if let Ok(r) = other.extract::<u64>(py) {
                    (self / r).into_pyobject(py).map(|x| x.into())
                }
                else if let Ok(r) = other.extract::<i64>(py) {
                    (self / r).into_pyobject(py).map(|x| x.into())
                }
                else if let Ok(r) = other.extract::<$duration>(py) {
                    Ok((self / r).into_pyobject(py).unwrap().into())
                }
                else {
                    Err(PyTypeError::new_err("Got unexpected type in duration integer division"))
                }
            }
        
            /// Get the remainder from an equivalent integer division
            fn __mod__(&self, py: Python<'_>, other: PyObject) -> PyResult<PyObject>
            {
                if let Ok(r) = other.extract::<f64>(py) {
                    (self % r).into_pyobject(py).map(|x| x.into())
                }
                else if let Ok(r) = other.extract::<u64>(py) {
                    (self % r).into_pyobject(py).map(|x| x.into())
                }
                else if let Ok(r) = other.extract::<i64>(py) {
                    (self % r).into_pyobject(py).map(|x| x.into())
                }
                else if let Ok(r) = other.extract::<$duration>(py) {
                    (self % r).into_pyobject(py).map(|x| x.into())
                }
                else {
                    Err(PyTypeError::new_err("Got unexpected type in duration modulus"))
                }
            }

            fn __neg__(&self, py: Python<'_>) -> PyResult<PyObject>
            {
                Ok((-self).into_pyobject(py).unwrap().into())
            }

            fn __pos__(&self, py: Python<'_>) -> PyResult<PyObject>
            {
                Ok(self.clone().into_pyobject(py).unwrap().into())
            }

            fn __abs__(&self, py: Python<'_>) -> PyResult<PyObject>
            {
                if self.ticks < 0 {
                    Ok((-self).into_pyobject(py).unwrap().into())
                } else {
                    Ok(self.clone().into_pyobject(py).unwrap().into())
                }

            }
        }
        
    }
}

pub (super) use implement_pyunit;
