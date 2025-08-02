import requests
import os
import xml.etree.ElementTree as ET
from .arxiv_data import ArxivPaper
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def fetch_arxiv_xml(url: str) -> str:
    """
    Fetch XML data from the arXiv API.
    :param url: URL to fetch XML data from.
    :return: XML data as a string.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def parse_arxiv_xml(xml_data) -> list[ArxivPaper]:
    """
    Parse XML data from the arXiv API and extract relevant information.
    :param xml_data: XML data as a string.
    :return: List of dictionaries containing paper details.
    """
    root = ET.fromstring(xml_data)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    results: list[ArxivPaper] = []

    for entry in root.findall('atom:entry', ns):
        title_elem = entry.find('atom:title', ns)
        title = (
            title_elem.text.strip()
            if title_elem is not None and title_elem.text is not None
            else ''
        )
        summary_elem = entry.find('atom:summary', ns)
        summary = (
            summary_elem.text.strip()
            if summary_elem is not None and summary_elem.text is not None
            else ''
        )
        id_elem = entry.find('atom:id', ns)
        arxiv_id = (
            id_elem.text.split('/')[-1]
            if id_elem is not None and id_elem.text is not None
            else ''
        )
        # Find the link with rel="alternate" (main page)
        link = ''
        for link_elem in entry.findall('atom:link', ns):
            if link_elem.attrib.get('rel') == 'alternate':
                link = link_elem.attrib.get('href', '')
                break
        # Get authors
        authors: list[str] = []
        for author in entry.findall('atom:author', ns):
            name_elem = author.find('atom:name', ns)
            if name_elem is not None and name_elem.text is not None:
                authors.append(name_elem.text.strip())

        results.append(ArxivPaper(
            title=title,
            summary=summary,
            arxiv_id=arxiv_id,
            link=link,
            authors=authors
        ))

    return results


def _create_documents(
    paper: ArxivPaper,
    path: str,
    **kwargs
) -> list[Document]:
    """
    Create documents from the downloaded PDF file.
    :param paper: ArxivPaper object containing paper details.
    :param path: Local file path where the PDF is saved.
    :param kwargs: Additional keyword arguments for the PyPDFLoader.
    :return: List of Document objects.
    """
    metadata: dict = {
        'title': paper.title,
        'summary': paper.summary,
        'arxiv_id': paper.arxiv_id,
        'link': paper.link,
        'authors': paper.authors
    }

    # Load the PDF and set documents
    loader = PyPDFLoader(path, **kwargs)
    docs = loader.load()
    if not docs:
        print(f"No documents found in {path}.")
        return []
    # Update metadata for each document
    for doc in docs:
        doc.metadata.update(metadata)

    return docs


def _download_paper(paper: ArxivPaper, path_download: str) -> tuple[str, bool]:
    """
    Download the PDF file of the paper.
    :param paper: ArxivPaper object containing paper details.
    :param path_download: Local directory path where the PDF will be saved.
    :return: Local file path where the PDF is saved.
    """
    # Make a request to download the PDF
    response = requests.get(paper.link, stream=True)
    response.raise_for_status()

    # Use the arxiv_id to create a unique filename
    filename = os.path.join(path_download, f"paper.{paper.arxiv_id}.pdf")

    # Check if the file already exists
    if os.path.exists(filename):
        print(f"File {filename} already exists. Skipping download.")
        paper.set_path(filename)
        # Load the PDF and set documents
        loader = PyPDFLoader(filename)
        paper.set_documents(loader.load())
        return filename, True

    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return filename, False


async def export_papers(
    search: str,
    path_download: str,
    max_results: int = 5,
    **kwargs
):
    """
    Export papers from arXiv based on a search query.
    Asynchronously fetches paper details, downloads PDFs,
    and creates documents.
    :param search: Search query string.
    :param max_results: Maximum number of results to return.
    :return: List of dictionaries containing paper details.
    """
    # Ensure the download directory exists
    os.makedirs(path_download, exist_ok=True)

    url = (
        f'https://export.arxiv.org/api/query?search_query=all:"{search}"'
        f'&start=0&max_results={max_results}'
        f'&sortBy=submittedDate&sortOrder=descending'
    )
    xml_data = fetch_arxiv_xml(url)
    papers: list[ArxivPaper] = parse_arxiv_xml(xml_data)
    for paper in papers:
        # Download the PDF file
        if not paper.link:
            continue
        # Replace 'abs' with 'pdf' in the link to get the PDF URL
        if not paper.link.endswith('.pdf'):
            # Ensure the link is in the correct format for PDF download
            if 'abs' in paper.link:
                paper.link = paper.link.replace('abs', 'pdf')
        # Download the PDF file
        if not paper.link:
            continue

        # Download the PDF file
        if not path_download.endswith('/'):
            path_download += '/'

        # Download the paper and set the local path
        filename, is_exist = _download_paper(paper, path_download)
        paper.set_path(os.path.join(path_download, filename))

        # Create documents from the downloaded PDF
        docs = _create_documents(paper, filename, **kwargs)
        paper.set_documents(docs)
        paper.set_is_exist(is_exist)
        yield paper
