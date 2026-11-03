# Contributing

Thanks for your interest in contributing.

## Development workflow

1. Fork the repository and create a feature branch.
2. Keep changes scoped to one service or feature where possible.
3. Install dependencies for the service you change.
4. Run the relevant tests and lint/build checks.
5. Update documentation when API routes, environment variables, or setup steps change.
6. Open a pull request with a clear summary, test evidence, and screenshots for UI changes.

## Code and security guidelines

- Never commit `.env` files, API keys, passwords, database URLs, JWT secrets, or personal data.
- Add new configuration keys to `.env.example` with blank or safe placeholder values.
- Avoid logging credentials or sensitive user content.
- Keep service-to-service URLs configurable through environment variables.
- Include tests for bug fixes and new behavior.

## Reporting issues

Include the affected service, steps to reproduce, expected behavior, actual behavior, relevant sanitized logs, and environment details. Remove secrets and personal information before sharing logs.
