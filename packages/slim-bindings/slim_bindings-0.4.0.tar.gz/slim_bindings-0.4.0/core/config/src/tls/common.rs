// Copyright AGNTCY Contributors (https://github.com/agntcy)
// SPDX-License-Identifier: Apache-2.0

use parking_lot::RwLock;
use rustls::RootCertStore;
use rustls::crypto::CryptoProvider;
use rustls::server::VerifierBuilderError;
use rustls::sign::CertifiedKey;
use rustls_native_certs;
use rustls_pki_types::pem::PemObject;
use rustls_pki_types::{CertificateDer, PrivateKeyDer};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use slim_auth::file_watcher::FileWatcher;
use std::path::Path;
use std::sync::Arc;
use std::time::Duration;
use thiserror::Error;

#[derive(Debug)]
pub(crate) struct WatcherCertResolver {
    // Files
    _key_file: String,
    _cert_file: String,

    // Crypto provider
    _provider: Arc<CryptoProvider>,

    // watchers
    _watchers: Vec<FileWatcher>,

    // the certificate
    pub cert: Arc<RwLock<Arc<CertifiedKey>>>,
}

fn to_certified_key(
    cert_der: Vec<CertificateDer<'static>>,
    key_der: PrivateKeyDer<'static>,
    crypto_provider: &CryptoProvider,
) -> CertifiedKey {
    CertifiedKey::from_der(cert_der, key_der, crypto_provider).unwrap()
}

impl WatcherCertResolver {
    pub(crate) fn new(
        key_file: impl Into<String>,
        cert_file: impl Into<String>,
        crypto_provider: &Arc<CryptoProvider>,
    ) -> Result<Self, ConfigError> {
        let key_file = key_file.into();
        let key_files = (key_file.clone(), key_file.clone());

        let cert_file = cert_file.into();
        let cert_files = (cert_file.clone(), cert_file.clone());
        let crypto_providers = (crypto_provider.clone(), crypto_provider.clone());

        // Read the cert and the key
        let key_der = PrivateKeyDer::from_pem_file(Path::new(&key_files.0))
            .map_err(|e| ConfigError::InvalidFile(e.to_string()))?;
        let cert_der = CertificateDer::from_pem_file(Path::new(&cert_files.0))
            .map_err(|e| ConfigError::InvalidFile(e.to_string()))?;

        // Transform it to CertifiedKey
        let cert_key = to_certified_key(vec![cert_der], key_der, crypto_provider);

        let cert = Arc::new(RwLock::new(Arc::new(cert_key)));
        let cert_clone = cert.clone();
        let w = FileWatcher::create_watcher(move |_file| {
            // Read the cert and the key
            let key_der = PrivateKeyDer::from_pem_file(Path::new(&key_files.0))
                .expect("failed to read key file");
            let cert_der = CertificateDer::from_pem_file(Path::new(&cert_files.0))
                .expect("failed to read cert file");
            let cert_key = to_certified_key(vec![cert_der], key_der, &crypto_providers.0);

            *cert_clone.as_ref().write() = Arc::new(cert_key);
        });

        Ok(Self {
            _key_file: key_files.1,
            _cert_file: cert_files.1,
            _provider: crypto_providers.1,
            _watchers: vec![w],
            cert,
        })
    }
}

#[derive(Debug)]
pub(crate) struct StaticCertResolver {
    // Cert and key
    _key_pem: String,
    _cert_pem: String,

    // the certificate
    pub cert: Arc<CertifiedKey>,
}

