from langchain_core.documents import Document


class ArxivPaper:
    """
    Represents a paper from arXiv with its metadata.
    """
    title: str
    summary: str
    arxiv_id: str
    link: str
    authors: list[str]
    path: str
    documents: list[Document]
    is_exist: bool

    def __init__(self, title, summary, arxiv_id, link, authors):
        self.title = title
        self.summary = summary
        self.arxiv_id = arxiv_id
        self.link = link
        self.authors = authors

    def set_is_exist(self, is_exist: bool):
        """
        Set the existence status of the paper.
        :param is_exist: Boolean indicating if the paper already exists.
        """
        self.is_exist = is_exist

    def set_path(self, path):
        """
        Set the local path where the paper will be saved.
        :param path: Local file path.
        """
        self.path = path

    def set_documents(self, documents: list[Document]):
        """
        Set the documents associated with the paper.
        :param documents: List of Document objects.
        """
        self.documents = documents
