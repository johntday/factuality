from tavily import TavilyClient

class TavilySearchClient:
    tavily_client = None

    def __init__(self, subscription_key):
        if not self.tavily_client:
            self.tavily_client = TavilyClient(api_key=subscription_key)

    def search(self, query, maximum_search_results, allowlist, blocklist):
        """
        Search for a query string using Tavily Search API.

        Parameters:
        query (str): The search query.

        Returns:
        dict: The JSON response from the API.
        """

        response = self.tavily_client.search(
            query,
            max_results=maximum_search_results,
            exclude_domains=blocklist,
        )

        return response
