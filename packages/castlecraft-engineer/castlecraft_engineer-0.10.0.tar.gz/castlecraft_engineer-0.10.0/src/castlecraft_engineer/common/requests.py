import http.client
import json
import ssl
import urllib.parse
from base64 import b64encode
from typing import Any, Dict, Optional, Tuple, Union


class Response:
    """
    A simple class for representing an HTTP Response object.
    """

    def __init__(
        self,
        status_code: int,
        headers: http.client.HTTPMessage,
        content: bytes,
        url: str,
        request_method: str,
        request_body: Optional[bytes] = None,
        request_headers: Optional[Dict[str, str]] = None,
    ):
        self.status_code = status_code
        self._raw_headers = headers
        self.content = content
        self.url = url
        self.request_method = request_method
        self.request_body = request_body
        self.request_headers = request_headers if request_headers else {}
        self._cached_json: Optional[Any] = None
        self._text_content: Optional[str] = None

    @property
    def headers(self) -> Dict[str, str]:
        """Returns headers as a case-insensitive dictionary."""
        # http.client.HTTPMessage is already somewhat case-insensitive for get()
        # but this provides a consistent dict view with lowercased keys.
        return {k.lower(): v for k, v in self._raw_headers.items()}

    @property
    def text(self) -> str:
        """Returns the content of the response, in unicode."""
        if self._text_content is None:
            content_type = self.headers.get("content-type", "")
            charset = "utf-8"  # Default
            if "charset=" in content_type:
                parts = content_type.split("charset=")
                if len(parts) > 1:
                    charset = parts[-1].split(";")[0].strip()
            try:
                self._text_content = self.content.decode(charset)
            except (UnicodeDecodeError, LookupError):
                self._text_content = self.content.decode("utf-8", errors="replace")
        return self._text_content

    def json(self, **kwargs) -> Any:
        """Returns the json-encoded content of a response, if any."""
        if self._cached_json is None:
            if not self.content:
                raise json.JSONDecodeError("No content to decode as JSON", "", 0)
            try:
                self._cached_json = json.loads(self.text, **kwargs)
            except json.JSONDecodeError as e:
                # Provide more context if possible
                raise ValueError(
                    f"Failed to decode JSON from URL {self.url}. Error: {e}. Content: '{self.text[:100]}...'"
                ) from e
        return self._cached_json

    def raise_for_status(self):
        """
        Raises an HTTPError if the HTTP request
        returned an unsuccessful status code.
        """
        if 400 <= self.status_code < 500:
            raise HTTPError(
                f"{self.status_code} Client Error for url: {self.url}",
                response=self,
            )
        elif 500 <= self.status_code < 600:
            raise HTTPError(
                f"{self.status_code} Server Error for url: {self.url}",
                response=self,
            )

    def __repr__(self):
        return f"<Response [{self.status_code}]>"


