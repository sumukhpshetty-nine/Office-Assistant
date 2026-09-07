# TechNova Office Assistant

An AI-powered office assistant for TechNova Pvt. Ltd. that helps employees access company policies, employee information, payroll details, leave balances, IT support, and office information through a Streamlit interface.

## Features

- Company policy question answering using PDF documents
- Gemini-powered intent classification
- Gemini-powered policy answer generation
- Local PDF text extraction
- Sentence-aware overlapping text chunking
- Sentence Transformer embeddings
- FAISS vector database for semantic search
- Employee information lookup
- Employee leave-balance lookup
- Payroll and salary information lookup
- IT support queries
- Office location queries
- Intent-based request routing
- Streamlit user interface

## Project Architecture

```text
Office_Assistant/
│
├── app.py
├── README.md
├── .gitignore
├── requirements.txt
├── .env
│
├── data/
│   └── documents/
│       └── company_policy.pdf
│
├── person1/
│   └── p1_rag.py
│
└── src/
    ├── agents/
    │   ├── intent_agent.py
    │   ├── router.py
    │   ├── employee_agent.py
    │   ├── payroll_agent.py
    │   └── it_support_agent.py
    │
    └── tools/
        ├── leave_tool.py
        └── office_tool.py
```

## How It Works

```text
Employee Query
      │
      ▼
Streamlit Interface
      │
      ▼
Gemini Intent Classification
      │
      ├── Policy Query ───────► PDF RAG
      │                              │
      │                              ▼
      │                       FAISS Retrieval
      │                              │
      │                              ▼
      │                       Gemini Answer
      │
      ├── Employee Query ────► Employee Agent
      │
      ├── Payroll Query ─────► Payroll Agent
      │
      ├── Leave Query ───────► Leave Tool
      │
      ├── IT Query ──────────► IT Support Agent
      │
      └── Office Query ──────► Office Tool
```

## Technologies Used

- Python
- Streamlit
- Google Gemini API
- Google Gen AI SDK
- Sentence Transformers
- FAISS
- PyPDF
- NumPy
- Pandas
- JSON
- python-dotenv

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/sumukhpshetty-nine/Office-Assistant.git
cd Office-Assistant
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the Gemini API

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

You can obtain a Gemini API key from:

https://aistudio.google.com/app/apikey

**Never commit your `.env` file or API key to GitHub.**

## Running the Application

From the project root:

```bash
streamlit run app.py
```

The application will open in your browser.

## Running the RAG Pipeline Separately

```bash
python person1/p1_rag.py
```

This will:

1. Load company policy PDFs
2. Extract text from the PDFs
3. Create overlapping text chunks
4. Generate embeddings
5. Build a FAISS index
6. Retrieve relevant policy chunks
7. Generate answers using Gemini
8. Display the retrieved sources

## Example Queries

```text
What is the work from home policy?
```

```text
What is my department?
```

```text
Who is my manager?
```

```text
What is my annual salary?
```

```text
How many leaves do I have?
```

```text
Where is the Bangalore office?
```

## RAG Pipeline

The policy-question workflow follows these steps:

```text
PDF Documents
      │
      ▼
Text Extraction
      │
      ▼
Text Cleaning
      │
      ▼
Sentence-Aware Chunking
      │
      ▼
Sentence Transformer Embeddings
      │
      ▼
FAISS Vector Index
      │
      ▼
Semantic Similarity Search
      │
      ▼
Relevant Policy Context
      │
      ▼
Gemini API
      │
      ▼
Grounded Answer with Sources
```

## Data Privacy

This project is designed for internal office-assistant use.

- Employee information is read from local JSON files.
- Payroll information is read from local JSON files.
- Company policy documents are stored locally.
- Do not upload confidential company data to public repositories.
- Do not commit passwords, API keys, employee personal information, or other secrets.

## Future Improvements

- Add authentication and role-based access
- Add expense-management functionality
- Add conversation memory
- Add multilingual support
- Add document upload through the UI
- Add more company tools and integrations
- Improve intent classification accuracy
- Add automated testing
- Add deployment using Docker
- Add monitoring and logging

## Author

Developed as a team project for the TechNova Pvt. Ltd. Office Assistant.

## License

This project is intended for educational and internal use.
