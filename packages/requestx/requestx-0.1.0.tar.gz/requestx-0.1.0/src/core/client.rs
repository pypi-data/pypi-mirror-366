use bytes::Bytes;
use hyper::{Body, Client, HeaderMap, Method, Request, Uri};
use hyper_tls::HttpsConnector;
use serde_json::Value;
use std::collections::HashMap;
use std::sync::{Arc, OnceLock};
use std::time::Duration;
use tokio::runtime::Runtime;

use crate::error::RequestxError;

// Pre-allocated common strings to reduce allocations
const CONTENT_TYPE_JSON: &str = "application/json";
const CONTENT_TYPE_FORM: &str = "application/x-www-form-urlencoded";

// Global shared runtime for better performance
static GLOBAL_RUNTIME: OnceLock<Runtime> = OnceLock::new();

// Global shared client for connection pooling
static GLOBAL_CLIENT: OnceLock<Client<HttpsConnector<hyper::client::HttpConnector>>> = OnceLock::new();

fn get_global_runtime() -> &'static Runtime {
    GLOBAL_RUNTIME.get_or_init(|| {
        // Determine optimal worker thread count for concurrent operations
        let worker_threads = std::thread::available_parallelism()
            .map(|n| (n.get() * 2).min(16).max(4))  // 2x CPU cores, min 4, max 16
            .unwrap_or(8);  // Default to 8 if can't detect
            
        tokio::runtime::Builder::new_multi_thread()
            .worker_threads(worker_threads)           // More threads for better concurrency
            .max_blocking_threads(512)                // High blocking thread limit
            .thread_name("requestx-worker")           // Named threads for debugging
            .thread_stack_size(1024 * 1024)          // 1MB stack size (smaller for more threads)
            .enable_all()                             // Enable all tokio features
            .build()
            .expect("Failed to create optimized global tokio runtime")
    })
}

fn get_global_client() -> &'static Client<HttpsConnector<hyper::client::HttpConnector>> {
    GLOBAL_CLIENT.get_or_init(|| {
        let https = HttpsConnector::new();
        Client::builder()
            .pool_idle_timeout(Duration::from_secs(90))      // Longer idle timeout for better reuse
            .pool_max_idle_per_host(50)                      // More connections per host
            .http2_only(false)                               // Allow HTTP/1.1 fallback
            .http2_initial_stream_window_size(Some(65536))   // Optimize HTTP/2 streams
            .http2_initial_connection_window_size(Some(1048576)) // 1MB connection window
            .build::<_, hyper::Body>(https)
    })
}

/// Request configuration for HTTP requests
#[derive(Debug, Clone)]
pub struct RequestConfig {
    pub method: Method,
    pub url: Uri,
    pub headers: Option<HeaderMap>,
    pub params: Option<HashMap<String, String>>,
    pub data: Option<RequestData>,
    pub json: Option<Value>,
    pub timeout: Option<Duration>,
    pub allow_redirects: bool,
    pub verify: bool,
}

/// Request data types
#[derive(Debug, Clone)]
pub enum RequestData {
    Text(String),
    Bytes(Vec<u8>),
    Form(HashMap<String, String>),
}

/// Response data from HTTP requests
#[derive(Debug)]
pub struct ResponseData {
    pub status_code: u16,
    pub headers: HeaderMap,
    pub body: Bytes,
    pub url: Uri,
}

/// Core HTTP client using hyper
pub struct RequestxClient {
    // Use reference to global client for better performance
    use_global_client: bool,
    custom_client: Option<Client<HttpsConnector<hyper::client::HttpConnector>>>,
    custom_runtime: Option<Arc<Runtime>>,
}

impl RequestxClient {
    // Constants for default values to reduce allocations
    const DEFAULT_ALLOW_REDIRECTS: bool = true;
    const DEFAULT_VERIFY: bool = true;

    /// Create a new RequestxClient using global shared resources
    pub fn new() -> Result<Self, RequestxError> {
        Ok(RequestxClient {
            use_global_client: true,
            custom_client: None,
            custom_runtime: None,
        })
    }

    /// Create a new RequestxClient with custom runtime
    pub fn with_runtime(runtime: Runtime) -> Result<Self, RequestxError> {
        Ok(RequestxClient {
            use_global_client: true,
            custom_client: None,
            custom_runtime: Some(Arc::new(runtime)),
        })
    }

    /// Create a new RequestxClient with custom client configuration
    pub fn with_custom_client(client: Client<HttpsConnector<hyper::client::HttpConnector>>) -> Result<Self, RequestxError> {
        Ok(RequestxClient {
            use_global_client: false,
            custom_client: Some(client),
            custom_runtime: None,
        })
    }

