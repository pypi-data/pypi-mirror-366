
import re
import json
from typing import (
    Optional,
    Union,
    Dict,
    List,
    Any
)
from ...network import Network
from ...exceptions import (
    EngineError,
    InvalidAPIKeyError,
    APILimitExceededError,
    NetworkError,
    UnexpectedResponseError,
)

 
class SearchResult:
    """
    Represents a single search result item from Google Custom Search API.

    This class allows both dot-notation (obj.key) and dict-style (obj["key"]) access,
    while normalizing invalid Python attribute characters like ':' and '-'.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initialize the SearchResult object.

        Args:
            data (Dict[str, Any]): Raw search result data from the API.
        """
        # Normalize keys to make them valid Python attributes
        self._data = self._replace_keys(data)

        # Set attributes for dot-access
        for key, value in self._data.items():
            setattr(self, key, self._convert_recursive(value))

    def _replace_keys(self, obj: Any) -> Any:
        """
        Recursively replace ':' and '-' in keys with '_'.

        Args:
            obj (Any): The input data (dict, list, or primitive).

        Returns:
            Any: The normalized data.
        """
        if isinstance(obj, dict):
            return {
                re.sub(r"[:\-]", "_", k): self._replace_keys(v)
                for k, v in obj.items()
            }
        if isinstance(obj, list):
            return [self._replace_keys(item) for item in obj]
        return obj

    def __getattr__(self, name: str) -> Any:
        """
        Handle missing attributes for dot-notation access.

        Args:
            name (str): The attribute name.

        Returns:
            Any: Default value ("N/A") if attribute not found.
        """
        return None

    def __getitem__(self, key: str) -> Any:
        """
        Allow dictionary-style access (obj["key"]).

        Args:
            key (str): The key name.

        Returns:
            Any: The value for the given key, or "N/A" if not found.
        """
        value = self._data.get(key, None)
        # Ensure nested dicts are also SearchResult objects
        if isinstance(value, dict):
            return SearchResult(value)
        if isinstance(value, list):
            return [self._convert_recursive(v) for v in value]
        return value

    def __contains__(self, key: str) -> bool:
        """
        Check if a key exists in the data.

        Args:
            key (str): The key name.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return key in self._data

    def __iter__(self):
        """
        Allow iteration over keys like a dictionary.
        """
        return iter(self._data)

    def keys(self):
        """
        Return the keys of the search result.
        """
        return self._data.keys()

    def items(self):
        """
        Return the (key, value) pairs.
        """
        return self._data.items()

    def values(self):
        """
        Return the values.
        """
        return self._data.values()

    def __repr__(self) -> str:
        """
        Pretty-print the stored data in JSON format.
        """
        return json.dumps(self._data, ensure_ascii=False, indent=4)

    @classmethod
    def _convert_recursive(cls, value: Any) -> Any:
        """
        Recursively convert dictionaries and lists to SearchResult objects.

        Args:
            value (Any): The input value.

        Returns:
            Any: Converted object.
        """
        if isinstance(value, dict):
            return cls(value)
        if isinstance(value, list):
            return [cls._convert_recursive(item) for item in value]
        return value


class GoogleEngine:
    """
    Asynchronous engine for Google Custom Search API integration.

    Supports searching with extensive filtering and image search options.
    """

    def __init__(self, api_key: str, cse_id: str) -> None:
        """
        Initialize the engine with API credentials.

        Args:
            api_key (str): Google API key.
            cse_id (str): Programmable Search Engine ID (CSE ID).
        """
        self.api_key = api_key
        self.cse_id = cse_id
        self._endpoint = "https://www.googleapis.com/customsearch/v1"
        self._network: Optional[Network] = None

    async def __aenter__(self) -> "GoogleEngine":
        """
        Async context manager entrypoint.

        Returns:
            GoogleEngine: Instance of the initialized engine.
        """
        self._network = Network(self._endpoint)
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        """
        Async context manager cleanup.

        Args:
            exc_type (Optional[type]): Exception type if raised.
            exc_val (Optional[BaseException]): The exception instance.
            exc_tb (Optional[object]): The traceback object.
        """
        self._network = None

    async def connect(self) -> None:
        """
        Explicitly initialize the internal network client.

        Use this if not using the context manager.
        """
        self._network = Network(self._endpoint)

    async def close(self) -> None:
        """
        Explicitly close the network client session.

        Use this if not using the context manager.
        """
        self._network = None

    async def search(
        self,
        q: str,
        num: Optional[int] = None,
        start: Optional[int] = None,
        lr: Optional[str] = None,
        gl: Optional[str] = None,
        cr: Optional[str] = None,
        safe: Optional[str] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        exactTerms: Optional[str] = None,
        excludeTerms: Optional[str] = None,
        siteSearch: Optional[str] = None,
        siteSearchFilter: Optional[str] = None,
        dateRestrict: Optional[str] = None,
        fileType: Optional[str] = None,
        rights: Optional[str] = None,
        fields: Optional[str] = None,
        c2coff: Optional[str] = None,
        hl: Optional[str] = None,
        imgSize: Optional[str] = None,
        imgType: Optional[str] = None,
        imgColorType: Optional[str] = None,
        imgDominantColor: Optional[str] = None,
        searchType: Optional[str] = None,
        googlehost: Optional[str] = None,
        lowRange: Optional[str] = None,
        highRange: Optional[str] = None,
        linkSite: Optional[str] = None,
        hq: Optional[str] = None,
        imgFilter: Optional[str] = None,
    ) -> Union[List[SearchResult], List[None]]:
        """
        Perform an asynchronous search using Google Custom Search API.

        Args:
            q (str): The search query string.
            num (Optional[int]): Number of results to return (1 to 10).
            start (Optional[int]): Index of the first result to return (1-based).
            lr (Optional[str]): Restrict results to a language (e.g., 'lang_en').
            gl (Optional[str]): Country for geolocation (e.g., 'us',).
            cr (Optional[str]): Country restrict (e.g., 'countryUS').
            safe (Optional[str]): Filter adult content: 'active', 'high', or 'off'.
            sort (Optional[str]): Sort results (e.g., by 'date').
            filter (Optional[str]): Duplicate filter: '0' (off), '1' (on).
            exactTerms (Optional[str]): Results must include this exact phrase.
            excludeTerms (Optional[str]): Exclude results with these terms.
            siteSearch (Optional[str]): Restrict to a specific site.
            siteSearchFilter (Optional[str]): 'i' to include, 'e' to exclude site.
            dateRestrict (Optional[str]): Limit by date (e.g., 'd1', 'w2', 'y1').
            fileType (Optional[str]): Limit to file type (e.g., 'pdf', 'doc').
            rights (Optional[str]): Usage rights (e.g., 'cc_publicdomain').
            fields (Optional[str]): Fields to include (e.g., 'items(title,link)').
            c2coff (Optional[str]): Set '1' to disable spelling correction.
            hl (Optional[str]): UI language (not result language).
            imgSize (Optional[str]): Image size (e.g., 'medium', 'xxlarge').
            imgType (Optional[str]): Image type (e.g., 'clipart', 'photo').
            imgColorType (Optional[str]): Image color type (e.g., 'gray').
            imgDominantColor (Optional[str]): Dominant color (e.g., 'blue').
            searchType (Optional[str]): Set to 'image' for image search.
            googlehost (Optional[str]): Google host (e.g., 'google.co.uk').
            lowRange (Optional[str]): Lower bound for numeric range.
            highRange (Optional[str]): Upper bound for numeric range.
            linkSite (Optional[str]): Pages that link to the given site.
            hq (Optional[str]): Appends a helper/boost query.
            imgFilter (Optional[str]): Filter images for safe search.

        Returns:
            Union[List[SearchResult], List[None]]:
                A list of SearchResult objects if found, or empty list otherwise.

        Raises:
            EngineError: If the network session is uninitialized.
            InvalidAPIKeyError: If the API key is invalid.
            APILimitExceededError: If API quota is exceeded.
            NetworkError: For connection-related issues.
            UnexpectedResponseError: For unexpected HTTP responses.
        """
        if self._network is None:
            raise EngineError(
                "Network session is not initialized. Use async context manager."
            )

        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": q,
            "num": num,
            "start": start,
            "lr": lr,
            "gl": gl,
            "cr": cr,
            "safe": safe,
            "sort": sort,
            "filter": filter,
            "exactTerms": exactTerms,
            "excludeTerms": excludeTerms,
            "siteSearch": siteSearch,
            "siteSearchFilter": siteSearchFilter,
            "dateRestrict": dateRestrict,
            "fileType": fileType,
            "rights": rights,
            "fields": fields,
            "c2coff": c2coff,
            "hl": hl,
            "imgSize": imgSize,
            "imgType": imgType,
            "imgColorType": imgColorType,
            "imgDominantColor": imgDominantColor,
            "searchType": searchType,
            "googlehost": googlehost,
            "lowRange": lowRange,
            "highRange": highRange,
            "linkSite": linkSite,
            "hq": hq,
            "imgFilter": imgFilter,
        }

        params = {key: value for key, value in params.items() if value is not None}

        try:
            data = await self._network.request(params)
        except (
            InvalidAPIKeyError,
            APILimitExceededError,
            NetworkError,
            UnexpectedResponseError,
            EngineError,
        ) as exc:
            raise exc

        items = data.get("items", [])
        return [
            SearchResult(item)
            for item in items
        ]
