mod define_unit;

extern crate proc_macro;
use proc_macro::TokenStream;

/// Does nothing
/// This macro is needed so that `staticmethod` attribute still builds
/// when not using python
///
/// There doesn't seem to be a away to make that attribute conditional
#[proc_macro_attribute]
pub fn staticmethod(_attr: TokenStream, input: TokenStream) -> TokenStream {
    input
}

#[proc_macro]
pub fn define_unit(input: TokenStream) -> TokenStream {
    define_unit::define_unit(input)
}