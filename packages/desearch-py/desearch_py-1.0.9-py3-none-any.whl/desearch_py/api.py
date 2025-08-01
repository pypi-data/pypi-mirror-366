import requests
import logging
from typing import Any, Dict, Union, List

from openai import OpenAI

from .protocol import (
    AISearchResponse,
    WebLinksSearchResponse,
    TwitterLinksSearchResponse,
    BasicTwitterSearchResponse,
    BasicWebSearchResponse,
    ToolEnum,
    ModelEnum,
    DateFilterEnum,
    TwitterByIdResponse,
    ResultTypeEnum,
    WebToolEnum,
    TwitterUserResponse,
)
from .openai_utils import wrap_openai_client


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Desearch:
    """
    SDK for interacting with the Desearch API.

    Attributes:
        client (requests.Session): The HTTP client used for making requests.
        base_url (str): The base URL for the API.
    """

    BASE_URL = "https://api.desearch.ai"
    AUTH_HEADER = "Authorization"

    def __init__(self, api_key: str):
        """
        Initializes the DesearchApiSDK with the provided API key.

        Args:
            api_key (str): The API key for authenticating requests.
        """
        self.client = requests.Session()
        self.client.headers.update({self.AUTH_HEADER: api_key})

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def handle_request(self, request_func, *args, **kwargs) -> Dict[str, Any]:
        """
        Handles HTTP requests and processes responses.

        Args:
            request_func (callable): The HTTP request function (e.g., self.client.post).
            *args: Positional arguments for the request function.
            **kwargs: Keyword arguments for the request function.

        Returns:
            Dict[str, Any]: The JSON response from the server.

        Raises:
            requests.exceptions.HTTPError: If an HTTP error occurs.
            requests.exceptions.RequestException: If a network error occurs.
        """
        try:
            response = request_func(*args, timeout=120, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP Error [{response.status_code}]: {response.text}")
            raise
        except requests.exceptions.RequestException as err:
            logger.error(f"Network Error: {err}")
            raise

    def ai_search(
        self,
        prompt: str,
        tools: List[ToolEnum],
        # model: ModelEnum,
        date_filter: DateFilterEnum = None,
        streaming: bool = None,
        result_type: ResultTypeEnum = None,
        system_message: str = None,
        count: int = 10,
    ) -> Union[AISearchResponse, dict, str]:
        """
        Performs an AI search with the given payload.

        Args:
            payload (AISearchPayload): The payload for the AI search.

        Returns:
            Union[AISearchResponse, dict, str]
        """
        payload = {
            k: v
            for k, v in {
                "prompt": prompt,
                "tools": tools,
                # "model": model,
                "date_filter": date_filter,
                "streaming": streaming,
                "result_type": result_type,
                "system_message": system_message,
                "count": count,
            }.items()
            if v is not None
        }

        if streaming:
            response = self.client.post(
                f"{self.BASE_URL}/desearch/ai/search", json=payload, stream=True
            )
            response.raise_for_status()
            return response.iter_content(chunk_size=8192)

        return self.handle_request(
            self.client.post, f"{self.BASE_URL}/desearch/ai/search", json=payload
        )

    def deep_research(
        self,
        prompt: str,
        tools: List[ToolEnum],
        # model: ModelEnum,
        date_filter: DateFilterEnum = None,
        streaming: bool = None,
        system_message: str = None,
    ) -> str:
        """
        Performs an Deep research with the given payload.

        Args:
            payload (DeepResearchPayload): The payload for the Deep research.

        Returns:
            str
        """
        payload = {
            k: v
            for k, v in {
                "prompt": prompt,
                "tools": tools,
                # "model": model,
                "date_filter": date_filter,
                "streaming": streaming,
                "system_message": system_message,
            }.items()
            if v is not None
        }

        if streaming:
            response = self.client.post(
                f"{self.BASE_URL}/desearch/deep/search", json=payload, stream=True
            )
            response.raise_for_status()
            return response.iter_content(chunk_size=8192)

        return self.handle_request(
            self.client.post, f"{self.BASE_URL}/desearch/deep/search", json=payload
        )

    def web_links_search(
        self, prompt: str, tools: List[WebToolEnum], count: int = 10
    ) -> WebLinksSearchResponse:
        """
        Searches for web links with the given payload.

        Args:
            payload (WebLinksPayload): The payload for the web links search.

        Returns:
            WebLinksSearchResponse: The response from the web links search.
        """
        payload = {"prompt": prompt, "tools": tools, "count": count}
        response = self.handle_request(
            self.client.post,
            f"{self.BASE_URL}/desearch/ai/search/links/web",
            json=payload,
        )
        return WebLinksSearchResponse(**response)

    def twitter_links_search(
        self, prompt: str, count: int = 10
    ) -> TwitterLinksSearchResponse:
        """
        Searches for Twitter links with the given payload.

        Args:
            payload (TwitterLinksPayload): The payload for the Twitter links search.

        Returns:
            TwitterLinksSearchResponse: The response from the Twitter links search.
        """
        payload = {"prompt": prompt, "count": count}
        response = self.handle_request(
            self.client.post,
            f"{self.BASE_URL}/desearch/ai/search/links/twitter",
            json=payload,
        )
        return response

    def basic_twitter_search(
        self,
        query: str,
        sort: str = None,
        user: str = None,
        start_date: str = None,
        end_date: str = None,
        lang: str = None,
        verified: bool = None,
        blue_verified: bool = None,
        is_quote: bool = None,
        is_video: bool = None,
        is_image: bool = None,
        min_retweets: int = None,
        min_replies: int = None,
        min_likes: int = None,
        count: int = 10,
    ) -> BasicTwitterSearchResponse:
        """
        Performs a basic Twitter search with the given payload.

        Args:
            payload (TwitterSearchPayload): The payload for the Twitter search.

        Returns:
            BasicTwitterSearchResponse: The response from the Twitter search.

        Example:
            {
                "query": "Whats going on with Bittensor",
                "sort": "Top",
                "user": "elonmusk",
                "start_date": "2024-12-01",
                "end_date": "2025-02-25",
                "lang": "en",
                "verified": true,
                "blue_verified": true,
                "is_quote": true,
                "is_video": true,
                "is_image": true,
                "min_retweets": 1,
                "min_replies": 1,
                "min_likes": 1,
                "count": 10
            }
        """
        payload = {
            k: v
            for k, v in {
                "query": query,
                "sort": sort,
                "user": user,
                "start_date": start_date,
                "end_date": end_date,
                "lang": lang,
                "verified": verified,
                "blue_verified": blue_verified,
                "is_quote": is_quote,
                "is_video": is_video,
                "is_image": is_image,
                "min_retweets": min_retweets,
                "min_replies": min_replies,
                "min_likes": min_likes,
                "count": count,
            }.items()
            if v is not None
        }
        response = self.handle_request(
            self.client.get, f"{self.BASE_URL}/twitter", params=payload
        )
        return response

    def basic_web_search(
        self, query: str, num: int, start: int
    ) -> BasicWebSearchResponse:
        """
        Performs a basic web search with the given payload.

        Args:
            payload (WebSearchPayload): The payload for the web search.

        Returns:
            BasicWebSearchResponse: The response from the web search.
        """
        payload = {"query": query, "num": num, "start": start}
        response = self.handle_request(
            self.client.get, f"{self.BASE_URL}/web", params=payload
        )
        return response

    def web_crawl(self, url: str) -> str:
        """
        Performs a web crawl with the given url.

        Args:
            url: The url of the website to crawl.

        Returns:
            str: The content of the website.
        """
        payload = {"url": url}
        response = self.client.get(f"{self.BASE_URL}/web/crawl", params=payload)
        response.raise_for_status()
        return response.content.decode("utf-8")

    def twitter_by_urls(self, urls: List[str]) -> List[TwitterByIdResponse]:
        """
        Performs a Twitter search by URLs with the given payload.

        Args:
            payload (TwitterByUrlsPayload): The payload for the Twitter search by URLs.

        Returns:
            TwitterByUrlsResponse: The response from the Twitter search by URLs.
        """
        payload = {"urls": urls}
        response = self.handle_request(
            self.client.get, f"{self.BASE_URL}/twitter/urls", params=payload
        )

        return response

    def twitter_by_id(self, id: str) -> TwitterByIdResponse:
        """
        Performs a Twitter search by IDs with the given payload.

        Args:
            payload (TwitterByIdPayload): The payload for the Twitter search by ID.

        Returns:
            TwitterByIdResponse: The response from the Twitter search by ID.
        """
        response = self.handle_request(
            self.client.get,
            f"{self.BASE_URL}/twitter/post",
            params={"id": id},
        )

        return TwitterByIdResponse(**response)

    def tweets_by_user(
        self, user: str, query: int = None, count: int = 10
    ) -> BasicTwitterSearchResponse:
        """
        Performs a twitter search with the given arguments.

        Args:
            user (str): The user to search for.
            query (str): The query to search for.
            count (int): The number of tweets to return.

        Returns:
            BasicTwitterSearchResponse: The response from the web search.
        """
        payload = {"user": user, "query": query, "count": count}
        response = self.handle_request(
            self.client.get, f"{self.BASE_URL}/twitter/post/user", params=payload
        )
        return response

    def latest_tweets(self, user: str, count: int = 10) -> BasicTwitterSearchResponse:
        """
        Performs a latest tweets search with the given arguments.

        Args:
            user (str): The user to search for.
            count (int): The number of tweets to return.

        Returns:
            BasicTwitterSearchResponse: The response from the web search.
        """
        payload = {"user": user, "count": count}
        response = self.handle_request(
            self.client.get, f"{self.BASE_URL}/twitter/latest", params=payload
        )
        return response

    def tweets_and_replies_by_user(
        self, user: str, query: int = None, count: int = 10
    ) -> BasicTwitterSearchResponse:
        """
        Performs a tweets and replies search with the given arguments.

        Args:
            user (str): The user to search for.
            query (str): The query to search for.
            count (int): The number of tweets to return.

        Returns:
            BasicTwitterSearchResponse: The response from the web search.
        """
        payload = {"user": user, "query": query, "count": count}
        response = self.handle_request(
            self.client.get, f"{self.BASE_URL}/twitter/replies", params=payload
        )
        return response

    def twitter_replies_post(
        self, post_id: str, count: int = 10, query: str = ""
    ) -> BasicTwitterSearchResponse:
        """
        Performs a tweets and replies search with the given arguments.

        Args:
            post_id (str): The post id to search for.
            count (int): The number of tweets to return.
            query (str): The query to search for.

        Returns:
            BasicTwitterSearchResponse: The response from the web search.
        """
        payload = {"post_id": post_id, "count": count, "query": query}
        response = self.handle_request(
            self.client.get, f"{self.BASE_URL}/twitter/replies/post", params=payload
        )
        return response

    def twitter_retweets_post(
        self, post_id: str, count: int = 10, query: str = ""
    ) -> BasicTwitterSearchResponse:
        """
        Performs a tweets and replies search with the given arguments.

        Args:
            post_id (str): The post id to search for.
            count (int): The number of tweets to return.
            query (str): The query to search for.

        Returns:
            BasicTwitterSearchResponse: The response from the web search.
        """
        payload = {"post_id": post_id, "count": count, "query": query}
        response = self.handle_request(
            self.client.get, f"{self.BASE_URL}/twitter/retweets/post", params=payload
        )
        return response

    def tweeter_user(self, user: str) -> TwitterUserResponse:
        """
        Performs a tweets and replies search with the given arguments.

        Args:
            user (str): The user to search for.

        Returns:
            TwitterUserResponse: The response from the web search.
        """
        payload = {"user": user}
        response = self.handle_request(
            self.client.get, f"{self.BASE_URL}/twitter/user", params=payload
        )
        return response

    def wrap(self, client: OpenAI):
        """
        Wrap an OpenAI client with Desearch functionality.

        This method delegates to the wrap_openai_client function in openai_utils.

        Args:
            client: The OpenAI client to wrap

        Returns:
            The wrapped OpenAI client with Desearch functionality
        """
        return wrap_openai_client(self, client)
