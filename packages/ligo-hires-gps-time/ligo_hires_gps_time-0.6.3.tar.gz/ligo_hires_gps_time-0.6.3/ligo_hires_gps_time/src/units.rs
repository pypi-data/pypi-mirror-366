use std::cmp::Ordering;
use std::fmt::{Display, Formatter};
use std::hash::{Hash, Hasher};
use std::ops::{Add, AddAssign, Div, Mul, Neg, Sub, SubAssign, Rem};
use std::borrow::Borrow;
use num_traits::{FromPrimitive};

#[cfg(feature = "python")]
use pyo3::{
    pyclass, pymethods
};

#[cfg(feature = "python")]
use pyo3_stub_gen::{
    derive::{
        gen_stub_pyclass,
        gen_stub_pymethods,
    }
};
#[cfg(feature = "python")]
use pyo3::{
    PyObject,PyResult,
    Python,IntoPyObject,
    exceptions::{PyTypeError},
};
#[cfg(feature = "python")]
use crate::python::implement_pyunit;
#[cfg(not (feature = "python"))]
use ligo_hires_gps_time_macros::{
    staticmethod
};

use ligo_hires_gps_time_macros::define_unit;
use crate::instant::{ instant, _snap_to_step, _snap_up_to_step, _snap_down_to_step};
use crate::duration::duration;
use crate::operators::{operators};
use crate::operators::IntFactors;


/// 2^30 * 5^9, handles every power of 2 and 10 up to (and slightly above!) 1 billion.
const PIPS_PER_SEC: i128 = (1<<30)*5*5*5*5*5*5*5*5*5;
const THUMPS_PER_SEC: i64 = (1<<19)*5*5*5*5*5;
//const PIPS_PER_NANOSECOND: i128 = PIPS_PER_SEC / 1_000_000_000;


macro_rules! unit_conversion {
    ($rate_a: expr, $type_a: ident,
     $rate_b: expr, $type_b: ident, $tick_b: ident,
     $to_name: ident
    ) => {

        impl From<&$type_a> for $type_b {
            fn from(a: &$type_a) -> Self {
                $type_b{ticks: ((a.ticks as i128 * $rate_b as i128 + $rate_a as i128/ 2) / $rate_a as i128) as $tick_b}
            }
        }

        impl From<$type_a> for $type_b {
            fn from(a: $type_a) -> Self {
                let ref a_ref = a;
                a_ref.into()
            }
        }

        #[cfg_attr(feature = "python", pymethods)]
        impl $type_a {
            /// Return a nearest equavalent time value of the given type.
            pub fn $to_name(&self) -> $type_b {
                self.into()
            }
        }
    }
}


define_unit!(
    // Defines PipInstant and PipDuration
    Pip, PIPS_PER_SEC, i128,

    // Defines ThumpInstant and ThumpDuration
    Thump, THUMPS_PER_SEC, i64,
);



