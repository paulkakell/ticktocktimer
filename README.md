# UNDER CONSTRUCTION...  NOT WORKING



# TickTock Timer Application

The **TickTock Timer Application** is a Dockerized application that allows users to manage multiple configurable countdown timers. The application features an administrative web interface, API endpoints, and multi-user support with API keys. It also supports webhook notifications when timers expire.

## Features

- **Countdown Timers**: 
  - Timer that counts down to a specific date/time.
  - Timer that elapses a specific duration (in years, months, days, hours, minutes, and seconds).

- **API Endpoints**:
  - Query the time left for individual timers.
  - Reset timers via API.
  - Webhook functionality to notify when a timer expires.

- **Multi-User Configuration**:
  - Users can have unique API keys to interact with timers.
  - Admin users can manage timers for all users.
  
- **Administrator Account**:
  - The default administrator account allows full access to manage and configure all timers.
  - Admin can only manage users and view timers; they cannot create new timers via the API.

- **Backend Database**:
  - Supports both internal and external PostgreSQL databases.
  - Admins can configure the external database, which shuts down the internal database to reduce footprint.

- **Security**:
  - Follows industry best practices for API key management, authentication, and data security.
  - Comprehensive logging of all actions and errors.

- **Logging**:
  - Verbose logging of all actions, errors, messages, and successes in `logs/ticktock.log`.

## Requirements

- **Docker**: To build and run the container.
- **Docker Compose**: For managing multi-container applications.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ticktock-timer.git
cd ticktock-timer
