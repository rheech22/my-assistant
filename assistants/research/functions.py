from langchain.tools import DuckDuckGoSearchResults, WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper
from langchain.document_loaders import WebBaseLoader
from pathlib import Path


assistant_functions = [
    {
        "type": "function",
        "function": {
            "name": "search_by_duckduckgo",
            "description": "Given a query, returns a URL of relevant websites from DuckDuckGo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query to search for",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_by_wikipedia",
            "description": "Given a query, returns the summary of the query from Wikipedia.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query to search for",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "scrape_web_page",
            "description": "Given a URL, returns the content of the web page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the web page",
                    },
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_to_file",
            "description": "Given a text content, saves it to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text content to save",
                    },
                },
                "required": ["text"],
            },
        },
    },
]


def search_by_duckduckgo(inputs):
    query = inputs["query"]
    ddg = DuckDuckGoSearchResults()
    return ddg.run(query)


def search_by_wikipedia(inputs):
    query = inputs["query"]
    wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    return wiki.run(query)


def scrape_web_page(inputs):
    url = inputs["url"]
    loader = WebBaseLoader([url])
    docs = loader.load()
    text = "\n\n".join([doc.page_content for doc in docs])
    return text


def save_to_file(inputs):
    output_dir = "./output"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    text = inputs["text"]
    with open(f"{output_dir}/output.txt", "w") as file:
        file.write(text)
    return f"Text saved to {output_dir}/output.txt"


functions_map = {
    "search_by_duckduckgo": {
        "function": search_by_duckduckgo,
        "description": "Searching by DuckDuckGo",
    },
    "search_by_wikipedia": {
        "function": search_by_wikipedia,
        "description": "Searching by Wikipedia",
    },
    "scrape_web_page": {
        "function": scrape_web_page,
        "description": "Scraping web page",
    },
    "save_to_file": {
        "function": save_to_file,
        "description": "Saving to file",
    },
}
