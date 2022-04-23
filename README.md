# rejsekort-python
Python Scrapper that returns Rejsekort Restful API

### Running the application
#### Pre-requisistes
- Make
- Python

#### Locally
1.  Using Make
    ```bash
    make run
    ```

2.  Using Docker
    - Build
      ```bash
      docker build -t rejsekort .
      ```

    - Run the container
      ```bash
      docker run --rm -p 3000:3000 flask
      ```

This will start a server which can be accessed on http://localhost:3000

#### Server
Set environment variable for production:
`ENV=production` or something other than `development`

## Usage
Once the server is up and running, requests can be made to these available endpoints.

#### Health Check
1. Request:
  `http://localhost:3000`

2. Response:
    ```
    {
      "status": "Healthy"
    }
    ```

#### Login
Username and Password can be generated from rejsekort self-service portal.
1. Post Request to: 
    `http://localhost:3000/login`

2. Request Body as raw JSON.
    ```
    {
      "username": "<USERNAME>",
      "password": "<PASSWORD>"
    }
    ```