impl StaticCertResolver {
    pub(crate) fn new(
        key_pem: impl Into<String>,
        cert_pem: impl Into<String>,
        crypto_provider: &Arc<CryptoProvider>,
    ) -> Result<Self, ConfigError> {
        let key_pem = key_pem.into();
        let cert_pem = cert_pem.into();

        // Read the cert and the key
        let key_der =
            PrivateKeyDer::from_pem_slice(key_pem.as_bytes()).map_err(ConfigError::InvalidPem)?;
        let cert_der =
            CertificateDer::from_pem_slice(cert_pem.as_bytes()).map_err(ConfigError::InvalidPem)?;
        let cert_key = to_certified_key(vec![cert_der], key_der, crypto_provider);

        Ok(Self {
            _key_pem: key_pem,
            _cert_pem: cert_pem,
            cert: Arc::new(cert_key),
        })
    }
}

#[derive(Debug, Serialize, Deserialize, PartialEq, Clone, JsonSchema)]
pub struct Config {
    /// Path to the CA cert. For a client this verifies the server certificate.
    /// For a server this verifies client certificates. If empty uses system root CA.
    /// (optional)
    pub ca_file: Option<String>,

    /// In memory PEM encoded cert. (optional)
    pub ca_pem: Option<String>,

    /// If true, load system CA certificates pool in addition to the certificates
    /// configured in this struct.
    #[serde(default = "default_include_system_ca_certs_pool")]
    pub include_system_ca_certs_pool: bool,

    /// Path to the TLS cert to use for TLS required connections. (optional)
    pub cert_file: Option<String>,

    /// In memory PEM encoded TLS cert to use for TLS required connections. (optional)
    pub cert_pem: Option<String>,

    /// Path to the TLS key to use for TLS required connections. (optional)
    pub key_file: Option<String>,

    /// In memory PEM encoded TLS key to use for TLS required connections. (optional)
    pub key_pem: Option<String>,

    /// The TLS version to use. If not set, the default is "tls1.3".
    /// The value must be either "tls1.2" or "tls1.3".
    /// (optional)
    #[serde(default = "default_tls_version")]
    pub tls_version: String,

    /// ReloadInterval specifies the duration after which the certificate will be reloaded
    /// If not set, it will never be reloaded
    // TODO(msardara): not implemented yet
    pub reload_interval: Option<Duration>,
}

/// Errors for Config
#[derive(Error, Debug)]
pub enum ConfigError {
    #[error("invalid tls version: {0}")]
    InvalidTlsVersion(String),
    #[error("invalid pem format: {0}")]
    InvalidPem(rustls_pki_types::pem::Error),
    #[error("error reading cert/key from file: {0}")]
    InvalidFile(String),
    #[error("cannot use both file and pem for {0}")]
    CannotUseBoth(String),
    #[error("root store error: {0}")]
    RootStore(rustls::Error),
    #[error("config builder error")]
    ConfigBuilder(rustls::Error),
    #[error("missing server cert and key. cert_{{file, pem}} and key_{{file, pem}} must be set")]
    MissingServerCertAndKey,
    #[error("verifier builder error")]
    VerifierBuilder(VerifierBuilderError),
    #[error("unknown error")]
    Unknown,
}

// Defaults for Config
impl Default for Config {
    fn default() -> Config {
        Config {
            ca_file: None,
            ca_pem: None,
            include_system_ca_certs_pool: default_include_system_ca_certs_pool(),
            cert_file: None,
            cert_pem: None,
            key_file: None,
            key_pem: None,
            tls_version: "tls1.3".to_string(),
            reload_interval: None,
        }
    }
}

// Default system CA certs pool
fn default_include_system_ca_certs_pool() -> bool {
    false
}

// Default for tls version
fn default_tls_version() -> String {
    "tls1.3".to_string()
}

impl Config {
    pub(crate) fn with_ca_file(self, ca_file: &str) -> Config {
        Config {
            ca_file: Some(ca_file.to_string()),
            ..self
        }
    }

    pub(crate) fn with_ca_pem(self, ca_pem: &str) -> Config {
        Config {
            ca_pem: Some(ca_pem.to_string()),
            ..self
        }
    }

