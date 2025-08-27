# Overview

This is a complete inventory management system built with Flask for managing product stock, sales, and generating reports. The system provides a web-based interface for tracking product entries, exits, and financial analytics with user authentication and comprehensive reporting capabilities.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLite with raw SQL queries using sqlite3 module
- **Session Management**: Flask-Session with filesystem storage
- **Authentication**: Password hashing using Werkzeug security utilities
- **Data Models**: Dataclass-based models (User, Product, Sale) for type safety

## Frontend Architecture
- **Template Engine**: Jinja2 templates with template inheritance
- **CSS Framework**: Bootstrap 5.3.0 for responsive design
- **JavaScript**: Vanilla JavaScript for client-side functionality
- **Icons**: Font Awesome 6.0.0 for UI icons
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

## Data Storage Design
- **Database Schema**: Three main tables (usuarios, produtos, vendas)
- **Product Management**: Tracks inventory levels, purchase/sale prices, and categories
- **Sales Tracking**: Automatic stock reduction on sales with validation
- **User Management**: Simple user authentication with hashed passwords

## Authentication System
- **Session-based Authentication**: Server-side session storage
- **Password Security**: Werkzeug password hashing (likely PBKDF2)
- **Route Protection**: Decorator-based login requirements
- **Default Credentials**: Admin user (admin@admin.com / admin123) for initial access

## Application Structure
- **MVC Pattern**: Clear separation between routes (controllers), models, and templates (views)
- **Modular Design**: Separate files for database operations, models, routes, and app configuration
- **Error Handling**: Flask flash messaging for user feedback
- **Form Validation**: Both client-side (Bootstrap) and server-side validation

# External Dependencies

## Frontend Libraries
- **Bootstrap 5.3.0**: CSS framework for responsive UI components
- **Font Awesome 6.0.0**: Icon library for UI elements
- **CDN Delivery**: External hosting for frontend libraries

## Python Dependencies
- **Flask**: Core web framework
- **Flask-Session**: Session management extension
- **Werkzeug**: WSGI utilities and security functions (password hashing)
- **SQLite3**: Database engine (built into Python)

## Development Tools
- **ProxyFix**: Werkzeug middleware for production deployment
- **Logging**: Python's built-in logging for debugging
- **Debug Mode**: Flask development server with hot reloading

## File Storage
- **Session Storage**: Filesystem-based session persistence
- **Database File**: Local SQLite file (inventory.db)
- **Static Assets**: Local CSS and JavaScript files