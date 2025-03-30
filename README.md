# AutoQuery: LLM-Powered Database Analysis

## Overview
AutoQuery is a Streamlit-based application that connects to SQL or MongoDB databases and allows users to query and analyze data using a Large Language Model (LLM). It supports:
- SQL databases (SQLite)
- MongoDB databases

The application provides schema exploration, data sampling, and natural language query capabilities.

## Features
- **SQL Database Support**: Explore table names, schemas, and query data using natural language.
- **MongoDB Support**: Explore collections, view sample documents, and query data using natural language.


## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
Create a `.env` file in the root directory and add your API key for the LLM:

```
GROQ_API_KEY=your_groq_api_key_here
```

Make sure to keep this file secure and do not share it publicly.

## Usage
Run the application:
```bash
streamlit run app.py
```

## File Structure
- `main.py`: Main entry point for the application.
- `db_utils.py`: Contains database-related utility functions.
- `requirements.txt`: List of dependencies for the application.

## Requirements
See `requirements.txt` for the list of dependencies.
