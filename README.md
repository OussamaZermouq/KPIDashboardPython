# Backend API for File Upload and Data Processing

## Description

This is the backend API built with FastAPI. It is designed to accept Excel files, process the data, and return the processed results in a structured format. The API supports file upload and allows the user to select a specific sheet for processing.

### API Endpoints:
- **POST /upload**: Uploads an Excel file and processes the data.
  - **Parameters**:
    - `file`: The Excel file to upload.
    - `sheet_name`: The name of the sheet to process (default: "Hourly Ville").
  - **Response**: Returns the processed data from the selected sheet.

## Installation

1. Clone the repository:

2. Navigate to the project folder:
    ```bash
    cd yourrepository
    ```

3. Set up a virtual environment:
    ```bash
    python -m venv venv
    ```

4. Activate the virtual environment:
    - On Windows:
      ```bash
      .\venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      source venv/bin/activate
      ```

5. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the API

1. Start the API server:
    ```bash
    uvicorn main:app --reload
    ```

2. Visit `http://127.0.0.1:8000/docs` to test the API via Swagger UI.

## Frontend Integration

- The frontend should send a `POST` request to the `/upload` endpoint with the file and optional `sheet_name` parameter.
