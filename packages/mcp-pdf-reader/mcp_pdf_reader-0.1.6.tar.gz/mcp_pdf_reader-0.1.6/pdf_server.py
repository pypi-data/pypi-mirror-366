import os, json, base64, fitz, logging
from typing import Optional, List, Dict, Any, Union, Literal
from fastmcp import FastMCP

mcp = FastMCP("PDF Reader", version="0.1.0")

@mcp.tool()
def read_pdf_text(file_path: str, start_page: int = 1, end_page: Optional[int] = None) -> str:
    """
    Output PDF text content per page in markdown format.
    Args:
        file_path: Path to the PDF file
        start_page: Start page (1-based)
        end_page: End page (inclusive)
    Returns:
        Markdown formatted string
    """
    if not os.path.exists(file_path):
        PDF_DIR = os.environ.get("PDF_DIR")
        if not PDF_DIR:
            raise ValueError(f"File not found: {file_path}. Try using an absolute path or set the PDF_DIR environment variable.")  
        else:
            abs_path = os.path.abspath(file_path)
            raise ValueError(f"File not found: {file_path}\nTry using absolute path, current absolute path is: {abs_path}")

    doc = fitz.open(file_path)
    total_pages = len(doc)

    if start_page < 1:
        start_page = 1
    if end_page is None or end_page > total_pages:
        end_page = total_pages
    if start_page > end_page:
        start_page, end_page = end_page, start_page

    markdown = ""
    for page_num in range(start_page - 1, end_page):
        page = doc[page_num]
        page_text = page.get_text().strip()
        markdown += f"---------- page {page_num + 1} ----------\n"
        markdown += page_text + "\n"
    markdown += f"---------- total {end_page - start_page + 1} ----------\n"

    doc.close()
    return markdown


@mcp.tool()
def read_by_ocr(file_path: str, start_page: int = 1, end_page: Optional[int] = None,
        language: str = "eng", dpi: int = 300) -> Dict[str, Any]:
    """
    Read text from PDF file using OCR.
    Args:
        file_path: Path to the PDF file
        start_page: Start page (1-based)
        end_page: End page (inclusive)
        language: OCR language code
        dpi: OCR DPI
    Returns:
        Dict with extracted text, page_count, extracted_pages
    """
    if not os.path.exists(file_path):
        PDF_DIR = os.environ.get("PDF_DIR")
        if not PDF_DIR:
            raise ValueError(f"File not found: {file_path}. Try using an absolute path or set the PDF_DIR environment variable.")  
        else:
            abs_path = os.path.abspath(file_path)
            raise ValueError(f"File not found: {file_path}\nTry using absolute path, current absolute path is: {abs_path}")

    doc = fitz.open(file_path)
    total_pages = len(doc)

    if start_page < 1:
        start_page = 1
    if end_page is None or end_page > total_pages:
        end_page = total_pages
    if start_page > end_page:
        start_page, end_page = end_page, start_page

    text_content = ""
    for page_num in range(start_page - 1, end_page):
        page = doc[page_num]
        try:
            textpage = page.get_textpage_ocr(flags=3, language=language, dpi=dpi, full=True)
            page_text = page.get_text(textpage=textpage).strip()
        except Exception as e:
            logging.warning(f"OCR failed on page {page_num + 1}, fallback to normal text: {e}")
            page_text = page.get_text().strip()

        text_content += f"---------- page {page_num + 1} ----------\n"
        text_content += page_text + "\n"
    
    text_content += f"---------- total {end_page - start_page + 1} ----------\n"

    doc.close()

    return {"text": text_content, "page_count": total_pages,
        "extracted_pages": list(range(start_page, end_page + 1))}


@mcp.tool()
def read_pdf_to_file(file_paths: List[str], use_ocr: Literal["yes", "no"] = "no",
                     language: str = "eng", dpi: int = 300) -> Dict[str, List[str]]:
    """
    Convert multiple PDF files to TXT files
    Args:
        file_paths: List of PDF file paths
        use_ocr: Whether to use OCR, options are "yes" or "no"
        language: OCR language code, only effective when use_ocr="yes"
        dpi: OCR DPI value, only effective when use_ocr="yes"
    Returns:
        Dictionary containing paths to the converted TXT files
    """
    # Limit to processing maximum 20 files at once
    if len(file_paths) > 20:
        raise ValueError(f"Maximum 20 files can be processed at once, {len(file_paths)} files were provided")
    
    # Check if files exist
    for file_path in file_paths:
        if not os.path.exists(file_path):
            PDF_DIR = os.environ.get("PDF_DIR")
            if not PDF_DIR:
                raise ValueError(f"File not found: {file_path}. Try using an absolute path or set the PDF_DIR environment variable.")
            else:
                abs_path = os.path.abspath(file_path)
                raise ValueError(f"File not found: {file_path}\nTry using absolute path, current absolute path is: {abs_path}")
    
    output_paths = []
    for file_path in file_paths:
        # Generate output file path
        file_name, file_ext = os.path.splitext(file_path)
        output_path = file_name + ".txt"
        
        # Open PDF file
        doc = fitz.open(file_path)
        total_pages = len(doc)
        
        # Extract text content
        text_content = ""
        for page_num in range(total_pages):
            page = doc[page_num]
            
            if use_ocr == "yes":
                try:
                    textpage = page.get_textpage_ocr(flags=3, language=language, dpi=dpi, full=True)
                    page_text = page.get_text(textpage=textpage).strip()
                except Exception as e:
                    logging.warning(f"OCR failed on page {page_num + 1}, falling back to normal text extraction: {e}")
                    page_text = page.get_text().strip()
            else:
                page_text = page.get_text().strip()
            
            text_content += f"---------- page {page_num + 1} ----------\n"
            text_content += page_text + "\n"
        
        text_content += f"---------- total {total_pages} ----------\n"
        
        # Close PDF file
        doc.close()
        
        # Write to TXT file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text_content)
        
        output_paths.append(output_path)
    
    return {"output_files": output_paths}


def main():
    # Only change directory if PDF_DIR environment variable is set and valid
    PDF_DIR = os.environ.get("PDF_DIR")
    if PDF_DIR and os.path.exists(PDF_DIR):
        os.chdir(PDF_DIR)
    mcp.run(show_banner=False)

if __name__ == "__main__":
    main()
