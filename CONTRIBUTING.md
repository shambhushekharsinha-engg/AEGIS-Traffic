# Contributing to AEGIS-Traffic

Thank you for your interest in contributing to **AEGIS-Traffic**! We welcome contributions to help make smart city traffic management safer, smarter, and more efficient.

---

## 🛠️ Getting Started

1. **Fork the Repository**: Create a fork of the repo on GitHub.
2. **Clone Locally**:
   ```bash
   git clone https://github.com/your-username/AEGIS-Traffic.git
   cd AEGIS-Traffic
   ```
3. **Set Up Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

---

## 🧪 Running Tests & Validation

Before submitting a pull request, ensure all unit tests and deployment validations pass:

```bash
# Run pytest test suite
pytest

# Run deployment validation
python docs/validate_deployment.py
```

---

## 📝 Code Style & Guidelines

- Follow **PEP 8** guidelines for Python code.
- Ensure all new REST API endpoints include Pydantic type annotations and docstrings.
- Keep components modular and isolated.

---

## 📬 Submitting Pull Requests

1. Create a descriptive branch name (`git checkout -b feature/awesome-feature`).
2. Commit your changes with clear commit messages (`git commit -m "feat: add real-time acoustic anomaly filter"`).
3. Push to your branch (`git push origin feature/awesome-feature`).
4. Open a Pull Request on GitHub with a summary of changes and test results.
