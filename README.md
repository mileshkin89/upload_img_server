# 📷 Upload Image Server

A comprehensive containerized service for uploading, viewing, and managing images.  
It features a drag-and-drop uploader, image gallery with pagination, automatic URL generation, and persistent logging — all powered by a clean backend + frontend separation with database support and managed with Docker Compose.

---

## 📌 Overview

This project is a complete image hosting platform designed for uploading, organizing, and sharing pictures via a modern user interface.
It features:

- A **backend server** built entirely with Python using the standard http.server module and custom routing logic
- A sleek, interactive **frontend UI** with support for drag-and-drop uploads and an image gallery
- A **PostgreSQL database** used to store image metadata
- **PgBouncer** for efficient database connection pooling
- An **Nginx** reverse proxy configured with load balancing across backend instances
- Detailed **logging** for both backend operations and access requests
- A **RESTful API** offering endpoints for uploading, retrieving, previewing, and deleting images
- All services run in isolated containers and are managed via **docker-compose**.

---

## 🚀 Features

- **📁 Easy Image Upload**  
  Users can drag & drop `.jpg`, `.png`, or `.gif` files or use a button to upload them through the interface.

- **🖼️ Gallery View with Paging**  
  Uploaded images are shown as stylish cards with pagination and sorting features for smooth browsing.

- **⚡ Instant Refresh**  
  The gallery updates automatically after each upload or delete — no need to reload the page.

- **🧭 Seamless Navigation**  
  Instantly switch between "Upload" and "Images" tabs, with state saved via URL parameters and localStorage.

- **📱 Mobile-Ready Layout**  
  Fully adaptive layout optimized for desktops, tablets, and smartphones.

- **🗑️ Image Deletion**  
  Each image includes a delete option with confirmation to prevent accidental removal.

- **❗ Clear Error Messages**  
  Users get immediate feedback for upload errors such as wrong file types, oversized images, or network failures.

- **🐳 One-Click Docker Setup**  
  All components run in containers and can be launched with a single `docker-compose up` command.

---

## ⚙️ Installation

Clone the repository and start the containers:

    git clone https://github.com/mileshkin89/upload_img_server.git
    cd upload_img_server
    docker-compose up --build

Before running the server, configure the environment variables:

**1. Backend Configuration:**

    cd services/backend
    cp .env.sample .env

Edit the `.env` file with your configuration. Sample variables:

    # Directory where uploaded images will be stored
    IMAGES_DIR=/usr/src/img_storage
    # Directory where log files will be written  
    LOG_DIR=/usr/src/logs
    
    # Number of worker processes to spawn for HTTP server
    WEB_SERVER_WORKERS=5
    # Starting port number for worker processes
    WEB_SERVER_START_PORT=8000
    
    # PostgreSQL Database Configuration
    POSTGRES_DB=upload_images_db
    POSTGRES_DB_PORT=5432
    POSTGRES_USER=admin
    POSTGRES_PASSWORD=some_password
    POSTGRES_HOST=postgres-upload-server

**2. PgBouncer Configuration:**

    cd services/pgbouncer
    cp .env.sample .env

Edit the `.env` file with your PgBouncer settings:

    # PgBouncer Configuration
    PGBOUNCER_USER=bouncer_user
    PGBOUNCER_PASSWORD=change_this_password_in_prod
    PGBOUNCER_HOST=pgbouncer-upload-server
    PGBOUNCER_PORT=6432
    USE_PGBOUNCER=true
    MAX_CLIENT_CONN=200
    DEFAULT_POOL_SIZE=20

Then visit: **http://localhost**

---

## 📂 Usage

### Web UI

1. **Welcome Page:**
   - Open browser and go to `http://localhost/`
   - You will be met by one of five unique heroes
   - Click on the "Go to upload" button

2. **Upload Images:**
   - Drag and drop or select files to upload
   - Copy the generated image URLs

3. **Browse Gallery:**
   - Switch to "Images" tab to see all uploaded files
   - Use pagination controls to navigate through images
   - Sort by uploaded time, file size or file name
   - Adjust items per page (4, 8, or 12)

