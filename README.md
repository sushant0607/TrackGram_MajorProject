# TrackGram – Social Media Forensic Documentation Tool

TrackGram is a Python-based OSINT (Open Source Intelligence) tool designed to extract and document publicly accessible Instagram profile metadata and image posts for forensic and investigative purposes.

The tool analyzes publicly available information from a target profile and generates a structured evidence report that can be used for documentation or investigative analysis.

The application is built using Streamlit for the interface and uses HTTP requests to retrieve publicly accessible data.

---

## Key Features

- Extracts publicly available Instagram profile metadata
- Retrieves image posts from public accounts
- Performs post-level analysis including:
  - captions
  - timestamps
  - engagement metrics (likes and comments)
  - accessibility captions
  - geolocation information
- Displays profile information and media content in an interactive interface
- Allows sorting posts by likes, comments, or date
- Exports raw data in JSON format
- Generates a structured PDF evidence report for documentation purposes

---

## Technology Stack

- Python
- Streamlit
- HTTPX
- FPDF
- Pillow (PIL)
- JSON

---

## How the Tool Works

1. The user enters an Instagram username.
2. The application sends a request to Instagram's public profile endpoint.
3. Publicly accessible profile metadata is extracted and parsed.
4. Image posts from the profile are retrieved and analyzed.
5. The data is displayed in a structured Streamlit interface.
6. The tool allows exporting:
   - Raw data in JSON format
   - A structured PDF forensic evidence report.

---

## Installation

Clone the repository.

```bash
git clone https://github.com/yourusername/trackgram.git
cd trackgram