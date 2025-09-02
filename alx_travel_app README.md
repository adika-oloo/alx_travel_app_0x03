
# ALX Travel App 0x03 - Background Task Management

A Django-based travel application with Celery background task management, RabbitMQ message broker, and email notification system for booking confirmations.

## 🚀 Features

- **Property Listings Management**: Create and manage travel property listings
- **Booking System**: Complete booking functionality with date management
- **Background Tasks**: Asynchronous task processing with Celery
- **Email Notifications**: Automated booking confirmation emails
- **Message Broker**: RabbitMQ for reliable task queuing
- **Real-time Monitoring**: Flower for Celery task monitoring
- **Dockerized Services**: RabbitMQ and Redis in Docker containers

## 🛠️ Tech Stack

- **Backend**: Django 4.x
- **Task Queue**: Celery
- **Message Broker**: RabbitMQ
- **Result Backend**: Redis
- **Database**: PostgreSQL (configured separately)
- **Email**: SMTP (Gmail/other providers)
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Git
- SMTP email account (Gmail recommended for testing)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the project (if not already done)
git clone <your-repository-url>
cd alx_travel_app_0x03

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
