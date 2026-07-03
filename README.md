# Little Lemon API

A robust, role-based backend REST API built using Python and Django REST Framework for a restaurant management ecosystem.

## Features
* **Authentication & Permissions:** Secure endpoint routing managed via Djoser/SimpleJWT.
* **Domain Seclusion:** Independent endpoints for Menu Management, Cart staging, and Order lifecycles.
* **Roles Matrix:** Enforces separate workflow privileges for Customers, Managers, and Delivery Crew.

## Technical Execution & CI/CD
* **Testing Engine:** 28 tests powered by `pytest` and `pytest-django` utilizing an isolated, modular `conftest.py` setup.
* **Automation:** An automated CI/CD pipeline built via **GitHub Actions** runs the 23-test validation suite on every single code push.

## Setup Instructions
1. Clone the repository.
2. Install dependencies: `pipenv install --dev`
3. Activate environment: `pipenv shell`
4. Run migrations: `python manage.py migrate`
5. Run tests locally: `pytest`