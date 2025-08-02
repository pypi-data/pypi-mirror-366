# Arxix Export

**Arxiv Export** is a Python library that allows you to search, download, and manage scientific articles from [arXiv.org](https://arxiv.org/). It is useful for automating paper downloads and obtaining structured information about articles.

## Installation

```bash
pip install arxiv-export
```

## Usage Example

```python
import asyncio
from arxiv_export_documents import export_papers


async def main():
    search_query = "quantum computing"
    download_path = "./arxiv_papers"
    max_results = 5

    async for paper in export_papers(
        search=search_query,
        path_download=download_path,
        max_results=max_results
    ):
        print(f"Downloaded paper: {paper.title}")
        print(f"Authors: {', '.join(paper.authors)}")
        print(f"Summary: {paper.summary}")
        print(f"Link: {paper.link}")
        print(f"Path: {paper.path}")
        print(f"Documents: {len(paper.documents)}")
        print(f"Exists: {paper.is_exist}")
        print("-" * 80)


if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- Search for articles on arXiv using keywords.
- Automatically download article PDFs.
- Access metadata such as title, authors, abstract, link, and local path.
- Manage multiple results with a single command.

## Main Parameters

- `search`: search string (e.g., `"quantum computing"`).
- `path_download`: path to save the PDFs.
- `max_results`: maximum number of articles to download.

### Vector Database for LLMs

The `documents` property provides a list of `Document` files intended for ingestion into a vector database. These files are commonly used to supply structured data to language models (LLMs), supporting semantic search and advanced analysis.

## License

This library is distributed under the MIT license.