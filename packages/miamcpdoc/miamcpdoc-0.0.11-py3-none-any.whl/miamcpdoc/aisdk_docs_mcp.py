from miamcpdoc.main import create_server

def main():
    """AI SDK Documentation MCP Server."""
    doc_sources = [
        {"name": "VercelAISDK", "llms_txt": "https://ai-sdk.dev/llms.txt"}
    ]
    
    server = create_server(doc_sources)
    server.run(transport="stdio")

if __name__ == "__main__":
    main()