    /// Get the HTTP client to use (global or custom)
    fn get_client(&self) -> &Client<HttpsConnector<hyper::client::HttpConnector>> {
        if self.use_global_client {
            get_global_client()
        } else {
            self.custom_client.as_ref().unwrap()
        }
    }

    /// Get the runtime to use (global or custom)
    fn get_runtime(&self) -> &Runtime {
        if let Some(ref custom_runtime) = self.custom_runtime {
            custom_runtime
        } else {
            get_global_runtime()
        }
    }

    /// Create a default RequestConfig for a given method and URL
    fn create_default_config(&self, method: Method, url: Uri) -> RequestConfig {
        RequestConfig {
            method,
            url,
            headers: None,
            params: None,
            data: None,
            json: None,
            timeout: None,
            allow_redirects: Self::DEFAULT_ALLOW_REDIRECTS,
            verify: Self::DEFAULT_VERIFY,
        }
    }

    /// Perform an async HTTP GET request
    pub async fn get_async(
        &self,
        url: Uri,
        config: Option<RequestConfig>,
    ) -> Result<ResponseData, RequestxError> {
        let request_config = config.unwrap_or_else(|| self.create_default_config(Method::GET, url));
        self.request_async(request_config).await
    }

    /// Perform an async HTTP POST request
    pub async fn post_async(
        &self,
        url: Uri,
        config: Option<RequestConfig>,
    ) -> Result<ResponseData, RequestxError> {
        let request_config = config.unwrap_or_else(|| self.create_default_config(Method::POST, url));
        self.request_async(request_config).await
    }

    /// Perform an async HTTP PUT request
    pub async fn put_async(
        &self,
        url: Uri,
        config: Option<RequestConfig>,
    ) -> Result<ResponseData, RequestxError> {
        let request_config = config.unwrap_or_else(|| self.create_default_config(Method::PUT, url));
        self.request_async(request_config).await
    }

    /// Perform an async HTTP DELETE request
    pub async fn delete_async(
        &self,
        url: Uri,
        config: Option<RequestConfig>,
    ) -> Result<ResponseData, RequestxError> {
        let request_config = config.unwrap_or_else(|| self.create_default_config(Method::DELETE, url));
        self.request_async(request_config).await
    }

    /// Perform an async HTTP HEAD request
    pub async fn head_async(
        &self,
        url: Uri,
        config: Option<RequestConfig>,
    ) -> Result<ResponseData, RequestxError> {
        let request_config = config.unwrap_or_else(|| self.create_default_config(Method::HEAD, url));
        self.request_async(request_config).await
    }

    /// Perform an async HTTP OPTIONS request
    pub async fn options_async(
        &self,
        url: Uri,
        config: Option<RequestConfig>,
    ) -> Result<ResponseData, RequestxError> {
        let request_config = config.unwrap_or_else(|| self.create_default_config(Method::OPTIONS, url));
        self.request_async(request_config).await
    }

    /// Perform an async HTTP PATCH request
    pub async fn patch_async(
        &self,
        url: Uri,
        config: Option<RequestConfig>,
    ) -> Result<ResponseData, RequestxError> {
        let request_config = config.unwrap_or_else(|| self.create_default_config(Method::PATCH, url));
        self.request_async(request_config).await
    }

    /// Perform a generic async HTTP request
    pub async fn request_async(
        &self,
        config: RequestConfig,
    ) -> Result<ResponseData, RequestxError> {
        let client = self.get_client().clone();
        Self::execute_request_async(client, config).await
    }

    /// Perform a synchronous HTTP request by spawning on async runtime
    pub fn request_sync(&self, config: RequestConfig) -> Result<ResponseData, RequestxError> {
        // Use the appropriate runtime (custom or global)
        let runtime = self.get_runtime();
        
        // Clone necessary data for the spawned task
        let client = self.get_client().clone();
        
        // Spawn the async task with cloned client
        let handle = runtime.spawn(async move {
            Self::execute_request_async(client, config).await
        });
        
        // Block on the spawned task handle instead of the runtime directly
        runtime.block_on(handle).map_err(|e| {
            RequestxError::RuntimeError(format!("Task execution failed: {}", e))
        })?
    }
    
