"""Loads word documents."""
from typing import List

from langchain_community.document_loaders import UnstructuredFileLoader


class PDFDocumentLoader(UnstructuredFileLoader):
    def _get_elements(self) -> List:
        from unstructured.partition.pdf import partition_pdf

        return partition_pdf(filename=self.file_path, **self.unstructured_kwargs)


class DocDocumentLoader(UnstructuredFileLoader):
    def _get_elements(self) -> List:
        from unstructured.partition.doc import partition_doc

        return partition_doc(filename=self.file_path, **self.unstructured_kwargs)


class DocxDocumentLoader(UnstructuredFileLoader):
    def _get_elements(self) -> List:
        from unstructured.partition.docx import partition_docx

        return partition_docx(filename=self.file_path, **self.unstructured_kwargs)
