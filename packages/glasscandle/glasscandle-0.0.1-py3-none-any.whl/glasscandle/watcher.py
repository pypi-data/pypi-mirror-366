from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

import json
import time
import requests

from .db import DB
from .http import create_session, HTTP_TIMEOUT
from .notifications import _call_notifiers
from .parsers import regex, jsonpath
from .pool import Pool, CustomFunc
from .providers import Provider, BiocondaProvider, CondaProvider, PyPIProvider, URLProvider

# Type alias for notification callbacks
NotifierCallback = Union[Callable[[str, str, str], None], List[Callable[[str, str, str], None]]]


class Watcher:
    """Main watcher class for tracking version changes across different providers.
    
    Args:
        db: Optional path to the JSON database file (default: None uses in-memory storage)
        allowed_custom_domains: Tuple of allowed domains for custom URL monitoring
        conda_channels: Default conda channels to search (default: ["conda-forge", "bioconda"])
        on_change: Default callback function(s) called when version changes occur
                          and no specific on_change is provided. Can be a single function
                          or a list of functions. Each receives (key, old_version, new_version).
    """
    
    def __init__(self, db: Optional[Path] = None, allowed_custom_domains: Tuple[str, ...] = (), 
                 conda_channels: Optional[List[str]] = None, 
                 on_change: Optional[NotifierCallback] = None):
        """
        Main watcher class for tracking version changes across different providers.

        Args:
          db (Optional[Path]): Optional path to the JSON database file (default: None uses in-memory storage)
          allowed_custom_domains (Tuple[str, ...]): Tuple of allowed domains for custom URL monitoring
          conda_channels (Optional[List[str]]): Default conda channels to search (default: ["conda-forge", "bioconda"])
          on_change (Optional[NotifierCallback]): Default callback function(s) called when version changes occur
                                and no specific on_change is provided. Can be a single function
                                or a list of functions. Each receives (key, old_version, new_version).
        """
        self.db = DB(db)
        self.pool = Pool()
        self._session = create_session()
        self._allowed_custom_domains = allowed_custom_domains
        self._conda_channels = conda_channels or ["conda-forge", "bioconda"]
        self._on_change = on_change

    # Registration methods
    def conda(self, name: str, channels: Optional[List[str]] = None, 
             on_change: Optional[NotifierCallback] = None, **kwargs) -> None:
        """Register a conda package for monitoring across multiple channels.
        
        Args:
            name: Package name to monitor. Can include channel prefix (e.g., "bioconda::samtools")
            channels: Optional list of channels to search. If None, uses default channels.
                     Ignored if name includes channel prefix.
            on_change: Optional callback function(s) called when version changes.
                      Can be a single function or list of functions.
                      Each receives (key, old_version, new_version) as arguments.
        
        Examples:
            # Search default channels (conda-forge, bioconda)
            watcher.conda("samtools")
            
            # Search specific channels only
            watcher.conda("samtools", channels=["bioconda"])
            
            # Use channel prefix (ignores channels parameter)
            watcher.conda("bioconda::samtools")
        """
        # Use provided channels, or fall back to instance default, or global default
        if channels is None:
            channels = self._conda_channels
        
        provider = CondaProvider(channels=channels)
        provider.on_change = on_change
        self.pool.conda[name] = provider

    def bioconda(self, name: str, on_change: Optional[NotifierCallback] = None, **kwargs) -> None:
        """Register a bioconda package for monitoring.
        
        Args:
            name: Package name to monitor
            on_change: Optional callback function(s) called when version changes.
                      Can be a single function or list of functions.
                      Each receives (key, old_version, new_version) as arguments.
        """
        provider = BiocondaProvider()
        provider.on_change = on_change
        self.pool.bioconda[name] = provider

    def pypi(self, name: str, on_change: Optional[NotifierCallback] = None, **kwargs) -> None:
        """Register a PyPI package for monitoring.
        
        Args:
            name: Package name to monitor
            on_change: Optional callback function(s) called when version changes.
                      Can be a single function or list of functions.
                      Each receives (key, old_version, new_version) as arguments.
        """
        provider = PyPIProvider()
        provider.on_change = on_change
        self.pool.pypi[name] = provider
    
    def url(self, url: str,
            parser: Callable[[requests.Response], str] = None,
            *,
            allow_http: bool = False,
            allowed_domains: Optional[Tuple[str, ...]] = None,
            on_change: Optional[NotifierCallback] = None) -> None:
        """Register a general URL with a parser function.
        
        Args:
            url: URL to monitor
            parser: Function to parse the response and extract version
            allow_http: Whether to allow plain HTTP URLs
            allowed_domains: Tuple of allowed domains for this URL
            on_change: Optional callback function called when version changes.
                      Receives (key, old_version, new_version) as arguments.
        """
        prov = URLProvider(
            parse=parser,
            allow_http=allow_http,
            allowed_domains=allowed_domains or self._allowed_custom_domains,
        )
        prov.on_change = on_change
        # validate now, fail fast
        prov._validate(url)
        self.pool.url[url] = prov

    def url_regex(self, url: str, pattern: str, group: int = 1, 
                  on_change: Optional[NotifierCallback] = None, **kwargs) -> None:
        """Register a URL with a regex parser.
        
        Args:
            url: URL to monitor
            pattern: Regex pattern to extract version
            group: Regex group number to capture (default: 1)
            on_change: Optional callback function called when version changes.
                      Receives (key, old_version, new_version) as arguments.
        """
        self.url(url, parser=regex(pattern, group), on_change=on_change, **kwargs)

    def response(self, url: str, on_change: Optional[Callable[[str, str, str], None]] = None) -> Callable[[CustomFunc], CustomFunc]:
        """Decorator for custom Response parsers.
        
        Args:
            url: URL to monitor
            on_change: Optional callback function called when version changes.
                      Receives (key, old_version, new_version) as arguments.
        """
        host = (urlparse(url).hostname or "")
        if self._allowed_custom_domains and host not in self._allowed_custom_domains:
            raise ValueError(f"Custom URL domain not allowed: {host}")

        def decorator(func: CustomFunc) -> CustomFunc:
            """
        This method is not defined in the provided code.
        """
            self.pool.custom[url] = func
            self.pool.custom_callbacks[url] = on_change
            return func
        return decorator

    def json(self, url: str, path: str, 
             on_change: Optional[NotifierCallback] = None, **kwargs) -> None:
        """Register a URL with a JSONPath parser.
        
        Args:
            url: URL to monitor (should return JSON)
            path: JSONPath expression to extract version (e.g., "$.version", "$.data[0].tag_name")
            on_change: Optional callback function called when version changes.
                      Receives (key, old_version, new_version) as arguments.
        """
        self.url(url, parser=jsonpath(path), on_change=on_change, **kwargs)

    # Core functionality
    def _update(self, key: str, new_value: str, on_change: Optional[NotifierCallback] = None) -> None:
        """Update a value in the database if it has changed."""
        old_value = self.db.get(key)
        if old_value == new_value:
            print(f"Skipping {key} as it is up to date.")
            return
        print(f"Updating {key}: {old_value} -> {new_value}")
        self.db.put(key, new_value)
        
        # Use provided callback, or fall back to default
        callback = on_change or self._on_change
        
        # Call the callback if available
        if callback:
            try:
                _call_notifiers(callback, key, old_value or "", new_value)
            except Exception as e:
                print(f"[WARN] on_change callback for {key} failed: {e}")

    def run(self, warn=False) -> None:
        """Run a single check of all registered providers."""
        providers: Tuple[Tuple[Dict[str, Provider], Provider], ...] = (
            (self._wrap(self.pool.bioconda), BiocondaProvider()),
            (self._wrap(self.pool.conda), CondaProvider()),
            (self._wrap(self.pool.pypi), PyPIProvider()),
            (self._wrap(self.pool.url), URLProvider()),  # proto only for .name
        )

        for items_map, proto in providers:
            for item, provider in items_map.items():
                try:
                    version = provider.fetch_version(item, self._session)
                    on_change = getattr(provider, 'on_change', None)
                    self._update(provider.key(item), version, on_change)
                except (requests.RequestException, ValueError, json.JSONDecodeError) as e:
                    if warn:
                        print(f"[WARN] {proto.name}:{item} failed: {e}")
                    else:
                        raise ValueError(f"Failed to fetch {proto.name} version for {item}: {e}")

        # Custom callables keep raw Response, but we still key them as url::URL
        for url, func in self.pool.custom.items():
            try:
                res = self._session.get(url, timeout=HTTP_TIMEOUT)
                if res.status_code != 200:
                    raise ValueError(f"{url} returned {res.status_code}")
                result = func(res)
                on_change = self.pool.custom_callbacks.get(url)
                self._update(f"url::{url}", result, on_change)
            except (requests.RequestException, ValueError) as e:
                if warn:
                    print(f"[WARN] custom:{url} failed: {e}")
                else:
                    raise ValueError(f"Failed to fetch custom URL {url}: {e}")

    def start(self, interval: int = 60) -> None:
        """Start continuous monitoring with the specified interval."""
        try:
            while True:
                self.run()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("Stopped.")

    @staticmethod
    def _wrap(d: Dict[str, Provider]) -> Dict[str, Provider]:
        """Wrapper for provider instances (no-op in current implementation)."""
        # If callers added raw names, convert to provider instances
        # In our registrations we already store instances, so this is no-op.
        return d

