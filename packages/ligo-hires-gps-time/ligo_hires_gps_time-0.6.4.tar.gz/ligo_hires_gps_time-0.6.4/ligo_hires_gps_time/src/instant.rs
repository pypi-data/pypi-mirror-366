/// Arguments are
/// 1. Name for the struct, e.g. `PipInstant`
/// 2. Unit name, lowercase, e.g. `pips`,
/// 3. Rate in ticks per second,
/// 4. and units of ticks.  This is the underlying store in the struct
macro_rules! instant {
    ($struct:ident, $unit:ident, $rate:expr, $ticks:ident, $duration:ident, $to_unit:ident, $from_unit:ident, $to_gpst_unit:ident, $from_gpst_unit:ident)  => {
        #[cfg_attr(feature = "python", pyclass(frozen, eq, ord))]
        #[cfg_attr(feature = "python", gen_stub_pyclass)]
        #[derive(Debug, Clone, Copy, Default, serde::Serialize, serde::Deserialize)]
        pub struct $struct {
            pub (crate) ticks: $ticks,
        }

        impl Hash for $struct {
            fn hash<H: Hasher>(&self, state: &mut H) {
                self.ticks.hash(state);
            }
        }

        impl PartialEq for $struct {
            fn eq(&self, other: &Self) -> bool {
                self.ticks == other.ticks
            }
        }

        impl Eq for $struct {}

        impl PartialOrd for $struct {
            fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
                Some(self.cmp(other))
            }
        }

        impl Ord for $struct {
            fn cmp(&self, other: &Self) -> Ordering {self.ticks.cmp(&other.ticks)}
        }


        impl Display for $struct {
            fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.ticks)
            }
        }

        impl From<$ticks> for $struct {
            fn from(value: $ticks) -> Self {
                Self { ticks: value }
            }
        }

        #[cfg_attr(feature = "python", gen_stub_pymethods)]
        #[cfg_attr(feature = "python", pymethods)]
        impl $struct {

            // # Time unit conversions
            // Most of the conversion functions are defined using the
            // duration conversion functions

            ///  Return the number of steps since the GPS epoch.

            pub fn $to_gpst_unit (&self) -> $ticks {
                self.sub_instant(&Self::gpst_epoch()).$to_unit()
            }


            /// Return the nearest nanosecond since the GPS epoch.
            pub fn to_gpst_seconds_nanoseconds(&self) -> (i64, u64) {
                self.sub_instant(&Self::gpst_epoch()).to_seconds_nanoseconds()
            }

            /// If positive, return nanoseconds since the GPS epoch, otherwise zero.
            pub fn to_gpst_nanoseconds(&self) -> u64 {
                self.sub_instant(&Self::gpst_epoch()).to_nanoseconds()
            }

            /// Return the seconds since GPS epoch rounded down to the latest second
            /// earlier than or coincident with the instant.
            ///
            /// Returns 0 for instants before the GPS epoch.
            pub const fn to_gpst_sec(&self) -> i64 {
                self.sub_instant(&Self::gpst_epoch()).to_sec()
            }

            /// Return the number of seconds since the GPS epoch.
            pub fn to_gpst_seconds(&self) -> f64 {
                self.sub_instant(&Self::gpst_epoch()).to_seconds()
            }

            // # construction

            /// Create an instant given seconds + nanoseconds since the GPS epoch.
            #[staticmethod]
            pub const fn from_gpst_seconds_nanoseconds(seconds: i64, nano: u64) -> Self {
                Self::gpst_epoch().add_duration(&$duration::from_seconds_nanoseconds(seconds, nano))
            }

            /// Create an instant given nanoseconds since the GPS epoch.
            #[staticmethod]
            pub const fn from_gpst_nanoseconds(nano: u64) -> Self {
                Self::gpst_epoch().add_duration(&$duration::from_nanoseconds(nano))
            }

            /// Create an instant given seconds since the GPS epoch.
            #[staticmethod]
            pub fn from_gpst_seconds(seconds: f64) -> Self {
                Self::gpst_epoch().add_duration(&$duration::from_seconds(seconds))
            }

            /// Create an instant at Midnight UTC, Jan 6 1980,
            /// the reference epoch for the GPS time system.
            #[staticmethod]
            pub const fn gpst_epoch() -> Self {
                Self {
                    ticks: 0
                }
            }

            /// Create an instant given whole seconds since the GPS epoch.
            #[staticmethod]
            pub const fn from_gpst_sec(seconds: i64) -> Self {
                Self::gpst_epoch().add_duration(&$duration::from_sec(seconds))
            }

            /// Create an instant given steps since the GPS epoch.
            #[staticmethod]
            pub const fn $from_gpst_unit( $unit : $ticks ) -> Self {
                Self::gpst_epoch().add_duration(&$duration::$from_unit( $unit ))
            }


            /// Snap to the nearest integer multiple of a step size.
            pub fn snap_to_step(&self, step: & $duration ) -> Self {
               Self{ ticks: _snap_to_step(self.ticks, step.ticks) }
            }

            /// Snap to the largest integer <= self that's a multiple of a step size.
            ///
            /// Like snap_to_step, but takes the floor rather than the nearest.
            pub fn snap_down_to_step(&self, step: &$duration) -> Self {
                Self{ ticks: _snap_down_to_step(self.ticks, step.ticks) }
            }

            /// Snap to the smallest integer >= self that's a multiple of a step size.
            ///
            /// Like snap_to_step, but takes the ceiling rather than the nearest.
            pub fn snap_up_to_step(&self, step: &$duration) -> Self {
                Self{ ticks: _snap_up_to_step(self.ticks, step.ticks) }
            }

            /// Return the rate of the units in Hz
            #[staticmethod]
            pub fn rate_hz() -> $ticks {
                $rate
            }
        }

        /// functions not wanted in python go here.
        impl $struct {
            /// const operators
            /// trait impls can't be const
            /// so we need some const operators to get some of the other const functions to work
            pub (crate) const fn sub_instant(&self, rhs: &Self) -> $duration {
                $duration {
                    ticks: self.ticks - rhs.ticks
                }
            }

            pub (crate) const fn add_duration(&self, rhs: &$duration) -> Self {
                Self {
                    ticks: self.ticks + rhs.ticks
                }
            }
        }

        #[cfg(feature = "hifitime")]
        #[cfg_attr(feature = "python", gen_stub_pymethods)]
        #[cfg_attr(feature = "python", pymethods)]
        impl $struct {
            /// return the current time
            #[staticmethod]
            pub fn now() -> Result<Self, crate::error::Error> {
                let now = match hifitime::Epoch::now() {
                    Ok(epoch) => epoch,
                    Err(_) => return Err(crate::error::Error::SystemTimeInitError),
                };
                let now_d = now.to_gpst_duration();
                let nanos = now_d.total_nanoseconds();
                Ok(Self::from_gpst_seconds_nanoseconds((nanos/1_000_000_000) as i64, (nanos%1_000_000_000) as u64))
            }
        }
    }
}

