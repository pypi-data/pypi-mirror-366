from miamcpdoc.main import create_server

def main():
    """Hugging Face Documentation MCP Server."""
    doc_sources = [
        {"name": "HuggingFaceaccelerate", "llms_txt": "https://huggingface-projects-docs-llms-txt.hf.space/accelerate/llms.txt"},
        {"name": "HuggingFaceDiffusers", "llms_txt": "https://huggingface-projects-docs-llms-txt.hf.space/diffusers/llms.txt"},
        {"name": "HuggingFaceHub", "llms_txt": "https://huggingface-projects-docs-llms-txt.hf.space/hub/llms.txt"},
        {"name": "HuggingFacePython", "llms_txt": "https://huggingface-projects-docs-llms-txt.hf.space/huggingface_hub/llms.txt"},
        {"name": "HuggingFaceTransformers", "llms_txt": "https://huggingface-projects-docs-llms-txt.hf.space/transformers/llms.txt"}
    ]
    
    server = create_server(doc_sources)
    server.run(transport="stdio")

if __name__ == "__main__":
    main()