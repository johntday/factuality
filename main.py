
def main():
    print("Hello from factuality!")


    from tavily import TavilyClient
    tavily_client = TavilyClient(api_key="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")
    response = tavily_client.search("Who is Leo Messi?")

    print(response)


if __name__ == "__main__":
    main()
