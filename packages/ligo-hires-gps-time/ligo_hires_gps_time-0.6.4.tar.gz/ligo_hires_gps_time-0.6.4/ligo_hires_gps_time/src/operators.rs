macro_rules! operators {
    ($instant:ident, $duration:ident, $ticks:ident) => {
        /// # Arithmetic operators
        /// ## Instant + Duration = Instant
        impl<T> Add<T> for &$instant
        where
            T: Borrow<$duration>,
        {
            type Output = $instant;

            fn add(self, rhs: T) -> Self::Output {
                self.add_duration(rhs.borrow())
            }
        }

        impl<T> Add<T> for $instant
        where
            T: Borrow<$duration>,
        {
            type Output = $instant;

            fn add(self, rhs: T) -> Self::Output {
                &self + rhs
            }
        }

        impl Add<&$instant> for &$duration {
            type Output = $instant;

            fn add(self, rhs: &$instant) -> Self::Output {
                rhs + self
            }
        }

        impl Add<&$instant> for $duration {
            type Output = $instant;

            fn add(self, rhs: &$instant) -> Self::Output {
                rhs + self
            }
        }

        impl Add<$instant> for &$duration {
            type Output = $instant;

            fn add(self, rhs: $instant) -> Self::Output {
                rhs + self
            }
        }

        impl Add<$instant> for $duration {
            type Output = $instant;

            fn add(self, rhs: $instant) -> Self::Output {
                rhs + self
            }
        }

        impl<T: Borrow<$duration>> AddAssign<T> for $instant {
            fn add_assign(&mut self, rhs: T) {
                let s = self.borrow() + rhs;
                self.ticks = s.ticks;
            }
        }

        /// ## Duration + Duration = Duration
        impl Add<&$duration> for &$duration {
            type Output = $duration;

            fn add(self, rhs: &$duration) -> Self::Output {
                Self::Output {
                    ticks: self.ticks + rhs.ticks,
                }
            }
        }

        impl Add<&$duration> for $duration {
            type Output = $duration;

            #[allow(clippy::op_ref)]
            fn add(self, rhs: &$duration) -> Self::Output {
                &self + rhs
            }
        }

        impl Add<$duration> for &$duration {
            type Output = $duration;

            #[allow(clippy::op_ref)]
            fn add(self, rhs: $duration) -> Self::Output {
                self + &rhs
            }
        }

        impl Add<$duration> for $duration {
            type Output = $duration;

            fn add(self, rhs: $duration) -> Self::Output {
                &self + rhs
            }
        }
        impl AddAssign<$duration> for $duration {
            fn add_assign(&mut self, rhs: $duration) {
                let s = &*self + rhs;
                self.ticks = s.ticks;
            }
        }

        impl AddAssign<&$duration> for $duration {
            fn add_assign(&mut self, rhs: &$duration) {
                let s = &*self + rhs;
                self.ticks = s.ticks;
            }
        }

        /// ## Instant - Instant = Duration
        impl Sub<&$instant> for &$instant {
            type Output = $duration;

            fn sub(self, rhs: &$instant) -> Self::Output {
                self.sub_instant(rhs)
            }
        }

        impl Sub<&$instant> for $instant {
            type Output = $duration;

            fn sub(self, rhs: &$instant) -> Self::Output {
                &self - rhs
            }
        }

        impl Sub<$instant> for &$instant {
            type Output = $duration;

            fn sub(self, rhs: $instant) -> Self::Output {
                self - &rhs
            }
        }

        impl Sub<$instant> for $instant {
            type Output = $duration;

            fn sub(self, rhs: $instant) -> Self::Output {
                &self - &rhs
            }
        }

        /// ## Duration - Duration = Instant

        impl Sub<&$duration> for &$duration {
            type Output = $duration;

            fn sub(self, rhs: &$duration) -> Self::Output {
                Self::Output {
                    ticks: self.ticks - rhs.ticks,
                }
            }
        }

        impl Sub<&$duration> for $duration {
            type Output = $duration;

            fn sub(self, rhs: &$duration) -> Self::Output {
                &self - rhs
            }
        }

        impl Sub<$duration> for &$duration {
            type Output = $duration;

            fn sub(self, rhs: $duration) -> Self::Output {
                self - &rhs
            }
        }

        impl Sub<$duration> for $duration {
            type Output = $duration;

            fn sub(self, rhs: $duration) -> Self::Output {
                &self - &rhs
            }
        }

        impl<T: Borrow<$duration>> SubAssign<T> for $duration {
            fn sub_assign(&mut self, rhs: T) {
                let diff = &*self - rhs.borrow();
                self.ticks = diff.ticks;
            }
        }

        /// ## Instant - Duration = Instant
        impl Sub<&$duration> for &$instant {
            type Output = $instant;

            fn sub(self, rhs: &$duration) -> Self::Output {
                Self::Output {
                    ticks: self.ticks - rhs.ticks,
                }
            }
        }

        impl Sub<&$duration> for $instant {
            type Output = $instant;

            fn sub(self, rhs: &$duration) -> Self::Output {
                &self - rhs
            }
        }

        impl Sub<$duration> for &$instant {
            type Output = $instant;

            fn sub(self, rhs: $duration) -> Self::Output {
                self - &rhs
            }
        }

        impl Sub<$duration> for $instant {
            type Output = $instant;

            fn sub(self, rhs: $duration) -> Self::Output {
                &self - &rhs
            }
        }

        impl SubAssign<&$duration> for $instant {
            fn sub_assign(&mut self, rhs: &$duration) {
                let diff: $instant = &*self - rhs;
                self.ticks = diff.ticks;
            }
        }

        impl SubAssign<$duration> for $instant {
            fn sub_assign(&mut self, rhs: $duration) {
                let diff: $instant = &*self - rhs;
                self.ticks = diff.ticks;
            }
        }

        /// ## Duration * C = Duration
        /// ### Numeric types we support for Duration integer multiplication

        impl<T: IntFactors> Mul<T> for &$duration {
            type Output = $duration;

            fn mul(self, rhs: T) -> Self::Output {
                let x = rhs.into();
                Self::Output {
                    ticks: self.ticks * x as $ticks,
                }
            }
        }

        impl<T: IntFactors> Mul<T> for $duration {
            type Output = $duration;

            #[allow(clippy::op_ref)]
            fn mul(self, rhs: T) -> Self::Output {
                let x: i128 = rhs.into();
                &self * x
            }
        }

        impl Mul<usize> for &$duration {
            type Output = $duration;

            fn mul(self, rhs: usize) -> Self::Output {
                self * rhs as i128
            }
        }

        impl Mul<usize> for $duration {
            type Output = $duration;

            #[allow(clippy::op_ref)]
            fn mul(self, rhs: usize) -> Self::Output {
                &self * rhs
            }
        }

        impl Mul<$duration> for i128 {
            type Output = $duration;

            fn mul(self, rhs: $duration) -> Self::Output {
                rhs * self
            }
        }

        impl Mul<&$duration> for i128 {
            type Output = $duration;

            fn mul(self, rhs: &$duration) -> Self::Output {
                rhs * self
            }
        }

        impl Mul<$duration> for usize {
            type Output = $duration;

            fn mul(self, rhs: $duration) -> Self::Output {
                rhs * self
            }
        }

        impl Mul<&$duration> for usize {
            type Output = $duration;

            fn mul(self, rhs: &$duration) -> Self::Output {
                rhs * self
            }
        }

        /// ### Duration floating point multiplication

        impl Mul<f64> for &$duration {
            type Output = $duration;

            fn mul(self, rhs: f64) -> Self::Output {
                Self::Output {
                    ticks: (self.ticks as f64 * rhs) as $ticks,
                }
            }
        }

        impl Mul<f64> for $duration {
            type Output = $duration;

            fn mul(self, rhs: f64) -> Self::Output {
                &self * rhs
            }
        }

        impl Mul<$duration> for f64 {
            type Output = $duration;

            fn mul(self, rhs: $duration) -> Self::Output {
                rhs * self
            }
        }

        impl Mul<&$duration> for f64 {
            type Output = $duration;

            fn mul(self, rhs: &$duration) -> Self::Output {
                rhs * self
            }
        }

        impl Mul<f32> for &$duration {
            type Output = $duration;

            fn mul(self, rhs: f32) -> Self::Output {
                Self::Output {
                    ticks: (self.ticks as f64 * rhs as f64) as $ticks,
                }
            }
        }

        impl Mul<f32> for $duration {
            type Output = $duration;

            fn mul(self, rhs: f32) -> Self::Output {
                &self * rhs
            }
        }

        impl Mul<$duration> for f32 {
            type Output = $duration;

            fn mul(self, rhs: $duration) -> Self::Output {
                rhs * self
            }
        }

        impl Mul<&$duration> for f32 {
            type Output = $duration;

            fn mul(self, rhs: &$duration) -> Self::Output {
                rhs * self
            }
        }

        /// #### Integer division

        impl<T: IntFactors> Div<T> for &$duration {
            type Output = $duration;

            fn div(self, rhs: T) -> Self::Output {
                let x = rhs.into();
                Self::Output {
                    ticks: self.ticks / x as $ticks,
                }
            }
        }

        impl<T: IntFactors> Div<T> for $duration {
            type Output = $duration;

            fn div(self, rhs: T) -> Self::Output {
                let x: i128 = rhs.into();
                &self / x
            }
        }

        impl Div<usize> for &$duration {
            type Output = $duration;

            fn div(self, rhs: usize) -> Self::Output {
                self / rhs as i128
            }
        }

        impl Div<usize> for $duration {
            type Output = $duration;

            fn div(self, rhs: usize) -> Self::Output {
                self / rhs as i128
            }
        }

        /// #### Floating point division
        impl Div<f64> for &$duration {
            type Output = $duration;

            fn div(self, rhs: f64) -> Self::Output {
                self * (1.0 / rhs)
            }
        }

        impl Div<f64> for $duration {
            type Output = $duration;

            fn div(self, rhs: f64) -> Self::Output {
                &self / rhs
            }
        }

        impl Div<f32> for &$duration {
            type Output = $duration;

            fn div(self, rhs: f32) -> Self::Output {
                self / rhs as f64
            }
        }

        impl Div<f32> for $duration {
            type Output = $duration;

            fn div(self, rhs: f32) -> Self::Output {
                &self / rhs
            }
        }

        /// ## Duration % C = Duration
        /// ### Integer remainder
        impl<T: IntFactors> Rem<T> for &$duration {
            type Output = $duration;

            fn rem(self, rhs: T) -> Self::Output {
                let x: i128 = rhs.into();
                Self::Output {
                    ticks: self.ticks % x as $ticks,
                }
            }
        }

        impl<T: IntFactors> Rem<T> for $duration {
            type Output = $duration;

            fn rem(self, rhs: T) -> Self::Output {
                let x: i128 = rhs.into();
                &self % x
            }
        }

        /// ### Floating point remainder
        impl Rem<f64> for &$duration {
            type Output = $duration;

            fn rem(self, rhs: f64) -> Self::Output {
                let d = self / rhs;

                let m = d * rhs;

                self - m
            }
        }

        impl Rem<f64> for $duration {
            type Output = $duration;

            fn rem(self, rhs: f64) -> Self::Output {
                &self % rhs
            }
        }

        impl Rem<f32> for &$duration {
            type Output = $duration;

            fn rem(self, rhs: f32) -> Self::Output {
                let d = self / rhs as f64;

                let m = d * rhs as f64;

                self - m
            }
        }

        impl Rem<f32> for $duration {
            type Output = $duration;

            fn rem(self, rhs: f32) -> Self::Output {
                &self % rhs
            }
        }

        /// ## Duration / Duration = C
        impl Div<&$duration> for &$duration {
            type Output = $ticks;

            fn div(self, rhs: &$duration) -> Self::Output {
                self.ticks / rhs.ticks
            }
        }

        impl Div<&$duration> for $duration {
            type Output = $ticks;

            fn div(self, rhs: &$duration) -> Self::Output {
                &self / rhs
            }
        }

        impl Div<$duration> for &$duration {
            type Output = $ticks;

            fn div(self, rhs: $duration) -> Self::Output {
                self / &rhs
            }
        }

        impl Div<$duration> for $duration {
            type Output = $ticks;

            fn div(self, rhs: $duration) -> Self::Output {
                &self / &rhs
            }
        }

        /// ## Duration % Duration = C
        impl Rem<&$duration> for &$duration {
            type Output = $duration;

            fn rem(self, rhs: &$duration) -> Self::Output {
                Self::Output {
                    ticks: self.ticks % rhs.ticks,
                }
            }
        }

        impl Rem<&$duration> for $duration {
            type Output = $duration;

            fn rem(self, rhs: &$duration) -> Self::Output {
                &self % rhs
            }
        }

        impl Rem<$duration> for &$duration {
            type Output = $duration;

            fn rem(self, rhs: $duration) -> Self::Output {
                self % &rhs
            }
        }

        impl Rem<$duration> for $duration {
            type Output = $duration;

            fn rem(self, rhs: $duration) -> Self::Output {
                &self % &rhs
            }
        }

        /// ## -Duration = Duration
        impl Neg for &$duration {
            type Output = $duration;

            fn neg(self) -> Self::Output {
                Self::Output { ticks: -self.ticks }
            }
        }

        impl Neg for $duration {
            type Output = $duration;

            fn neg(self) -> Self::Output {
                -&self
            }
        }
    };
}

pub (super) use operators;

pub(crate) trait IntFactors: Into<i128> {}

impl IntFactors for u8 {}
impl IntFactors for u16 {}
impl IntFactors for u32 {}
impl IntFactors for u64 {}
impl IntFactors for i8 {}
impl IntFactors for i16 {}
impl IntFactors for i32 {}
impl IntFactors for i64 {}
impl IntFactors for i128 {}