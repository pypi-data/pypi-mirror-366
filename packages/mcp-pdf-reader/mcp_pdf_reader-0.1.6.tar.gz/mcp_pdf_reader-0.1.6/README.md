# 📄 MCP PDF Server

A PDF file reading server based on [FastMCP](https://github.com/minimaxir/fastmcp).

Supports PDF text extraction, OCR recognition, and image extraction via the MCP protocol, with a built-in web debugger for easy testing.

---

## 🚀 Features

- **read_pdf_text**  
  Extracts normal text from a PDF (page by page).

- **read_by_ocr**  
  Uses OCR to recognize text from scanned or image-based PDFs.

- **read_pdf_to_file**  
  Converts PDF files to TXT files with optional OCR support.

---

## 📂 Project Structure

```
mcp-pdf-server/
├── pdf_server.py         # Main server entry point
└── README.md             # Project documentation
```

---

## ⚙️ Installation

Recommended Python version: 3.9+

```bash
pip install pymupdf mcp
```

> Note: To use OCR features, you may need a MuPDF build with OCR support or external OCR libraries.

## 🤖 Configuration

```json
{
  "mcpServers": {
    "pdf-reader": {
      "command": "uvx",
      "timeout": 60000,
      "args": [
        "mcp-pdf-reader"
      ]
    }
  }
}
```

---

## 🔦 Start the Server

Run the following command:

```bash
python pdf_server.py
```

You should see logs like:

```
INFO:mcp-pdf-server:Starting MCP PDF Server...
```

---

## 🛠️ API Tool List

| Tool | Description | Input Parameters | Returns |
|:-----|:------------|:-----------------|:--------|
| `read_pdf_text` | Extracts normal text from PDF pages | `file_path`, `start_page`, `end_page` | List of page texts |
| `read_by_ocr` | Recognizes text via OCR | `file_path`, `start_page`, `end_page`, `language`, `dpi` | OCR extracted text |
| `read_pdf_to_file` | Converts PDF files to TXT files | `file_paths`, `use_ocr`, `language`, `dpi` | Dictionary of generated TXT file paths |

---

## 📝 Example Usage

Extract text from pages 1 to 5:

```bash
mcp run read_pdf_text --args '{"file_path": "pdf_resources/example.pdf", "start_page": 1, "end_page": 5}'
```

Perform OCR recognition on page 1:

```bash
mcp run read_by_ocr --args '{"file_path": "pdf_resources/example.pdf", "start_page": 1, "end_page": 1, "language": "eng"}'
```

Convert PDF files to TXT files:

```bash
mcp run read_pdf_to_file --args '{"file_paths": ["pdf_resources/example.pdf"], "use_ocr": "no"}'
```

Convert PDF files with OCR support:

```bash
mcp run read_pdf_to_file --args '{"file_paths": ["pdf_resources/example.pdf"], "use_ocr": "yes", "language": "eng", "dpi": 300}'
```

---

## 📢 Notes

- Files must be placed inside the `pdf_resources/` directory, or an absolute path must be provided.
- OCR functionality requires appropriate OCR support in the environment.
- When processing large files, adjust memory and timeout settings as needed.

---

## 📜 License

This project is licensed under the MIT License.  
For commercial use, please credit the original source.

---