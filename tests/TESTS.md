🧪 Running Tests

This project uses pytest with pytest-django and Playwright for end-to-end (E2E) and integration testing.

1. Environment Setup

Before running tests, make sure you are inside the virtual environment:

**source venv/bin/activate**


Using the Test Runner Script (Recommended)

I have provide a helper script **runtests.sh** to handle environment variables automatically.

Make it executable (first time only):
**chmod +x runtests.sh**

RUN ALL TESTS

### ./runtests.sh tests/ -v

./runtests.sh tests/e2e -v                  # Run all E2E tests
./runtests.sh tests/integration -v          # Run integration tests
./runtests.sh tests/unit -v                 # Run unit tests
./runtests.sh tests/e2e/tests/orders/test_orders_business.py::test_orders_sorted_by_created_date -v



3. Running Tests Manually (Without Script)

If you don’t want to use runtests.sh, you must export the variables yourself:

export PYTHONPATH=$PYTHONPATH:$(pwd)
export DJANGO_SETTINGS_MODULE=savannah_assess.settings
pytest tests/ -v


4. Coverage Reports

To run tests with coverage:

### ./runtests.sh --cov=api tests/ -v

✅ With this setup, you can easily run unit tests, integration tests, and end-to-end tests without worrying about environment setup.


