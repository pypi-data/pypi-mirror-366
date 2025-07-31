#[macro_use]
mod macros;

mod buffer;
mod client;
mod error;
mod typing;

use client::{
    async_impl::{
        Client,
        response::{Message, Response, Streamer, WebSocket},
    },
    blocking::{BlockingClient, BlockingResponse, BlockingStreamer, BlockingWebSocket},
    delete, get, head, options, patch, post, put, request, trace, websocket,
};
use error::*;
use pyo3::{prelude::*, types::PyDict, wrap_pymodule};
use typing::{
    Cookie, HeaderMap, HeaderMapItemsIter, HeaderMapKeysIter, HeaderMapValuesIter, Impersonate,
    ImpersonateOS, ImpersonateOption, LookupIpStrategy, Method, Multipart, Part, Proxy, SameSite,
    SocketAddr, StatusCode, TlsVersion, Version,
};

#[cfg(all(
    not(target_env = "msvc"),
    not(all(target_os = "linux", target_env = "gnu"))
))]
#[global_allocator]
static ALLOC: jemallocator::Jemalloc = jemallocator::Jemalloc;

#[pymodule(gil_used = false)]
fn rnet(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    pyo3::prepare_freethreaded_python();
    m.add_class::<SocketAddr>()?;
    m.add_class::<Message>()?;
    m.add_class::<StatusCode>()?;
    m.add_class::<Part>()?;
    m.add_class::<Multipart>()?;
    m.add_class::<Client>()?;
    m.add_class::<Response>()?;
    m.add_class::<WebSocket>()?;
    m.add_class::<Streamer>()?;
    m.add_class::<Proxy>()?;
    m.add_class::<Method>()?;
    m.add_class::<Version>()?;
    m.add_class::<LookupIpStrategy>()?;
    m.add_class::<TlsVersion>()?;

    m.add_function(wrap_pyfunction!(get, m)?)?;
    m.add_function(wrap_pyfunction!(post, m)?)?;
    m.add_function(wrap_pyfunction!(put, m)?)?;
    m.add_function(wrap_pyfunction!(patch, m)?)?;
    m.add_function(wrap_pyfunction!(delete, m)?)?;
    m.add_function(wrap_pyfunction!(head, m)?)?;
    m.add_function(wrap_pyfunction!(options, m)?)?;
    m.add_function(wrap_pyfunction!(trace, m)?)?;
    m.add_function(wrap_pyfunction!(request, m)?)?;
    m.add_function(wrap_pyfunction!(websocket, m)?)?;

    m.add_wrapped(wrap_pymodule!(header_module))?;
    m.add_wrapped(wrap_pymodule!(cookie_module))?;
    m.add_wrapped(wrap_pymodule!(impersonate_module))?;
    m.add_wrapped(wrap_pymodule!(blocking_module))?;
    m.add_wrapped(wrap_pymodule!(exceptions_module))?;

    let sys = PyModule::import(py, "sys")?;
    let sys_modules: Bound<'_, PyDict> = sys.getattr("modules")?.downcast_into()?;
    sys_modules.set_item("rnet.header", m.getattr("header")?)?;
    sys_modules.set_item("rnet.cookie", m.getattr("cookie")?)?;
    sys_modules.set_item("rnet.impersonate", m.getattr("impersonate")?)?;
    sys_modules.set_item("rnet.blocking", m.getattr("blocking")?)?;
    sys_modules.set_item("rnet.exceptions", m.getattr("exceptions")?)?;
    Ok(())
}

#[pymodule(gil_used = false, name = "header")]
fn header_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<HeaderMap>()?;
    m.add_class::<HeaderMapItemsIter>()?;
    m.add_class::<HeaderMapKeysIter>()?;
    m.add_class::<HeaderMapValuesIter>()?;
    Ok(())
}

#[pymodule(gil_used = false, name = "cookie")]
fn cookie_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Cookie>()?;
    m.add_class::<SameSite>()?;
    Ok(())
}

#[pymodule(gil_used = false, name = "impersonate")]
fn impersonate_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Impersonate>()?;
    m.add_class::<ImpersonateOS>()?;
    m.add_class::<ImpersonateOption>()?;
    Ok(())
}

#[pymodule(gil_used = false, name = "blocking")]
fn blocking_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<BlockingClient>()?;
    m.add_class::<BlockingResponse>()?;
    m.add_class::<BlockingWebSocket>()?;
    m.add_class::<BlockingStreamer>()?;
    Ok(())
}

#[pymodule(gil_used = false, name = "exceptions")]
fn exceptions_module(py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("DNSResolverError", py.get_type::<DNSResolverError>())?;
    m.add("BodyError", py.get_type::<BodyError>())?;
    m.add("BuilderError", py.get_type::<BuilderError>())?;
    m.add("ConnectionError", py.get_type::<ConnectionError>())?;
    m.add(
        "ConnectionResetError",
        py.get_type::<ConnectionResetError>(),
    )?;
    m.add("DecodingError", py.get_type::<DecodingError>())?;
    m.add("RedirectError", py.get_type::<RedirectError>())?;
    m.add("TimeoutError", py.get_type::<TimeoutError>())?;
    m.add("StatusError", py.get_type::<StatusError>())?;
    m.add("RequestError", py.get_type::<RequestError>())?;
    m.add("UpgradeError", py.get_type::<UpgradeError>())?;
    m.add("URLParseError", py.get_type::<URLParseError>())?;
    m.add("MIMEParseError", py.get_type::<MIMEParseError>())?;
    Ok(())
}
