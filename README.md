# CapeZone Assignment

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Docker installed on your machine.
- Docker Compose installed on your machine.

## Setup Instructions

Follow these steps to set up and run the project:

1. **Clone the repository**

   ```bash
   git clone https://github.com/nandan-jain/capezone-assignment.git
   cd capezone-assignment
   
2. **Create a .env file**

   ```bash
   cp .env.example .env
    ```
    Open the .env file and update the environment variables as needed.
    
3. **Build and run the project using Docker Compose**

    Use the following command to build and run the project:

   ```bash
   docker-compose up --build
    ```
    This will build the Docker images and start the containers.
    
4. **Access the application**

    Once the containers are up and running, you can access the application at:

   ```bash
   http://localhost:8000

    ```

5. **Run tests**

    To run the test cases for the project, use the following command:

   ```bash
    docker-compose exec web poetry run python manage.py test

    ```
