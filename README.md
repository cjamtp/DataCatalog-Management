# Data Catalog Management System

A comprehensive data catalog management system for managing business objects, data elements, domains, and business rules with similarity search capabilities using Neo4j and CrewAI.

## Features

- 🏢 **Business Object Management**: Track and manage business entities and their relationships
- 📊 **Data Element Management**: Document and organize data fields with technical metadata
- 🌐 **Domain Management**: Group related objects into business domains with hierarchical structures
- 📏 **Business Rule Management**: Define and enforce data rules across the organization
- 🔍 **Similarity Search**: Find similar entities using vector embeddings
- 🤖 **AI-Powered Analysis**: Get comprehensive insights using CrewAI agents

## Architecture

The system is built with a clean, modular architecture:

- **Models**: Domain entities representing the key concepts
- **Repositories**: Data access layer for Neo4j database operations
- **Services**: Business logic for operations like similarity search
- **API**: RESTful endpoints for all operations
- **CrewAI**: Intelligent agents for advanced analysis
- **Utilities**: Helper functions for logging and error handling

## Tech Stack

- **Python 3.10+**: Core programming language
- **Neo4j**: Graph database for storing catalog data
- **FastAPI**: API framework for REST endpoints
- **CrewAI**: Agent-based AI framework for similarity search
- **Sentence Transformers**: Model for text embedding generation
- **Pydantic**: Data validation and settings management
- **Loguru**: Advanced logging

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Neo4j 4.4 or higher
- OpenAI API key (for CrewAI)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/cjamtp/DataCatalog-Management.git
cd DataCatalog-Management
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -e .
```

4. Create a `.env` file with your configuration:

```bash
cp .env.example .env
# Edit .env with your Neo4j and OpenAI credentials
```

## Project Structure

```
data-catalog/
├── src/
│   ├── models/          # Domain models
│   ├── repositories/    # Data access layer
│   ├── services/        # Business logic
│   ├── api/             # API endpoints
│   ├── crews/           # CrewAI integration
│   ├── db/              # Database client
│   └── utils/           # Utilities
├── scripts/             # Administrative scripts
└── tests/               # Unit and integration tests
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
