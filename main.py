from app import app
from database import init_db

# Initialize database when module is imported
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