    pub(crate) fn with_include_system_ca_certs_pool(
        self,
        include_system_ca_certs_pool: bool,
    ) -> Config {
        Config {
            include_system_ca_certs_pool,
            ..self
        }
    }

    pub(crate) fn with_cert_file(self, cert_file: &str) -> Config {
        Config {
            cert_file: Some(cert_file.to_string()),
            ..self
        }
    }

    pub(crate) fn with_cert_pem(self, cert_pem: &str) -> Config {
        Config {
            cert_pem: Some(cert_pem.to_string()),
            ..self
        }
    }

    pub(crate) fn with_key_file(self, key_file: &str) -> Config {
        Config {
            key_file: Some(key_file.to_string()),
            ..self
        }
    }

    pub(crate) fn with_key_pem(self, key_pem: &str) -> Config {
        Config {
            key_pem: Some(key_pem.to_string()),
            ..self
        }
    }

    pub(crate) fn with_tls_version(self, tls_version: &str) -> Config {
        Config {
            tls_version: tls_version.to_string(),
            ..self
        }
    }

    pub(crate) fn with_reload_interval(self, reload_interval: Option<Duration>) -> Config {
        Config {
            reload_interval,
            ..self
        }
    }

    pub(crate) fn load_ca_cert_pool(&self) -> Result<RootCertStore, ConfigError> {
        let mut root_store = RootCertStore::empty();

        let cert = match (self.has_ca_file(), self.has_ca_pem()) {
            (true, true) => return Err(ConfigError::CannotUseBoth("ca".to_string())),
            (true, false) => {
                CertificateDer::from_pem_file(Path::new(self.ca_file.as_ref().unwrap()))
                    .map_err(ConfigError::InvalidPem)?
            }
            (false, true) => {
                CertificateDer::from_pem_slice(self.ca_pem.as_ref().unwrap().as_bytes())
                    .map_err(ConfigError::InvalidPem)?
            }
            (false, false) => return Ok(root_store),
        };

        root_store.add(cert).map_err(ConfigError::RootStore)?;

        if self.include_system_ca_certs_pool {
            for cert in
                rustls_native_certs::load_native_certs().expect("could not load platform certs")
            {
                root_store.add(cert).map_err(ConfigError::RootStore)?;
            }
        }

        Ok(root_store)
    }

    /// Returns true if the config has a CA cert
    pub fn has_ca(&self) -> bool {
        self.has_ca_file() || self.has_ca_pem()
    }

    /// Returns true if the config has a CA file
    pub fn has_ca_file(&self) -> bool {
        self.ca_file.is_some()
    }

    /// Returns true if the config has a CA PEM
    pub fn has_ca_pem(&self) -> bool {
        self.ca_pem.is_some()
    }

    /// Returns true if the config has a cert file
    pub fn has_cert_file(&self) -> bool {
        self.cert_file.is_some()
    }

    /// Returns true if the config has a cert PEM
    pub fn has_cert_pem(&self) -> bool {
        self.cert_pem.is_some()
    }

    /// Returns true if the config has a key file
    pub fn has_key_file(&self) -> bool {
        self.key_file.is_some()
    }

    /// Returns true if the config has a key PEM
    pub fn has_key_pem(&self) -> bool {
        self.key_pem.is_some()
    }
}

// trait load_rustls_config
pub trait RustlsConfigLoader<T> {
    fn load_rustls_config(&self) -> Result<Option<T>, ConfigError>;
}

// Tests
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default() {
        let config = Config::default();
        assert_eq!(config.ca_file, None);
        assert_eq!(config.ca_pem, None);
        assert!(!config.include_system_ca_certs_pool);
        assert_eq!(config.cert_file, None);
        assert_eq!(config.cert_pem, None);
        assert_eq!(config.key_file, None);
        assert_eq!(config.key_pem, None);
        assert_eq!(config.tls_version, "tls1.3".to_string());
        assert_eq!(config.reload_interval, None);
    }
}
