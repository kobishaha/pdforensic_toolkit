
# 🕵️ PDFOrensic CLI - Documentation

A forensic command-line tool for analyzing PDF files: metadata, hidden objects, OCR, image extraction, text anomalies, etc.

---

## 🧠 Features

* Full support for** ****file or folder** input
* Detects** ****scanned** vs** ****digitally created** PDFs
* Handles** ** **multiple tools** :
  * `pdfinfo`,** **`exiftool`
  * `pdftotext`,** **`strings`,** **`grep`
  * `pdfimages`,** **`qpdf`,** **`mutool`
  * `ocrmypdf` /** **`tesseract`
  * `xxd`,** **`file`,** **`diff`
* **Interactive menu** if no arguments are given
* **Command-line flags** for automation
* **Output ZIP** , CSV and structure per run

---

## 🚀 Usage

```bash
python pdforensic_cli_ultimate.py [<file_or_folder>] [options]
```

### 🔤 Options

| Flag   | Tool             | Description                                     |
| ------ | ---------------- | ----------------------------------------------- |
| `-m` | Metadata         | Extract metadata with `pdfinfo`, `exiftool` |
| `-t` | Text             | Extract text with `pdftotext`                 |
| `-s` | Structure        | Analyze PDF internal structure                  |
| `-h` | Hidden text      | Find hidden layers and text                     |
| `-i` | Image extraction | Extract all embedded images                     |
| `-o` | OCR              | Run OCR (Tesseract or OCRmyPDF)                 |
| `-d` | Decode streams   | QPDF --qdf to unpack objects                    |
| `-a` | All              | Run all supported analyses                      |

If no arguments are passed, you'll be prompted:

1. For** ****file/folder path**
2. For** ****actions** to perform (A, M, T, etc.)

---

## 📁 Output Structure

Each run will generate:

* Folder:** **`forensic_results/<filename>_<timestamp>`
* Inside:
  * `pdf_info.txt`,** **`exif.json`,** **`text.txt`,** **`images/`,** **`ocr_output.pdf`,** **`ocr_output.txt`, etc.
  * Final:** **`summary.csv`,** **`output.zip`

---

## ⚙️ Config File (JSON)

We'll support external config for tools:

```json
{
  "metadata": {
    "flag": "m",
    "description": "Extract metadata",
    "commands": [
      "pdfinfo {input} > {output}/pdfinfo.txt",
      "exiftool -j {input} > {output}/exif.json"
    ]
  },
  "ocr": {
    "flag": "o",
    "description": "OCR scanned PDF",
    "commands": [
      "tesseract {image} {output}/ocr --dpi 300 -l heb+eng --psm 3 --oem 1"
    ]
  }
}
```

---

## 🧪 Examples

```bash
# Full folder run with all tools
python pdforensic_cli_ultimate.py ./src -a

# Only OCR
python pdforensic_cli_ultimate.py document.pdf -o

# Interactive
python pdforensic_cli_ultimate.py
```

---

## ✅ TODO

* [X] OCR integration (force + sidecar)
* [X] Menu UI with ASCII banner
* [X] Support folders and loop through files
* [X] Image pre-processing for OCR (grayscale, binarize)
* [ ] Generate ZIP + CSV summary for each run
* [ ] Add JSON config support
* [ ] Plugin support in future (pluggable tools)
* [ ] Add PDF comparison (diff)

---

## 💡 Future Ideas

* Markdown export with full breakdown
* Raycast / Droplet mini app
* Detect anomalies (OCR vs text mismatches)
* Deep fake detection via ELA + ML

---

## 👥 Contributing

Want to add a forensic trick? Add a new tool in the** **`tools_config.json` and submit a PR 💥
