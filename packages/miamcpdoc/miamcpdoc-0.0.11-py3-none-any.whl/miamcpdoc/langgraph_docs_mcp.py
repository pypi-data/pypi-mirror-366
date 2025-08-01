from miamcpdoc.main import create_server

def main():
    """LangGraph and LangChain Documentation MCP Server."""
    doc_sources = [
        {"name": "LangGraph", "llms_txt": "https://langchain-ai.github.io/langgraph/llms.txt"},
        {"name": "LangChain", "llms_txt": "https://python.langchain.com/llms.txt"}
    ]
    
    server = create_server(doc_sources)
    server.run(transport="stdio")

if __name__ == "__main__":
    main()