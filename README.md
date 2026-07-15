# BrewCafe – High-Concurrency RESTful Ordering & Payment Engine

BrewCafe is a production-ready backend REST API built with Python and Django REST Framework (DRF), designed to process high-throughput digital ordering and transactional payments.

## 🚀 Key Features
* **Domain Seclusion:** Decoupled, role-based endpoints managing Menu, Cart, Orders, and Payments lifecycles via Djoser/Token authentication.
* **Relational Integrity:** Database-level `unique_together` constraints to eliminate concurrency-driven cart duplication.
* **Transactional Payments:** Built-in mock payment processing gateway handling multi-stage customer checkout workflows.

## 🧪 Testing Suite & Architectural Mocking
* **Pytest Ecosystem:** 34 unit and integration tests driven by `pytest` and `pytest-django` via a modular `conftest.py` setup.
* **Advanced Test Design:** Parameterized testing arrays evaluating payment edge cases alongside `unittest.mock` configurations and Test Spies to audit payment interface invocations.
* **Automated CI/CD:** GitHub Actions workflow executing the validation suite automatically on every single code push.

## 📊 Performance Engineering (Locust)
* **Stress Profiling:** Simulated asymmetric, weighted user traffic patterns to pressure-test write operations.
* **Telemetry Calibration:** Utilized Locust `catch_response` context managers to isolate physical database-contention locks (SQLite 500 errors) from core application defects.
* **Result:** Achieved a clean 0% logical application failure rate while successfully scaling past 2,600+ parallel transaction flows.

## 🛠️ Quick Start
1. Clone the repository.
2. Install dependencies: `pipenv install --dev`
3. Activate environment: `pipenv shell`
4. Run migrations: `python manage.py migrate`
5. Run tests locally: `pytest`
6. Generate load testing tokens: `python manage.py generate_tokens`
7. Stress Test: `locust -f locustfile.py`