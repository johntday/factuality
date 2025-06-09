import datetime
import json
import os
import re
from dotenv import load_dotenv
from factuality.api.gist import GistManager
from factuality.utils import logging
from factuality.utils.defaults import Defaults
from factuality.utils.options import Options
from factuality.runner.factuality import Factuality
from rich.console import Console
from rich.markdown import Markdown
from collections import defaultdict


load_dotenv()
import argparse

def strtobool(val: str | bool) -> bool:
    if isinstance(val, bool):
        return val
    return val.lower() in ("true", "1", "t")


def main():
    parser = argparse.ArgumentParser(
        description="Factuality CLI: Fact-check any statement using ChatGPT with integrated search options (Bing or Google). Generates a markdown table summarizing the claim, verification result, source references, and direct quotes from these sources. Designed for quick verification and summarization to assist in distinguishing factual information from misinformation."
    )
    parser.add_argument(
        "--statement",
        "-s",
        type=str,
        help="Statement to fact-check can be text or path to a text file",
        required=True,
    )
    parser.add_argument(
        "--id",
        type=str,
        help="tweet id",
        required=False,
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="The output format for the fact-check results. Default is console. Supported formats: console, markdown, json.",
        default=os.getenv("OUTPUT_FORMAT", Defaults.OUTPUT_FORMAT.value),
    )
    parser.add_argument(
        "--output-path",
        type=str,
        help="The output path for the fact-check results. Default is the folder the script is run from.",
        default=os.getenv("OUTPUT_PATH", Defaults.OUTPUT_PATH.value),
    )
    parser.add_argument(
        "--search-engine",
        type=str,
        help="The search engine to use for extracting articles. Default is Bing. Supported search engines: Bing, Google.",
        default=os.getenv("SEARCH_ENGINE", Defaults.SEARCH_ENGINE.value),
    )
    parser.add_argument(
        "--log-level",
        type=str,
        help="Log level for the logger. Default is INFO. Supported log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.",
        default=os.getenv("LOG_LEVEL", Defaults.LOG_LEVEL.value),
    )
    parser.add_argument(
        "--oai-api-key",
        required=False,
        type=str,
        default=os.getenv("OPENAI_API_KEY"),
        help="OpenAI API key",
    )
    parser.add_argument(
        "--allowlist",
        type=str,
        default=os.getenv(
            "ALLOWLIST", Defaults.ALLOWLIST.value
        ),
        help="List of domains to allow for search results (allowlist takes precedence over blocklist). Default is empty. Format ['domain1.com', 'domain2.com']",
    )
    parser.add_argument(
        "--blocklist",
        type=str,
        default=os.getenv(
            "BLOCKLIST", Defaults.BLOCKLIST.value
        ),
        help="List of domains to block for search results (allowlist takes precedence over blocklist). Default is empty. Format ['domain1.com', 'domain2.com']",
    )
    parser.add_argument(
        "--validation-checks-per-claim",
        type=int,
        default=os.getenv(
            "VALIDATION_CHECKS_PER_CLAIM", Defaults.VALIDATION_CHECKS_PER_CLAIM.value
        ),
        help="How many resources will factuality use the verify a claim. Default is 1.",
    )
    parser.add_argument(
        "--same-site-allowed",
        type=str,
        default=os.getenv(
            "SAME_SITE_ALLOWED", f"{Defaults.SAME_SITE_ALLOWED.value}"
        ),
        help="If the same site is allowed to be used multiple times for the same claim. Default is True.",
    )
    parser.add_argument(
        "--bing-search-v7-subscription-key",
        type=str,
        default=os.getenv("BING_SEARCH_V7_SUBSCRIPTION_KEY"),
        help="Bing Search V7 Subscription Key",
    )
    parser.add_argument(
        "--bing-search-v7-endpoint",
        type=str,
        default=os.getenv(
            "BING_SEARCH_V7_ENDPOINT", Defaults.BING_SEARCH_V7_ENDPOINT.value
        ),
        help="Bing Search V7 Endpoint URL",
    )
    parser.add_argument(
        "--google-search-api-key",
        type=str,
        default=os.getenv("GOOGLE_SEARCH_API_KEY"),
        help="Google Search API Key",
    )
    parser.add_argument(
        "--tavily-api-key",
        type=str,
        default=os.getenv("TAVILY_API_KEY"),
        help="Tavily Search API Key",
    )
    parser.add_argument(
        "--google-search-cx",
        type=str,
        default=os.getenv("GOOGLE_SEARCH_CX"),
        help="Google Search identifier of the Programmable Search Engine",
    )
    parser.add_argument(
        "--openai-model-extract",
        type=str,
        default=os.getenv("OPENAI_MODEL_EXTRACT", Defaults.OPENAI_MODEL_EXTRACT.value),
        help="OpenAI Model for Extract",
    )
    parser.add_argument(
        "--openai-model-factcheck",
        type=str,
        default=os.getenv(
            "OPENAI_MODEL_FACTCHECK", Defaults.OPENAI_MODEL_FACTCHECK.value
        ),
        help="OpenAI Model for Fact Check",
    )
    parser.add_argument(
        "--openai-model-conclusion",
        type=str,
        default=os.getenv(
            "OPENAI_MODEL_CONCLUSION", Defaults.OPENAI_MODEL_CONCLUSION.value
        ),
        help="OpenAI Model for Conclusion",
    )
    parser.add_argument(
        "--search-extract-article-length",
        type=int,
        default=os.getenv(
            "SEARCH_EXTRACT_ARTICLE_LENGTH",
            Defaults.SEARCH_EXTRACT_ARTICLE_LENGTH.value,
        ),
        help="Search Extract Article Length",
    )
    parser.add_argument(
        "--search-extract-article-overlap",
        type=int,
        default=os.getenv(
            "SEARCH_EXTRACT_ARTICLE_OVERLAP",
            Defaults.SEARCH_EXTRACT_ARTICLE_OVERLAP.value,
        ),
        help="Search Extract Article Overlap",
    )
    parser.add_argument(
        "--maximum-search-results",
        type=int,
        default=os.getenv(
            "MAXIMUM_SEARCH_RESULTS", Defaults.MAXIMUM_SEARCH_RESULTS.value
        ),
        help="Maximum Search Results",
    )

    args = parser.parse_args()

    if not os.getenv('OPENAI_API_KEY') and not args.oai_api_key:
        raise ValueError("At least one of 'env OPENAI_API_KEY' or 'cmd oai_api_key' must be set")

    options = Options(
        oai_api_key=args.oai_api_key,
        bing_search_v7_subscription_key=args.bing_search_v7_subscription_key,
        bing_search_v7_endpoint=args.bing_search_v7_endpoint,
        openai_model_extract=args.openai_model_extract,
        openai_model_factcheck=args.openai_model_factcheck,
        openai_model_conclusion=args.openai_model_conclusion,
        search_extract_article_length=args.search_extract_article_length,
        search_extract_article_overlap=args.search_extract_article_overlap,
        maximum_search_results=args.maximum_search_results,
        output_format=args.output,
        tweet_id=args.id,
        output_path=args.output_path,
        search_engine=args.search_engine,
        allowlist=args.allowlist,
        blocklist=args.blocklist,
        validation_checks_per_claim=args.validation_checks_per_claim,
        same_site_allowed=args.same_site_allowed,
        google_search_api_key=args.google_search_api_key,
        tavily_api_key=args.tavily_api_key,
        google_search_cx=args.google_search_cx,
    )
    if not options.tweet_id and options.output_format == "json":
        raise ValueError("Missing tweet ID parameter '--id'")

    logging.setup_structlog()
    if args.log_level:
        logging.change_log_level(args.log_level)
    else:
        logging.change_log_level(logging.INFO)
    factuality = Factuality(options)
    conclusion, checked_claims, statement = factuality.check(args.statement)
    statement_part = re.sub(r'[^\x00-\x7F]+', '', statement[:20].replace(' ', '_'))
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{statement_part}_{current_time}"

    def do_gist(markdown_text: str, filename: str) -> str | None:
        try:
            gist_manager = GistManager()

            response = gist_manager.create_gist(
                content=markdown_text,
                filename=f"{filename}.md",
                description=f"{conclusion.description[:254]}",
                public=True
            )
            return response['html_url']
        except Exception as e:
            print(f"Error creating gist: {str(e)}")

    gist_url = None
    if options.output_format == "markdown":
        with open(f"{options.output_path}/{filename}.md", "w") as f:
            markdown_text = factuality.convert_conclusions_to_markdown(
                checked_claims, statement, conclusion
            )
            if strtobool(os.getenv('GITHUB_GIST_ENABLED')):
                do_gist(markdown_text, filename)
            f.write(markdown_text)
    elif options.output_format == "json":
        # markdown_text = factuality.convert_conclusions_to_markdown(
        #     checked_claims, statement, conclusion
        # )

        # if strtobool(os.getenv('GITHUB_GIST_ENABLED')):
        #     gist_url = do_gist(markdown_text, filename)

        output_json = {
            'id': options.tweet_id,
            'factuality': {
                "statement": statement,
                "claims": transform_claims( [claim.model_dump(by_alias=True) for claim in checked_claims] ),
                "conclusion": conclusion.model_dump(by_alias=True),
            },
            # 'gist_url': gist_url,
        }

        print( json.dumps( output_json ) )
    elif options.output_format == "console":
        markdown_text = factuality.convert_conclusions_to_markdown(
            checked_claims, statement, conclusion
        )

        if strtobool(os.getenv('GITHUB_GIST_ENABLED')):
            gist_url = do_gist(markdown_text, filename)

        console = Console()
        console.print(Markdown(markdown_text))
        if strtobool(os.getenv('GITHUB_GIST_ENABLED')):
            console.print(gist_url)
        pass


def transform_claims(data):
    # Process claims into grouped structure
    claim_map = defaultdict(lambda: {
        "claim": None,
        "reference": None,
        "verification_query": None,
        "evidence": []
    })

    for claim in data["factuality"]["claims"]:
        key = (claim["claim"], claim["verification_query"])
        entry = claim_map[key]
        entry["claim"] = claim["claim"]
        entry["reference"] = claim.get("reference")
        entry["verification_query"] = claim["verification_query"]
        entry["evidence"].append({
            "result": claim["result"],
            "source_reference": claim["source_reference"],
            "source_quote": claim["source_quote"]
        })

    # Rebuild the output structure
    claims = list(claim_map.values()),
    return claims


if __name__ == "__main__":
    main()
