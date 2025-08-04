//! Conversions to and from hifitime types

use hifitime::Epoch;
use crate::units::PipInstant;

impl From<PipInstant> for Epoch {
    fn from(value: PipInstant) -> Self {
        let (seconds, nano) = value.to_gpst_seconds_nanoseconds();
        hifitime::Epoch::from_gpst_nanoseconds((seconds as u64)*1_000_000_000 + nano)
    }
}