#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn duration_division() {
        let p1 = PipDuration{ticks: 1000};
        let p2 = PipDuration{ticks: 999};
        let p3 = PipDuration{ticks: -1000};

        assert_eq!((p1%p1).to_pips(), 0);
        assert_eq!((p1%p2).to_pips(), 1);
        assert_eq!((p3%p2).to_pips(), -1);
        assert_eq!((p2%p1).to_pips(), 999);
        assert_eq!((p2%p3).to_pips(), 999);

        assert_eq!(p1/p1, 1);
        assert_eq!(p1/p2, 1);
        assert_eq!(p1/p3, -1);
        assert_eq!(p2/p1, 0);
        assert_eq!(p2/p3, 0);

        assert_eq!(p1%999.0, PipDuration{ticks: 1});
        assert_eq!(p1/999.0, PipDuration{ticks: 1});
        assert_eq!(p3%999.0, PipDuration{ticks: -1});
    }

    #[test]
    fn snap() {
        let d1 = PipDuration{ticks: 1000};
        let d2 = PipDuration{ticks: 999};
        let d3 = PipDuration{ticks: 998};
        let step = PipDuration{ticks: 111};

        assert_eq!(d1.snap_to_step(&step), d2);
        assert_eq!(d2.snap_to_step(&step), d2);
        assert_eq!(d3.snap_to_step(&step), d2);

        assert_eq!(d1.snap_up_to_step(&step), PipDuration{ticks: 1110});
        assert_eq!(d2.snap_up_to_step(&step), d2);
        assert_eq!(d3.snap_up_to_step(&step), d2);

        assert_eq!(d1.snap_down_to_step(&step), d2);
        assert_eq!(d2.snap_down_to_step(&step), d2);
        assert_eq!(d3.snap_down_to_step(&step), PipDuration{ticks: 888});

        let d1 = PipInstant{ticks: 1000};
        let d2 = PipInstant{ticks: 999};
        let d3 = PipInstant{ticks: 998};

        assert_eq!(d1.snap_to_step(&step), d2);
        assert_eq!(d2.snap_to_step(&step), d2);
        assert_eq!(d3.snap_to_step(&step), d2);

        assert_eq!(d1.snap_up_to_step(&step), PipInstant{ticks: 1110});
        assert_eq!(d2.snap_up_to_step(&step), d2);
        assert_eq!(d3.snap_up_to_step(&step), d2);

        assert_eq!(d1.snap_down_to_step(&step), d2);
        assert_eq!(d2.snap_down_to_step(&step), d2);
        assert_eq!(d3.snap_down_to_step(&step), PipInstant{ticks: 888});
    }

    #[test]
    fn abs() {
        assert_eq!(PipDuration{ticks: -1000}.abs(), PipDuration{ticks: 1000});
        assert_eq!(PipDuration{ticks: 1000}.abs(), PipDuration{ticks: 1000});
        assert_eq!(PipDuration{ticks: 0}.abs(), PipDuration{ticks: 0});
    }

    #[test]
    fn empty() {
        assert!(PipDuration{ticks: 0}.is_empty());
        assert!(!PipDuration{ticks: 1}.is_empty());
        assert!(!PipDuration{ticks: -1}.is_empty());
    }

    #[test]
    fn equality() {
        let d1 = PipInstant{ticks: 1000};
        let d2 = PipInstant{ticks: 999};
        assert_eq!(d1, d1);
        assert_ne!(d1, d2);
        assert!(d1 > d2);
        assert!(d1 >= d2);
        assert!(d2 < d1);
        assert!(d2 <= d1);
    }

    #[test]
    fn duration_division_thump() {
        let p1 = ThumpDuration{ticks: 1000};
        let p2 = ThumpDuration{ticks: 999};
        let p3 = ThumpDuration{ticks: -1000};

        assert_eq!((p1%p1).to_thumps(), 0);
        assert_eq!((p1%p2).to_thumps(), 1);
        assert_eq!((p3%p2).to_thumps(), -1);
        assert_eq!((p2%p1).to_thumps(), 999);
        assert_eq!((p2%p3).to_thumps(), 999);

        assert_eq!(p1/p1, 1);
        assert_eq!(p1/p2, 1);
        assert_eq!(p1/p3, -1);
        assert_eq!(p2/p1, 0);
        assert_eq!(p2/p3, 0);

        assert_eq!(p1%999.0, ThumpDuration{ticks: 1});
        assert_eq!(p1/999.0, ThumpDuration{ticks: 1});
        assert_eq!(p3%999.0, ThumpDuration{ticks: -1});
    }

    #[test]
    fn snap_thump() {
        let d1 = ThumpDuration{ticks: 1000};
        let d2 = ThumpDuration{ticks: 999};
        let d3 = ThumpDuration{ticks: 998};
        let step = ThumpDuration{ticks: 111};

        assert_eq!(d1.snap_to_step(&step), d2);
        assert_eq!(d2.snap_to_step(&step), d2);
        assert_eq!(d3.snap_to_step(&step), d2);

        assert_eq!(d1.snap_up_to_step(&step), ThumpDuration{ticks: 1110});
        assert_eq!(d2.snap_up_to_step(&step), d2);
        assert_eq!(d3.snap_up_to_step(&step), d2);

        assert_eq!(d1.snap_down_to_step(&step), d2);
        assert_eq!(d2.snap_down_to_step(&step), d2);
        assert_eq!(d3.snap_down_to_step(&step), ThumpDuration{ticks: 888});

        let d1 = ThumpInstant{ticks: 1000};
        let d2 = ThumpInstant{ticks: 999};
        let d3 = ThumpInstant{ticks: 998};

        assert_eq!(d1.snap_to_step(&step), d2);
        assert_eq!(d2.snap_to_step(&step), d2);
        assert_eq!(d3.snap_to_step(&step), d2);

        assert_eq!(d1.snap_up_to_step(&step), ThumpInstant{ticks: 1110});
        assert_eq!(d2.snap_up_to_step(&step), d2);
        assert_eq!(d3.snap_up_to_step(&step), d2);

        assert_eq!(d1.snap_down_to_step(&step), d2);
        assert_eq!(d2.snap_down_to_step(&step), d2);
        assert_eq!(d3.snap_down_to_step(&step), ThumpInstant{ticks: 888});
    }

    #[test]
    fn abs_thump() {
        assert_eq!(ThumpDuration{ticks: -1000}.abs(), ThumpDuration{ticks: 1000});
        assert_eq!(ThumpDuration{ticks: 1000}.abs(), ThumpDuration{ticks: 1000});
        assert_eq!(ThumpDuration{ticks: 0}.abs(), ThumpDuration{ticks: 0});
    }

    #[test]
    fn empty_thump() {
        assert!(ThumpDuration{ticks: 0}.is_empty());
        assert!(!ThumpDuration{ticks: 1}.is_empty());
        assert!(!ThumpDuration{ticks: -1}.is_empty());
    }

    #[test]
    fn equality_thump() {
        let d1 = ThumpInstant{ticks: 1000};
        let d2 = ThumpInstant{ticks: 999};
        assert_eq!(d1, d1);
        assert_ne!(d1, d2);
        assert!(d1 > d2);
        assert!(d1 >= d2);
        assert!(d2 < d1);
        assert!(d2 <= d1);
    }

    #[test]
    fn thump_pip_duration_conversion() {
        let d1 = ThumpDuration{ticks: 1};
        let d2: PipDuration = d1.into();
        assert_eq!(d2.ticks, 1_280_000);
    }

    #[test]
    fn thump_pip_instant_conversion() {
        let d1 = ThumpInstant{ticks: 1};
        let d2: PipInstant = d1.into();
        assert_eq!(d2.ticks, 1_280_000);
    }

    #[test]
    fn pip_thump_duration_conversion() {
        let d1 = PipDuration{ticks: 1_280_000};
        let d2: ThumpDuration = d1.into();
        assert_eq!(d2.ticks, 1);
        let d1 = PipDuration{ticks: 640_000};
        let d2: ThumpDuration = d1.into();
        assert_eq!(d2.ticks, 1);
        let d1 = PipDuration{ticks: 640_000 - 1};
        let d2: ThumpDuration = d1.into();
        assert_eq!(d2.ticks, 0);
    }

    #[test]
    fn pip_thump_instant_conversion() {
        let d1 = PipInstant{ticks: 1_280_000};
        let d2: ThumpInstant = d1.into();
        assert_eq!(d2.ticks, 1);
        let d1 = PipInstant{ticks: 640_000};
        let d2: ThumpInstant = d1.into();
        assert_eq!(d2.ticks, 1);
        let d1 = PipInstant{ticks: 640_000 - 1};
        let d2: ThumpInstant = d1.into();
        assert_eq!(d2.ticks, 0);
    }
}