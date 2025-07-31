use std::sync::{Arc, OnceLock};

use pyo3::PyResult;
use wreq::dns::HickoryDnsResolver;

use crate::{error::DNSResolverError, typing::LookupIpStrategy};

macro_rules! dns_resolver {
    ($strategy:expr) => {{
        static DNS_RESOLVER: OnceLock<Result<Arc<HickoryDnsResolver>, &'static str>> =
            OnceLock::new();
        init(&DNS_RESOLVER, $strategy)
    }};
}

/// Initializes and returns a DNS resolver with the specified strategy.
///
/// This function initializes a global DNS resolver using the provided lookup IP strategy.
/// If the DNS resolver has already been initialized, it returns the existing instance.
///
/// # Returns
///
/// A `Result` containing an `Arc` to the `HickoryDnsResolver` instance, or an error if
/// initialization fails.
///
/// # Errors
///
/// This function returns an error if the DNS resolver fails to initialize.
pub fn get_or_try_init<S>(strategy: S) -> PyResult<Arc<HickoryDnsResolver>>
where
    S: Into<Option<LookupIpStrategy>>,
{
    let strategy = strategy.into().unwrap_or(LookupIpStrategy::Ipv4AndIpv6);
    match strategy {
        LookupIpStrategy::Ipv4Only => dns_resolver!(strategy),
        LookupIpStrategy::Ipv6Only => dns_resolver!(strategy),
        LookupIpStrategy::Ipv4AndIpv6 => dns_resolver!(strategy),
        LookupIpStrategy::Ipv6thenIpv4 => dns_resolver!(strategy),
        LookupIpStrategy::Ipv4thenIpv6 => dns_resolver!(strategy),
    }
}

fn init(
    dns_resolver: &'static OnceLock<Result<Arc<HickoryDnsResolver>, &'static str>>,
    strategy: LookupIpStrategy,
) -> PyResult<Arc<HickoryDnsResolver>> {
    dns_resolver
        .get_or_init(move || {
            HickoryDnsResolver::new(strategy.into_ffi())
                .map(Arc::new)
                .map_err(|err| {
                    eprintln!("failed to initialize the DNS resolver: {}", err);
                    "failed to initialize the DNS resolver"
                })
        })
        .as_ref()
        .map(Arc::clone)
        .map_err(DNSResolverError::new_err)
}
