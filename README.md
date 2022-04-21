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
