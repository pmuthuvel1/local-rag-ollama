# Contributing to Loomin-Docs

## Development Setup

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker (optional, for isolated environment)
- Git

### Initial Setup

```bash
# Clone repository
git clone <repo-url>
cd loomin-docs

# Setup frontend
cd frontend
npm install
npm run dev

# Setup backend (in new terminal)
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints
- Format with `black`
- Lint with `pylint` or `flake8`

```bash
pip install black pylint
black app/
pylint app/
```

### TypeScript (Frontend)
- Use strict mode
- Write meaningful component names
- Use hooks for state management

```bash
npm run lint
```

## Commit Guidelines

Format: `<type>: <subject>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Build/dependency updates

Example:
```
feat: add summarization endpoint
fix: prevent PII in LLM context
docs: update API reference
```

## Pull Request Process

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and commit
3. Push to branch: `git push origin feature/my-feature`
4. Create Pull Request with description
5. Wait for code review and CI checks

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Integration Tests
```bash
python scripts/verify-rag-faithfulness.py
```

## Adding New Features

### New Backend Endpoint

1. Create router file in `app/api/`
2. Add route and handler
3. Update `app/main.py` to include router
4. Add request/response schemas in `app/models/schemas.py`
5. Add tests in `backend/tests/`

Example:
```python
# app/api/new_feature.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/endpoint")
async def my_endpoint():
    return {"message": "Hello"}
```

### New Frontend Component

1. Create component file in `src/components/`
2. Export from component
3. Import and use in pages

```typescript
// src/components/MyComponent.tsx
import React from 'react'

export const MyComponent: React.FC = () => {
  return <div>Component</div>
}

// Usage in App.tsx
import { MyComponent } from '@/components/MyComponent'
```

### Adding RAG Features

1. Update `rag_service.py` with new methods
2. Create API endpoint in `app/api/rag.py`
3. Integrate into AI responses

## Performance Optimization

### Backend
- Profile with `cProfile` or `py-spy`
- Cache embeddings with Redis
- Use batch processing for chunks

### Frontend
- Use React DevTools Profiler
- Minimize bundle with webpack
- Lazy load components

## Security Considerations

- Always sanitize user input
- Validate all API parameters
- Use parameterized SQL queries (via SQLAlchemy ORM)
- Don't expose sensitive errors to clients
- Implement rate limiting for production
- Use HTTPS in production

## Documentation

- Update README for new features
- Add docstrings to functions
- Document API changes in API.md
- Update architecture diagrams if needed

## Releasing

1. Update version in `package.json` and `__init__.py`
2. Update CHANGELOG.md
3. Create git tag: `git tag v0.2.0`
4. Push tag: `git push origin v0.2.0`
5. Create GitHub Release

## Common Issues

### ModuleNotFoundError
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

### npm ERR!
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

### Docker build fails
- Ensure Dockerfile is in correct location
- Check for sensitive files in `.dockerignore`

## Getting Help

- Check existing issues on GitHub
- Review documentation in `/docs`
- Ask in project discussions

---

Happy coding! 🎉
