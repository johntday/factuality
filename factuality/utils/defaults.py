from enum import Enum

class Defaults(Enum):
    BING_SEARCH_V7_ENDPOINT = 'https://api.bing.microsoft.com/'
    OPENAI_MODEL_EXTRACT = 'gpt-4o'
    OPENAI_MODEL_FACTCHECK = 'gpt-4o'
    OPENAI_MODEL_CONCLUSION = 'gpt-4o'
    SEARCH_EXTRACT_ARTICLE_LENGTH = 5000
    SEARCH_EXTRACT_ARTICLE_OVERLAP = 500
    MAXIMUM_SEARCH_RESULTS = 5
    SEARCH_ENGINE = 'tavily'
    OUTPUT_FORMAT = 'console'
    OUTPUT_PATH = '.'
    ALLOWLIST = '[]'
    BLOCKLIST = '[]'
    VALIDATION_CHECKS_PER_CLAIM = 1
    SAME_SITE_ALLOWED = True
    LOG_LEVEL = 'INFO'