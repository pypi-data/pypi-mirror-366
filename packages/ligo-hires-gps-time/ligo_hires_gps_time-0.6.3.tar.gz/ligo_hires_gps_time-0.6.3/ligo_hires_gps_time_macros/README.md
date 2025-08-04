ligo_hires_gps_time is a Rust crate that provides high-resolution time types that coincide with GPS time, which is seconds
since Januray 6, 1980, and disregards leap seconds.

The module provides two units of time of different duration.

The structs `PipInstant`, and `PipDuration` use the "pip" unit.  There are $`2^{30} \cdot 5^{9} = 2,097,152,000,000,000`$ pips per second.

The structs `ThumpInstant` and `ThumpDuration` use the "thump".  There are $`2^{19} \cdot 5^{5} = 1,638,400,000`$ pips per second.

# History and Motivation

Almost all LIGO channels have a data rate that is a power of two.  This choice has some benefits.  The data rates are 
exactly representable as floating point numbers.  FFTs, which are more efficient with inputs with sizes that are powers 
of two, produce bucket-widths that are either simple fractions of 1 Hz, or multiples of 1 Hz.

At the same time, LIGO software has historically used nanosecond resolution value to represent times and durations. 
Since there are 1 billion nanoseconds in a second, and 1 billion is factored into $` 2^9 \cdot 5^9 `$, nanoseconds can 
exactly represent any rate that's a power of two, as long as it's no greater than $` 2^9 `$, or 512 Hz.

The typical LIGO fast channel is $` 2^{14} `$ or 16384 Hz, which is too great to be represented by nanoseconds exactly.  
The period of such a channel is $` P = 61035.15625 `$ ns .

For nanosecond resolution values, the error in units of samples is $` E = 1 - \lfloor{P}\rfloor/{P} = 2.56\cdot10^{-6} `$ samples-per-sample.

We get into trouble when $` E \cdot n \ge 0.5 `$, where $`n`$ is the number of samples.  For a 16384 Hz channel, that's less than 12 
seconds worth of samples.

Double-precision floating point values can help, but they will become worse than nanosecond resolution for any span greater than 52 days,
and won't do much better for most of the days prior.

With care, this error can be corrected, but if the right time resolution is used, the error is zero.

# Operators

Useful math operators between durations and instants are provided,
as well as operators for scaling duration.

# Features

## nds
Include functions to convert to and from NDS time types.

## hifitime
Include functions to convert to and from [hifitime](https://github.com/nyx-space/hifitime) types.

## python
Include [pyo3](https://github.com/PyO3/pyo3) and use it to create a python interface

## all
Include all other features

# Python

We use [pyO3](https://github.com/PyO3/pyo3) to create a python interface, providing these same types and operators in python.

Build and package the python using "maturin", but make sure to specify at least the 'python' feature.

```bash
maturin develop --features python
python
import gps_pip
```

## Testing python

With python in development using maturin, run
```bash
python -m pytest
```

# Testing

[bacon](https://dystroy.org/bacon/) can be used to speed up testing.

The repo includes a `bacon.toml` file with some custom jobs.

Run bacon in the project directory. Use the hotkeys 1 through 0 in order to complete a full test, including of python interface.