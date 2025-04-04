from tavily import TavilyClient
import requests

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
        # params = {'mkt': "en-us", 'count': maximum_search_results}
        # headers = {'Ocp-Apim-Subscription-Key': self.subscription_key}
        #
        # q = query
        # if len(allowlist) > 0:
        #     q += " " + " OR ".join(map(lambda x: f"site:{x}", allowlist))
        # elif len(blocklist) > 0 and len(allowlist) == 0:
        #     q += " " + " OR ".join(map(lambda x: f"-site:{x}", blocklist))
        # params['q'] = q

        response = self.tavily_client.search(query)

        return response

    # from tavily import TavilyClient
    # tavily_client = TavilyClient(api_key="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")
    # response = tavily_client.search("Who is Leo Messi?")