    /// Static method to execute async request with a given client
    async fn execute_request_async(
        client: Client<HttpsConnector<hyper::client::HttpConnector>>,
        config: RequestConfig,
    ) -> Result<ResponseData, RequestxError> {
        // Build the request more efficiently
        let mut request_builder = Request::builder()
            .method(&config.method)  // Use reference instead of clone
            .uri(&config.url);       // Use reference instead of clone

        // Add headers efficiently
        if let Some(ref headers) = config.headers {
            for (name, value) in headers.iter() {
                request_builder = request_builder.header(name, value);
            }
        }

        // Build request body more efficiently
        let body = match (&config.data, &config.json) {
            (Some(RequestData::Text(text)), None) => {
                Body::from(text.clone())  // Need to clone for lifetime
            }
            (Some(RequestData::Bytes(bytes)), None) => {
                Body::from(bytes.clone())  // Need to clone for lifetime
            }
            (Some(RequestData::Form(form)), None) => {
                // More efficient form encoding with pre-allocated capacity
                let estimated_size = form.iter()
                    .map(|(k, v)| k.len() + v.len() + 10) // +10 for encoding overhead
                    .sum::<usize>();
                let mut form_data = String::with_capacity(estimated_size);
                
                let mut first = true;
                for (k, v) in form.iter() {
                    if !first {
                        form_data.push('&');
                    }
                    form_data.push_str(&urlencoding::encode(k));
                    form_data.push('=');
                    form_data.push_str(&urlencoding::encode(v));
                    first = false;
                }
                
                request_builder = request_builder.header("content-type", CONTENT_TYPE_FORM);
                Body::from(form_data)
            }
            (None, Some(json)) => {
                let json_string = serde_json::to_string(json)?;
                request_builder = request_builder.header("content-type", CONTENT_TYPE_JSON);
                Body::from(json_string)
            }
            (None, None) => Body::empty(),
            (Some(_), Some(_)) => {
                return Err(RequestxError::RuntimeError(
                    "Cannot specify both data and json parameters".to_string(),
                ));
            }
        };

        let request = request_builder
            .body(body)
            .map_err(|e| RequestxError::RuntimeError(format!("Failed to build request: {}", e)))?;

        // Execute the request with optional timeout
        let response = if let Some(timeout) = config.timeout {
            tokio::time::timeout(timeout, client.request(request)).await??
        } else {
            client.request(request).await?
        };

        // Extract response data efficiently
        let status_code = response.status().as_u16();
        let headers = response.headers().clone();  // This clone is necessary
        let url = config.url;  // Move instead of clone

        // Read response body
        let body_bytes = hyper::body::to_bytes(response.into_body()).await?;

        Ok(ResponseData {
            status_code,
            headers,
            body: body_bytes,
            url,
        })
    }
}