// // sorry, the extra args are needed because pyo3 doesn't let use the paste! macro
// // to build a function name
// // we could fix this by turning this into a proc macro
// macro_rules! gps_unit {
//     ($instant:ident, $duration:ident, $unit:ident, $rate:expr, $ticks:ident, $to_units:ident, $from_units:ident, $to_gpst_units:ident, $from_gpst_units:ident )  => {
//         instant!($instant, $unit, $rate, $ticks, $duration, $to_units, $from_units, $to_gpst_units, $from_gpst_units);
//         duration!($duration, $unit, $rate, $ticks, $instant, $to_units, $from_units);
//         operators!($instant, $duration);
//     }
// }

use num_traits::{AsPrimitive, PrimInt};
pub (super) use instant;

/// Snap to the nearest integer multiple of a step size.
pub (crate) fn _snap_to_step<T>(ticks: T, step: T) -> T
where
    T: PrimInt + 'static,
    i32: AsPrimitive<T>,
{
    if step == 0.as_() {
        ticks
    } else {
        let new_ticks = ticks + step /2.as_();
        new_ticks - (new_ticks % step)
    }
}

/// Snap to the largest integer <= self that's a multiple of a step size.
///
/// Like snap_to_step, but takes the floor rather than the nearest.
pub (crate) fn _snap_down_to_step<T>(ticks: T, step: T) -> T
where
    T: PrimInt + 'static,
    i32: AsPrimitive<T>,
{
    if step == 0.as_() {
        ticks
    } else {
        ticks - (ticks % step)
    }
}

/// Snap to the smallest integer >= self that's a multiple of a step size.
///
/// Like snap_to_step, but takes the ceiling rather than the nearest.
pub (crate) fn _snap_up_to_step<T>(ticks: T, step: T) -> T
where
    T: PrimInt + 'static,
    i32: AsPrimitive<T>,
{
    if step == 0.as_() {
        ticks
    } else {
        let new_ticks = ticks + (step - 1.as_());
        new_ticks - (new_ticks % step)
    }
}

