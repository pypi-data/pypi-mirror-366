use std::time::SystemTime;

use bytes::Bytes;
use pyo3::{FromPyObject, prelude::*, pybacked::PyBackedStr, types::PyDict};
use wreq::{
    cookie::{self, Expiration},
    header::{self, HeaderMap, HeaderValue},
};

use crate::{client::typing::SameSite, error::Error};

/// A cookie.
#[pyclass(subclass)]
#[derive(Clone)]
pub struct Cookie(pub cookie::Cookie<'static>);

impl Cookie {
    pub(crate) fn extract_cookies(headers: &HeaderMap) -> Vec<Self> {
        headers
            .get_all(header::SET_COOKIE)
            .iter()
            .map(cookie::Cookie::parse)
            .flat_map(Result::ok)
            .map(cookie::Cookie::into_owned)
            .map(Cookie)
            .collect()
    }
}

#[pymethods]
impl Cookie {
    /// Create a new cookie.
    #[new]
    #[pyo3(signature = (
        name,
        value,
        domain = None,
        path = None,
        max_age = None,
        expires = None,
        http_only = false,
        secure = false,
        same_site = None
    ))]
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        name: String,
        value: String,
        domain: Option<String>,
        path: Option<String>,
        max_age: Option<std::time::Duration>,
        expires: Option<SystemTime>,
        http_only: bool,
        secure: bool,
        same_site: Option<SameSite>,
    ) -> Cookie {
        let mut builder = cookie::Cookie::builder(name, value);
        if let Some(domain) = domain {
            builder = builder.domain(domain);
        }

        if let Some(path) = path {
            builder = builder.path(path);
        }

        if let Some(max_age) = max_age {
            if let Ok(max_age) = cookie::Duration::try_from(max_age) {
                builder = builder.max_age(max_age);
            }
        }

        if let Some(expires) = expires {
            builder = builder.expires(Expiration::DateTime(expires.into()));
        }

        if http_only {
            builder = builder.http_only(true);
        }

        if secure {
            builder = builder.secure(true);
        }

        if let Some(same_site) = same_site {
            builder = builder.same_site(same_site.into_ffi());
        }

        Self(builder.build())
    }

    /// The name of the cookie.
    #[getter]
    #[inline(always)]
    pub fn name(&self) -> &str {
        self.0.name()
    }

    /// The value of the cookie.
    #[getter]
    #[inline(always)]
    pub fn value(&self) -> &str {
        self.0.value()
    }

    /// Returns true if the 'HttpOnly' directive is enabled.
    #[getter]
    #[inline(always)]
    pub fn http_only(&self) -> bool {
        self.0.http_only()
    }

    /// Returns true if the 'Secure' directive is enabled.
    #[getter]
    #[inline(always)]
    pub fn secure(&self) -> bool {
        self.0.secure()
    }

    /// Returns true if  'SameSite' directive is 'Lax'.
    #[getter]
    #[inline(always)]
    pub fn same_site_lax(&self) -> bool {
        self.0.same_site_lax()
    }

    /// Returns true if  'SameSite' directive is 'Strict'.
    #[getter]
    #[inline(always)]
    pub fn same_site_strict(&self) -> bool {
        self.0.same_site_strict()
    }

    /// Returns the path directive of the cookie, if set.
    #[getter]
    #[inline(always)]
    pub fn path(&self) -> Option<&str> {
        self.0.path()
    }

    /// Returns the domain directive of the cookie, if set.
    #[getter]
    #[inline(always)]
    pub fn domain(&self) -> Option<&str> {
        self.0.domain()
    }

    /// Get the Max-Age information.
    #[getter]
    #[inline(always)]
    pub fn max_age(&self) -> Option<std::time::Duration> {
        self.0.max_age()
    }

    /// The cookie expiration time.
    #[getter]
    #[inline(always)]
    pub fn expires(&self) -> Option<SystemTime> {
        self.0.expires()
    }

    fn __str__(&self) -> String {
        self.0.to_string()
    }

    fn __repr__(&self) -> String {
        self.__str__()
    }
}

pub struct CookieExtractor(pub Vec<HeaderValue>);

impl FromPyObject<'_> for CookieExtractor {
    fn extract_bound(ob: &Bound<'_, PyAny>) -> PyResult<Self> {
        let dict = ob.downcast::<PyDict>()?;
        dict.iter()
            .try_fold(Vec::with_capacity(dict.len()), |mut cookies, (k, v)| {
                let cookie = {
                    let mut cookie = String::with_capacity(10);
                    cookie.push_str(k.extract::<PyBackedStr>()?.as_ref());
                    cookie.push('=');
                    cookie.push_str(v.extract::<PyBackedStr>()?.as_ref());
                    HeaderValue::from_maybe_shared(Bytes::from(cookie)).map_err(Error::from)?
                };

                cookies.push(cookie);
                Ok(cookies)
            })
            .map(CookieExtractor)
    }
}