impl Default for RequestxClient {
    fn default() -> Self {
        Self::new().expect("Failed to create default RequestxClient")
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tokio::runtime::Runtime;

    #[tokio::test]
    async fn test_client_creation() {
        let client = RequestxClient::new();
        assert!(client.is_ok());
    }

    #[tokio::test]
    async fn test_client_with_runtime() {
        let rt = Runtime::new().unwrap();
        let client = RequestxClient::with_runtime(rt);
        assert!(client.is_ok());
    }

    #[tokio::test]
    async fn test_get_request() {
        let client = RequestxClient::new().unwrap();
        let url: Uri = "https://httpbin.org/get".parse().unwrap();

        let result = client.get_async(url, None).await;
        assert!(result.is_ok());

        let response = result.unwrap();
        assert_eq!(response.status_code, 200);
        assert!(!response.body.is_empty());
    }

    #[tokio::test]
    async fn test_post_request() {
        let client = RequestxClient::new().unwrap();
        let url: Uri = "https://httpbin.org/post".parse().unwrap();

        let result = client.post_async(url, None).await;
        assert!(result.is_ok());

        let response = result.unwrap();
        assert_eq!(response.status_code, 200);
    }

    #[tokio::test]
    async fn test_put_request() {
        let client = RequestxClient::new().unwrap();
        let url: Uri = "https://httpbin.org/put".parse().unwrap();

        let result = client.put_async(url, None).await;
        assert!(result.is_ok());

        let response = result.unwrap();
        assert_eq!(response.status_code, 200);
    }

    #[tokio::test]
    async fn test_delete_request() {
        let client = RequestxClient::new().unwrap();
        let url: Uri = "https://httpbin.org/delete".parse().unwrap();

        let result = client.delete_async(url, None).await;
        assert!(result.is_ok());

        let response = result.unwrap();
        assert_eq!(response.status_code, 200);
    }

    #[tokio::test]
    async fn test_head_request() {
        let client = RequestxClient::new().unwrap();
        let url: Uri = "https://httpbin.org/get".parse().unwrap();

        let result = client.head_async(url, None).await;
        assert!(result.is_ok());

        let response = result.unwrap();
        assert_eq!(response.status_code, 200);
        // HEAD requests should have empty body
        assert!(response.body.is_empty());
    }

    #[tokio::test]
    async fn test_options_request() {
        let client = RequestxClient::new().unwrap();
        let url: Uri = "https://httpbin.org/get".parse().unwrap();

        let result = client.options_async(url, None).await;
        assert!(result.is_ok());

        let response = result.unwrap();
        // OPTIONS requests typically return 200 or 204
        assert!(response.status_code == 200 || response.status_code == 204);
    }

    #[tokio::test]
    async fn test_patch_request() {
        let client = RequestxClient::new().unwrap();
        let url: Uri = "https://httpbin.org/patch".parse().unwrap();

        let result = client.patch_async(url, None).await;
        assert!(result.is_ok());

        let response = result.unwrap();
        assert_eq!(response.status_code, 200);
    }

    #[tokio::test]
    async fn test_request_with_json_data() {
        let client = RequestxClient::new().unwrap();
        let url: Uri = "https://httpbin.org/post".parse().unwrap();

        let json_data = serde_json::json!({
            "key": "value",
            "number": 42
        });

        let config = RequestConfig {
            method: Method::POST,
            url,  // Remove unnecessary clone
            headers: None,
            params: None,
            data: None,
            json: Some(json_data),
            timeout: None,
            allow_redirects: true,
            verify: true,
        };

        let result = client.request_async(config).await;
        assert!(result.is_ok());

        let response = result.unwrap();
        assert_eq!(response.status_code, 200);
    }

    #[tokio::test]
    async fn test_request_with_form_data() {
        let client = RequestxClient::new().unwrap();
        let url: Uri = "https://httpbin.org/post".parse().unwrap();

        let mut form_data = HashMap::new();
        form_data.insert("key1".to_string(), "value1".to_string());
        form_data.insert("key2".to_string(), "value2".to_string());

        let config = RequestConfig {
            method: Method::POST,
            url,  // Remove unnecessary clone
            headers: None,
            params: None,
            data: Some(RequestData::Form(form_data)),
            json: None,
            timeout: None,
            allow_redirects: true,
            verify: true,
        };

        let result = client.request_async(config).await;
        assert!(result.is_ok());

        let response = result.unwrap();
        assert_eq!(response.status_code, 200);
    }

    #[tokio::test]
    async fn test_request_with_text_data() {
        let client = RequestxClient::new().unwrap();
        let url: Uri = "https://httpbin.org/post".parse().unwrap();

        let config = RequestConfig {
            method: Method::POST,
            url,  // Remove unnecessary clone
            headers: None,
            params: None,
            data: Some(RequestData::Text("Hello, World!".to_string())),
            json: None,
            timeout: None,
            allow_redirects: true,
            verify: true,
        };

        let result = client.request_async(config).await;
        assert!(result.is_ok());

        let response = result.unwrap();
        assert_eq!(response.status_code, 200);
    }

    #[tokio::test]
    async fn test_request_with_timeout() {
        let client = RequestxClient::new().unwrap();
        let url: Uri = "https://httpbin.org/delay/5".parse().unwrap();

        let config = RequestConfig {
            method: Method::GET,
            url,  // Remove unnecessary clone
            headers: None,
            params: None,
            data: None,
            json: None,
            timeout: Some(Duration::from_secs(1)), // 1 second timeout for 5 second delay
            allow_redirects: true,
            verify: true,
        };

        let result = client.request_async(config).await;
        assert!(result.is_err());

        // Should be a timeout error
        match result.unwrap_err() {
            RequestxError::TimeoutError(_) => (),
            _ => panic!("Expected timeout error"),
        }
    }

    #[tokio::test]
    async fn test_invalid_url() {
        let _client = RequestxClient::new().unwrap();
        let invalid_url = "not-a-valid-url";

        let result: Result<Uri, _> = invalid_url.parse();
        assert!(result.is_err());
    }

    #[test]
    fn test_sync_request() {
        let client = RequestxClient::new().unwrap();
        let url: Uri = "https://httpbin.org/get".parse().unwrap();

        let config = RequestConfig {
            method: Method::GET,
            url,  // Remove unnecessary clone
            headers: None,
            params: None,
            data: None,
            json: None,
            timeout: None,
            allow_redirects: true,
            verify: true,
        };

        let result = client.request_sync(config);
        assert!(result.is_ok());

        let response = result.unwrap();
        assert_eq!(response.status_code, 200);
    }

    #[test]
    fn test_error_conversion() {
        // Test that our error types can be created and converted
        let network_error = RequestxError::RuntimeError("Test error".to_string());
        let py_err: pyo3::PyErr = network_error.into();
        assert!(py_err.to_string().contains("Test error"));
    }
}
