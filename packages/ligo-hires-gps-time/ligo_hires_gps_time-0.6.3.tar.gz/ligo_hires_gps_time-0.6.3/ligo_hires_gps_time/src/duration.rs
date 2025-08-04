

macro_rules! duration {
    ($struct:ident, $unit:ident, $rate:expr, $ticks:ident, $instant:ident, $to_unit:ident, $from_unit:ident)  => {
        #[cfg_attr(feature = "python", gen_stub_pyclass)]
        #[cfg_attr(feature = "python", pyclass(frozen, eq, ord))]
        #[derive(Debug, Clone, Copy, Default, serde::Serialize, serde::Deserialize)]
        pub struct $struct {
            pub (crate) ticks: $ticks,
        }

        impl Hash for $struct {
            fn hash<H: Hasher>(&self, state: &mut H) {
                self.ticks.hash(state);
            }
        }

        /// # formatting functions
        impl Display for $struct {
            fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
                write!(f, "{}", self.ticks)
            }
        }

        /// # Relational operators
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
            fn cmp(&self, other: &Self) -> Ordering {
                self.ticks.cmp(&other.ticks)
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

            /// Convert a frequency as Hz into a duration that represents the corresponding period.
            #[staticmethod]
            pub fn freq_hz_to_period(rate_hz: f64) -> Self {
                Self::from_seconds(1.0 / rate_hz)
            }

            /// Convert a duration that represents a period into the corresponding frequency as Hz.
            pub fn period_to_freq_hz(&self) -> f64 {
                1.0/self.to_seconds()
            }

            /// Create a duration given the length in seconds.
            #[staticmethod]
            pub fn from_seconds(seconds: f64) -> Self {
                Self {
                    ticks: $ticks::from_f64((seconds * $rate as f64).round()).unwrap_or(0)
                }
            }

            /// Return the length of the duration as seconds.
            pub fn to_seconds(&self) -> f64 {

                (self.ticks as f64) / $rate as f64
            }

            /// Create a duration given the length in seconds.
            #[staticmethod]
            pub const fn from_sec(seconds: i64) -> Self {
                Self {
                    ticks: seconds as $ticks * $rate,
                }
            }

            /// Round the duration to the nearest second.
            ///
            /// Return 0 for negative durations.
            pub const fn to_sec(&self) -> i64 {
                let(sec, nano) = self.to_seconds_nanoseconds();
                if nano >= 500_000_000 {
                    sec + 1
                } else {
                    sec
                }
            }

            /// Create a duration given the length in nanoseconds.
            #[staticmethod]
            pub const fn from_nanoseconds(nanoseconds: u64) -> Self {
                Self {
                    ticks: ((nanoseconds as $ticks * $rate + 500_000_000) / 1_000_000_000 as $ticks) as $ticks,
                }
            }

            /// Return the length to the nearest nanosecond,
            /// but return zero if the duration is negative.
            pub const fn to_nanoseconds(&self) -> u64 {
                let(sec, nano) = self.to_seconds_nanoseconds();
                sec as u64 * 1_000_000_000 + nano as u64
            }

            /// Return the length as seconds and nanoseconds
            pub const fn to_seconds_nanoseconds(&self) -> (i64, u64) {
                let seconds = (self.ticks / $rate ) as i64;
                let nano = (((self.ticks % $rate ) * 1_000_000_000 + $rate/2)  / $rate ) as u64;
                (seconds, nano)
            }

            /// Create  a duration object from a numerical value of the same units.
            #[staticmethod]
            pub const fn $from_unit ($unit :$ticks) -> Self {
                Self {
                    ticks: $unit,
                }
            }

            /// Create a duration given the length as seconds and nanoseconds
            #[staticmethod]
            pub const fn from_seconds_nanoseconds(seconds: i64, nano: u64) -> Self {
                Self {
                    ticks: (seconds as $ticks * $rate) + ((nano as i128 * $rate as i128+ 500_000_000) / 1_000_000_000) as $ticks
                }
            }

            /// Return duration in units of the type..
            pub const fn $to_unit (&self) -> $ticks {
                self.ticks
            }


            /// True if the length of the duration is zero.
            pub const fn is_empty(&self) -> bool {
                self.ticks == 0
            }

            /// Return a non-negative duration of the same magnitude.
            pub const fn abs(&self) -> Self {
                Self{ticks: self.ticks.abs()}
            }

            /// Snap to the nearest integer multiple of a step size.
            pub fn snap_to_step(&self, step: &Self) -> Self {
                Self{ ticks: _snap_to_step(self.ticks, step.ticks) }
            }

            /// Snap to the largest integer <= self that's a multiple of a step size.
            ///
            /// Like snap_to_step, but takes the floor rather than the nearest.
            pub fn snap_down_to_step(&self, step: &Self) -> Self {
                Self{ ticks: _snap_down_to_step(self.ticks, step.ticks) }
            }

            /// Snap to the smallest integer >= self that's a multiple of a step size.
            ///
            /// Like snap_to_step, but takes the ceiling rather than the nearest.
            pub fn snap_up_to_step(&self, step: &Self) -> Self {
                Self{ ticks: _snap_up_to_step(self.ticks, step.ticks) }
            }

            /// Return the rate of the units in Hz
            #[staticmethod]
            pub fn rate_hz() -> $ticks {
                $rate
            }
        }
    }
}

pub (super) use duration;