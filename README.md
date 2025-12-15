# Python Unreal Game Sync Metadata Server

- Can be deployed on a cheap Linux server.
- Backward & forward compatible with Epic's UGS Metadata server.
- All UGS Metadata server features implemented (as of December 2025).

## Requirements

- Python 3.9+
- MySQL 8.0+

## Installation

### 1. Install Python Dependencies

```bash
pip install fastapi aiomysql uvicorn
```

### 2. Database Setup

Create the required database and tables by running the setup script:

```bash
mysql -u root -p < install/setup.sql
```

### 3. Configuration

Configure the database connection using environment variables:

```bash
export UGS_DB_HOST=127.0.0.1
export UGS_DB_PORT=3306
export UGS_DB_USER=ugs_user
export UGS_DB_PASSWORD=your_password
export UGS_DB_CHARSET=utf8
```

## Running the Server

From the `api` directory:

```bash
cd api
uvicorn main:app --host 0.0.0.0 --port 5001 --workers 4
```

### Verify Installation

Once the server is running, you can verify it's working by accessing the interactive API documentation:

```
http://127.0.0.1:5001/docs
```