4. **Manage Images:**
   - Use fullscreen mode for better viewing
   - Copy direct URLs or download images
   - Delete images with confirmation prompts
   - All changes reflected immediately in gallery

---

## 🧩 Project Structure

    .
    ├── README.md
    ├── docker-compose.yml
    ├── .dockerignore
    ├── .gitignore
    ├── img_storage/                            # Uploaded files stored here
    ├── logs/                                   # Backend logs
    │   ├── app.log 
    │   ├── pgbouncer/
    │   │   └── pgbouncer.log    
    │   └── nginx/
    │       ├── access.log
    │       └── error.log
    ├── init-sql/                               # Database initialization scripts
    │   ├── 1-init.sql
    │   ├── 2-create-tables.sql
    │   └── 3-create-indexes.sql
    └── services/
        ├── backend/
        │   ├── Dockerfile
        │   ├── .env.sample
        │   ├── poetry.lock
        │   ├── pyproject.toml
        │   └── src/
        │       ├── run.py                      # Restarting the server
        │       ├── server.py                   # Starting the server
        │       ├── db/
        │       │   ├── __init__.py
        │       │   ├── dependencies.py         # Create singleton instance of repository
        │       │   ├── dto.py                  # Data Transfer Object for image metadata
        │       │   ├── repositories.py         # Image repository for DB
        │       │   └── session.py              # Create a connection pool for DB
        │       ├── exceptions/                 # Custom exceptions
        │       │   ├── __init__.py
        │       │   ├── api_errors.py
        │       │   ├── pagination_errors.py
        │       │   └── repository_errors.py
        │       ├── handlers/
        │       │   ├── __init__.py
        │       │   ├── file_handler.py         # Class for handle operations with files
        │       │   └── http_handler.py         # Class for processing HTTP request
        │       ├── mixins/                     # Mixins for HTTPHandler
        │       │   ├── __init__.py
        │       │   ├── json_sender.py
        │       │   ├── pagination.py
        │       │   ├── route_parser.py
        │       │   └── sorter.pye
        │       └── settings/                   # Application settings
        │           ├── __init__.py
        │           ├── config.py
        │           └── logging_config.py
        ├── frontend/
        │   ├── index.html
        │   ├── upload.html
        │   ├── images.html
        │   └── static/
        │       ├── css/
        │       │   ├── styles.css
        │       │   ├── upload.css
        │       │   └── images.css
        │       ├── js/
        │       │   ├── upload.js
        │       │   ├── images.js
        │       │   └── random-hero.js
        │       └── random_images/              # Images for the welcome page
        │           └── *.png
        ├── nginx/
        │   └── nginx.conf
        └── pgbouncer/
            ├── Dockerfile
            ├── .env.sample
            └── setup_pgbouncer_auth.sh

---

## 🛠️ Tech Stack

| Layer       | Technology                           |
|-------------|--------------------------------------|
| Backend     | Pure Python (http.server, multiprocessing)|
| Database    | PostgreSQL, PgBouncer               |
| Frontend    | HTML5, CSS3, Vanilla JavaScript     |
| Web Server  | Nginx (reverse proxy)               |
| Logging     | Python Logging + Nginx logs         |
| Packaging   | Docker, Docker Compose              |
| Styling     | Custom CSS with responsive design    |
| API         | RESTful with JSON responses          |

---

## 🔧 API Endpoints

| Method | Endpoint                    | Description                    |
|--------|-----------------------------|--------------------------------|
| POST   | `/api/upload/`             | Upload new image               |
| GET    | `/api/images/`             | List all images with pagination|
| DELETE | `/api/images/{filename}`   | Delete specific image          |
| GET    | `/images/{filename}`       | Serve image file               |

---

## 🚨 Important Notes

- Change default passwords in production environment
- `IMAGES_DIR` and `LOG_DIR` should match volume mounts in docker-compose.yml
- Database credentials must be consistent across all services
- PgBouncer acts as connection pooler between application and PostgreSQL

---

## 🙏 Acknowledgments

Icons and images provided by free open-source tools.

---

## 📋 License

MIT License. Use freely, fork, or extend.
