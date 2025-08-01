//! Implement `-p <python_spec>` argument parser of `virutualenv` from
//! <https://github.com/pypa/virtualenv/blob/216dc9f3592aa1f3345290702f0e7ba3432af3ce/src/virtualenv/discovery/py_spec.py>

use std::path::PathBuf;

use crate::languages::version;
use crate::languages::version::LanguageRequest;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PythonRequest {
    Major(u8),
    MajorMinor(u8, u8),
    MajorMinorPatch(u8, u8, u8),
    Path(PathBuf),
    Range(semver::VersionReq, String),
}

impl PythonRequest {
    // TODO: support version like `3.8b1`, `3.8rc2`, `python3.8t`, `python3.8-64`.
    // Parse Python language_version from pre-commit:
    // If request begins with `python`, then it can not follow a VersionReq syntax.
    // 1. `python3` => Major(3)
    // 2. `python3.12` => MajorMinor(3, 12)
    // 3. `python3.13.2` => MajorMinorPatch(3, 13, 2)
    // Otherwise invalid
    // Also parse `3`, `3.12`, `3.12.3` into Major, MajorMinor, MajorMinorPatch
    // Try to parse into a VersionReq like `>= 3.12` or `>=3.8, <3.12`
    pub fn parse(request: &str) -> Result<LanguageRequest, version::Error> {
        if request.is_empty() {
            return Ok(LanguageRequest::Any);
        }

        // Check if it starts with "python" - parse as specific version
        if let Some(version_part) = request.strip_prefix("python") {
            if version_part.is_empty() {
                return Ok(LanguageRequest::Any);
            }

            Self::parse_version_numbers(version_part, request)
        } else {
            Self::parse_version_numbers(request, request)
                .or_else(|_| {
                    // Try to parse as a VersionReq (like ">= 3.12" or ">=3.8, <3.12")
                    semver::VersionReq::parse(request)
                        .map(|version_req| {
                            LanguageRequest::Python(PythonRequest::Range(
                                version_req,
                                request.into(),
                            ))
                        })
                        .map_err(|_| version::Error::InvalidVersion(request.to_string()))
                })
                .or_else(|_| {
                    // If it doesn't match any known format, treat it as a path
                    let path = PathBuf::from(request);
                    if path.exists() {
                        Ok(LanguageRequest::Python(PythonRequest::Path(path)))
                    } else {
                        Err(version::Error::InvalidVersion(request.to_string()))
                    }
                })
        }
    }

    /// Parse version numbers into appropriate `PythonRequest` variants
    fn parse_version_numbers(
        version_str: &str,
        original_request: &str,
    ) -> Result<LanguageRequest, version::Error> {
        // Check if all parts are valid u8 numbers
        let parts = version_str
            .split('.')
            .map(str::parse::<u8>)
            .collect::<Result<Vec<_>, _>>()
            .map_err(|_| version::Error::InvalidVersion(original_request.to_string()))?;

        match parts[..] {
            [major] => Ok(LanguageRequest::Python(PythonRequest::Major(major))),
            [major, minor] => Ok(LanguageRequest::Python(PythonRequest::MajorMinor(
                major, minor,
            ))),
            [major, minor, patch] => Ok(LanguageRequest::Python(PythonRequest::MajorMinorPatch(
                major, minor, patch,
            ))),
            _ => Err(version::Error::InvalidVersion(original_request.to_string())),
        }
    }

    pub(crate) fn satisfied_by(&self, install_info: &crate::hook::InstallInfo) -> bool {
        match self {
            PythonRequest::Major(major) => install_info.language_version.major == u64::from(*major),
            PythonRequest::MajorMinor(major, minor) => {
                install_info.language_version.major == u64::from(*major)
                    && install_info.language_version.minor == u64::from(*minor)
            }
            PythonRequest::MajorMinorPatch(major, minor, patch) => {
                install_info.language_version.major == u64::from(*major)
                    && install_info.language_version.minor == u64::from(*minor)
                    && install_info.language_version.patch == u64::from(*patch)
            }
            PythonRequest::Path(path) => path == &install_info.toolchain,
            PythonRequest::Range(req, _) => req.matches(&install_info.language_version),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_python_request() {
        // Empty request
        assert_eq!(PythonRequest::parse("").unwrap(), LanguageRequest::Any);
        assert_eq!(
            PythonRequest::parse("python").unwrap(),
            LanguageRequest::Any
        );

        assert_eq!(
            PythonRequest::parse("python3").unwrap(),
            LanguageRequest::Python(PythonRequest::Major(3))
        );
        assert_eq!(
            PythonRequest::parse("python3.12").unwrap(),
            LanguageRequest::Python(PythonRequest::MajorMinor(3, 12))
        );
        assert_eq!(
            PythonRequest::parse("python3.13.2").unwrap(),
            LanguageRequest::Python(PythonRequest::MajorMinorPatch(3, 13, 2))
        );
        assert_eq!(
            PythonRequest::parse("3").unwrap(),
            LanguageRequest::Python(PythonRequest::Major(3))
        );
        assert_eq!(
            PythonRequest::parse("3.12").unwrap(),
            LanguageRequest::Python(PythonRequest::MajorMinor(3, 12))
        );
        assert_eq!(
            PythonRequest::parse("3.12.3").unwrap(),
            LanguageRequest::Python(PythonRequest::MajorMinorPatch(3, 12, 3))
        );

        // VersionReq
        assert_eq!(
            PythonRequest::parse(">=3.12").unwrap(),
            LanguageRequest::Python(PythonRequest::Range(
                semver::VersionReq::parse(">=3.12").unwrap(),
                ">=3.12".to_string()
            ))
        );
        assert_eq!(
            PythonRequest::parse(">=3.8, <3.12").unwrap(),
            LanguageRequest::Python(PythonRequest::Range(
                semver::VersionReq::parse(">=3.8, <3.12").unwrap(),
                ">=3.8, <3.12".to_string()
            ))
        );

        // Invalid versions
        assert!(PythonRequest::parse("invalid").is_err());
        assert!(PythonRequest::parse("3.12.3.4").is_err());
        assert!(PythonRequest::parse("3.12.a").is_err());
        assert!(PythonRequest::parse("3.b.1").is_err());
        assert!(PythonRequest::parse("3..2").is_err());
        assert!(PythonRequest::parse("a3.12").is_err());

        // TODO: support
        assert!(PythonRequest::parse("3.12.3a1").is_err(),);
        assert!(PythonRequest::parse("3.12.3rc1").is_err(),);
        assert!(PythonRequest::parse("python3.13.2a1").is_err());
        assert!(PythonRequest::parse("python3.13.2rc1").is_err());
        assert!(PythonRequest::parse("python3.13.2t1").is_err());
        assert!(PythonRequest::parse("python3.13.2-64").is_err());
        assert!(PythonRequest::parse("python3.13.2-64").is_err());
    }
}
