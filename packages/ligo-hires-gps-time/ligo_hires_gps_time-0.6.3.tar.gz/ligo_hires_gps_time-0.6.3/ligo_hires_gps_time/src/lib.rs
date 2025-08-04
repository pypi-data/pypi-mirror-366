//! There are 2<sup>30</sup> · 5<sup>9</sup> "pips" in one second.  We coin the name "pip" and
//! introduce this novel reoslution here for the first time.
//!
//! This library provides types for tracking time in pips as integer.
//!
//! Because all, or almost all LIGO/VIRGO channels, except for minute trends, have a
//! sample period that is a power of two or ten, this allows exact representation
//! of the time of every sample of every channel
//!
//! The exception is LIGO minute trends which have a sample period of 60 seconds,
//! but these points are also exactly represented.

pub mod units;

#[macro_use]
mod operators;

#[macro_use]
mod duration;
#[macro_use]
mod instant;
#[cfg(feature = "hifitime")]
mod hifitime;

pub use units::{PipInstant, PipDuration, ThumpInstant, ThumpDuration};

/// python feature only
#[macro_use]
mod python;

#[cfg(feature = "python")]
pyo3_stub_gen::define_stub_info_gatherer!(stub_info);




