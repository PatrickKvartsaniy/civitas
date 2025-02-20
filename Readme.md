# Civitas

## Overview
Civitas is a geospatial data-driven application that leverages **Domain-Driven Design (DDD)** and **Hexagonal Architecture** to provide insights and analytics for urban environments through an interactive 2D and 3D map viewer and a comprehensive dashboard. It also enables user participation by allowing them to report the maintenance status of buildings, indicating whether repairs are needed. It integrates various geospatial services, routing functionalities, and data processing techniques to deliver valuable insights for city planning, logistics, and more.

## Preview
(It takes some time to load the map first time, but after that it will be momentary since both server side and client side cache are implemented)
https://civitas-471b.onrender.com/web/map/amenities


## Technology Stack

- **Programming Language:** Python 3.9
- **Framework:** FastAPI
- **Database:** PostgreSQL with PostGIS
- **Geospatial Tools:** Overpass API, Terra
- **Frontend:** Mapbox GL JS, HTML, CSS, JS, flask, jinja
- **Infrastructure:** Docker, Terraform
- **Linting:** Black

## Architecture

### Two Application Modes
Civitas can run in two different modes using a **single entry point** (`main.py`) with **command-line arguments**:

1. **Web App (`web`)**: Runs the interactive web application.
2. **ETL Process (`etl`)**: Executes the data extraction, transformation, and loading (ETL) pipeline.

![img.png](docs/img/img_1.png)

This approach allows for **code reuse** across both modes, including shared logic, models, and configurations.


### Domain-Driven Design (DDD)
Civitas follows the **Domain-Driven Design** approach, structuring the codebase into meaningful business domains. The core logic is encapsulated in domain entities, keeping the system modular and scalable.

### Hexagonal Architecture
The project implements **Hexagonal Architecture**, also known as the **Ports and Adapters Pattern**, to keep business logic independent from external dependencies such as databases or APIs. This approach allows easier testing and better maintainability.
![img.png](docs/img/img.png)
- **Adapters**: Interfaces for interacting with external services (e.g., Overpass, Terra)
- **Application Layer**: Handles use cases and business logic
- **Infrastructure Layer**: Database and external service implementations
- **Domain Layer**: Core business rules and models

## Installation

### Prerequisites
- Python 3.9+
- PostgreSQL with PostGIS
- Docker (optional, for containerized deployment)

### Setup
```sh
# Clone the repository
git clone https://github.com/PatrickKvartsaniy/civitas.git
cd civitas

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

### Local Development (Web Server)
```sh
make run_web
```

### Local Development (ETL)
```sh
make run_etl
```

### Deploy to AWS
```sh
make deploy
```

### Destroy
```sh
make destroy
```

## API Documentation
Civitas provides an interactive API documentation using **Swagger**. Once the server is running, visit:

- Swagger UI: `https://civitas-471b.onrender.com/docs`

## Configuration & Environment Variables
Civitas uses a `env` for configuration. The following environment variables are required:

```
DATABASE_URL=postgresql://user:password@localhost:5432/civitas
MAPBOX_API_KEY=your_mapbox_api_key
OVERPASS_API_URL=https://overpass-api.de/api/interpreter
```

### Running Migrations
```sh
alembic upgrade head
```

### Run static analysis and linting:
```
Happens automaticly when commit
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Commit changes (`git commit -m "Added new feature"`)
4. Push to the branch (`git push origin feature-name`)
5. Open a pull request
