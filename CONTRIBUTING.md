# Contributing to Lagos State Property Portal

Thank you for your interest in contributing to the Lagos State Property Portal! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

We have adopted a Code of Conduct that we expect project participants to adhere to. Please read [the full text](CODE_OF_CONDUCT.md) so that you can understand what actions will and will not be tolerated.

## How to Contribute

### Reporting Bugs

If you find a bug in the application, please create an issue with the following information:

- A clear, descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment details (browser, operating system, etc.)

### Suggesting Features

We welcome feature suggestions! To suggest a new feature:

- Check if the feature has already been suggested or implemented
- Create an issue with a clear description of the feature
- Explain why this feature would be beneficial to the project
- Include any relevant mockups or examples

### Pull Requests

1. Fork the repository
2. Create a new branch from `main` with a descriptive name
   ```
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Write or update tests as needed
5. Ensure your code follows the project's coding standards
6. Commit your changes with clear, descriptive commit messages
7. Push your branch to your fork
8. Submit a pull request to the `main` branch

## Development Setup

1. Clone the repository
   ```
   git clone https://github.com/yourusername/LagosStatePropertyPortal.git
   cd LagosStatePropertyPortal
   ```

2. Create a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file using the `.env.example` as a template

5. Run migrations
   ```
   python manage.py migrate
   ```

6. Create a superuser
   ```
   python manage.py createsuperuser
   ```

7. Run the development server
   ```
   python manage.py runserver
   ```

## Coding Standards

### Python

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Write docstrings for all functions, classes, and modules
- Keep functions and methods focused on a single responsibility

### Django

- Follow Django's best practices
- Use Django's ORM instead of raw SQL when possible
- Write tests for new features and bug fixes
- Keep views lightweight and move business logic to models or services

### API

- Follow RESTful principles
- Document all API endpoints using docstrings compatible with DRF Spectacular
- Include appropriate validation for all input data
- Use appropriate status codes for responses

## Testing

- Write unit tests for models, serializers, and views
- Ensure all tests pass before submitting a pull request
- Run tests using:
  ```
  python manage.py test
  ```

## Documentation

- Update the README.md file with any necessary changes
- Document new features, API endpoints, or significant changes
- Keep code comments up-to-date

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

## Questions?

If you have any questions about contributing, please reach out to the project maintainers.

Thank you for contributing to the Lagos State Property Portal!