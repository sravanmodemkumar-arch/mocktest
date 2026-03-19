# mocktest

A real-time project repository.

## Getting Started

```bash
# Install dependencies
npm install

# Run in development
npm run dev

# Build for production
npm run build

# Run tests
npm test
```

## Project Structure

```
├── .github/
│   ├── workflows/       # CI/CD pipelines
│   ├── ISSUE_TEMPLATE/  # Issue templates
│   └── pull_request_template.md
├── src/                 # Source code
└── README.md
```

## CI/CD

- **CI Pipeline** — runs on every push and PR (lint, test, build)
- **Deploy** — auto-deploys to production on merge to `main`
- **Security Scan** — weekly dependency audit

## Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Open a Pull Request using the PR template
4. Get review approval before merging

## License

MIT
