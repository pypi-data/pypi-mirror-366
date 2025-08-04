use proc_macro::{TokenStream};
use proc_macro2::{Ident, TokenStream as TokenStream2};
use quote::{quote};
use syn::{parse_macro_input, Expr, };
use syn::parse::{Parse, ParseStream};
use syn::punctuated::Punctuated;
use syn::token::Comma;

#[derive(Clone)]
struct Unit {
    name: Ident,
    _comma: Comma,
    rate_hz: Expr,
    _comma2: Comma,
    type_: Ident,
}

impl Parse for Unit {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        Ok(Unit{
            name: input.parse()?,
            _comma: input.parse()?,
            rate_hz: input.parse()?,
            _comma2: input.parse()?,
            type_: input.parse()?,
        })
    }
}

#[derive(Clone)]
struct Units(Punctuated<Unit, Comma>);

impl Parse for Units {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        Ok(Units(Punctuated::parse_terminated(input)?))
    }
}

fn add_conversion(unit_a: Unit, unit_b: Unit, unit_type: String) -> TokenStream2 {

    let name_a = unit_a.name.to_string();
    let name_b = unit_b.name.to_string();
    let to_name = Ident::new(&format!("to_{}_{}", name_b.to_lowercase(), unit_type.to_lowercase() ), unit_a.name.span());
    let type_name_a = Ident::new(&format!("{}{}", name_a, unit_type), unit_a.name.span());
    let type_name_b = Ident::new(&format!("{}{}", name_b, unit_type), unit_b.name.span());

    let rate_a = unit_a.rate_hz;
    let rate_b = unit_b.rate_hz;
    let tick_b = unit_b.type_;

    let stream = quote! {
      unit_conversion!( #rate_a, #type_name_a, #rate_b, #type_name_b, #tick_b, #to_name);
    };

    stream
}

pub (super) fn define_unit(item: TokenStream) -> TokenStream {

    let units = parse_macro_input!(item as Units);

    let mut out_stream = TokenStream2::new();

    let units_a = units.clone().0;
    let units_b = units_a.clone();

    for (i, unit) in units_a.into_iter().enumerate() {
        let unit_a = unit.clone();
        let name = unit.name.to_string();
        let lname = format!("{}s", name.to_lowercase());
        let instant_name = Ident::new(&format!("{}Instant", name), unit.name.span());
        let duration_name = Ident::new(&format!("{}Duration", name), unit.name.span());
        let unit_name = Ident::new(&lname, unit.name.span());
        let to_units = Ident::new(&format!("to_{}", lname), unit.name.span());
        let from_units = Ident::new(&format!("from_{}", lname), unit.name.span());
        let to_gpst_units = Ident::new(&format!("to_gpst_{}", lname), unit.name.span());
        let from_gpst_units = Ident::new(&format!("from_gpst_{}", lname), unit.name.span());

        let rate = unit.rate_hz;
        let ticks = unit.type_;

        let mut stream = quote! {
            instant!( #instant_name, #unit_name, #rate, #ticks, #duration_name, #to_units, #from_units, #to_gpst_units, #from_gpst_units);
            duration!(#duration_name, #unit_name, #rate, #ticks, #instant_name, #to_units, #from_units);
            operators!(#instant_name, #duration_name, #ticks);
            #[cfg(feature = "python")]
            implement_pyunit!(#instant_name, #duration_name);
        };

        for j in  i+1..units_b.len() {
            let unit_b = units_b.get(j).unwrap();

            stream.extend(add_conversion(unit_a.clone(), unit_b.clone(), "Instant".to_string()));
            stream.extend(add_conversion(unit_b.clone(), unit_a.clone(), "Instant".to_string()));
            stream.extend(add_conversion(unit_a.clone(), unit_b.clone(), "Duration".to_string()));
            stream.extend(add_conversion(unit_b.clone(), unit_a.clone(), "Duration".to_string()));
        }


        out_stream.extend(stream);
    }

    out_stream.into()
}