class HTTPError(IOError):
    """
    Custom exception for HTTP errors, optionally holding the response.
    """

    def __init__(self, *args, response: Optional[Response] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.response = response


class Requests:
    """
    A class that mimics core functionalities of the requests library
    using Python's standard http.client.
    """

    def _prepare_url_and_connection(
        self, url: str, verify_ssl: bool = True, timeout: float = 10.0
    ) -> Tuple[
        Union[http.client.HTTPSConnection, http.client.HTTPConnection], str, str
    ]:
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(
                f"Invalid URL: '{url}'. Missing scheme or network location."
            )

        host = parsed_url.hostname
        if host is None:
            raise ValueError(f"Invalid URL: '{url}'. Could not determine hostname.")

        path = parsed_url.path
        if not path:
            path = "/"
        if parsed_url.query:
            path += "?" + parsed_url.query

        port: Optional[int] = parsed_url.port

        if parsed_url.scheme == "https":
            context = ssl.create_default_context()
            if not verify_ssl:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            effective_port = port if port is not None else 443
            conn: Union[http.client.HTTPConnection, http.client.HTTPSConnection] = (
                http.client.HTTPSConnection(
                    host, port=effective_port, context=context, timeout=timeout
                )
            )
        elif parsed_url.scheme == "http":
            effective_port = port if port is not None else 80
            conn = http.client.HTTPConnection(
                host, port=effective_port, timeout=timeout
            )
        else:
            raise ValueError(f"Unsupported URL scheme: {parsed_url.scheme}")

        return conn, host, path

    def _extract_common_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        common_args: Dict[str, Any] = {}
        common_args["headers"] = kwargs.pop("headers", None)
        common_args["auth"] = kwargs.pop("auth", None)

        verify = kwargs.pop("verify", True)
        if isinstance(verify, str):
            common_args["verify_ssl"] = True
        else:
            common_args["verify_ssl"] = bool(verify)

        common_args["timeout"] = float(kwargs.pop("timeout", 10.0))
        return common_args

    def _request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json_data: Optional[Any] = None,
        **kwargs: Any,
    ) -> Response:
        common_args = self._extract_common_kwargs(kwargs)
        headers: Optional[Dict[str, str]] = common_args["headers"]
        auth: Optional[Tuple[str, str]] = common_args["auth"]
        verify_ssl: bool = common_args["verify_ssl"]
        timeout: float = common_args["timeout"]

        actual_url = url
        if params:
            query_string = urllib.parse.urlencode(params, doseq=True)
            if "?" in actual_url:
                actual_url += "&" + query_string
            else:
                actual_url += "?" + query_string

        conn, host_header_val, path = self._prepare_url_and_connection(
            actual_url, verify_ssl, timeout
        )

        request_headers: Dict[str, str] = {"Host": host_header_val}
        if headers:
            # Ensure header keys and values are strings
            header_items = headers.items()  # Make items() call explicit
            for key, value in header_items:
                str_key = str(key)
                str_value = str(value)
                request_headers[str_key] = str_value

        body_bytes: Optional[bytes] = None
        if json_data is not None and data is not None:
            raise ValueError(
                "Cannot provide both 'data' and 'json' (json_data internal)."
            )

        if json_data is not None:
            body_bytes = json.dumps(json_data).encode("utf-8")
            if "content-type" not in {k.lower() for k in request_headers.keys()}:
                request_headers["Content-Type"] = "application/json"
        elif data is not None:
            if isinstance(data, dict):
                body_bytes = urllib.parse.urlencode(data, doseq=True).encode("utf-8")
                if "content-type" not in {k.lower() for k in request_headers.keys()}:
                    request_headers["Content-Type"] = (
                        "application/x-www-form-urlencoded"
                    )
            elif isinstance(data, str):
                body_bytes = data.encode("utf-8")
            elif isinstance(data, bytes):
                body_bytes = data
            else:
                raise TypeError("Data must be a dict, str, or bytes.")

        if auth and isinstance(auth, tuple) and len(auth) == 2:
            user, passwd = auth
            auth_header_val = b64encode(f"{user}:{passwd}".encode()).decode("ascii")
            request_headers["Authorization"] = f"Basic {auth_header_val}"

        try:
            conn.request(method.upper(), path, body=body_bytes, headers=request_headers)
            http_response = conn.getresponse()
            response_content = http_response.read()

            # For Response object context
            final_request_headers = request_headers.copy()

            return Response(
                status_code=http_response.status,
                headers=http_response.headers,
                content=response_content,
                url=actual_url,
                request_method=method.upper(),
                request_body=body_bytes,
                request_headers=final_request_headers,
            )
        except (
            http.client.HTTPException,
            OSError,
            ssl.SSLError,
            ConnectionRefusedError,
            TimeoutError,
        ) as e:
            # TimeoutError for Python 3.3+ for socket timeouts
            raise HTTPError(f"Request failed for {method} {url}: {e}") from e
        finally:
            conn.close()

    def get(
        self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Response:
        return self._request("GET", url, params=params, **kwargs)

    def post(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> Response:
        return self._request("POST", url, data=data, json_data=json, **kwargs)

    def put(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> Response:
        return self._request("PUT", url, data=data, json_data=json, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Response:
        return self._request("DELETE", url, **kwargs)

    def head(self, url: str, **kwargs: Any) -> Response:
        # HEAD requests should not have a body in the response,
        # but http.client handles this.
        # Our Response object will have empty content.
        return self._request("HEAD", url, **kwargs)

    def options(self, url: str, **kwargs: Any) -> Response:
        return self._request("OPTIONS", url, **kwargs)

    def patch(
        self,
        url: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Any] = None,
        **kwargs: Any,
    ) -> Response:
        return self._request("PATCH", url, data=data, json_data=json, **kwargs)


requests = Requests()
