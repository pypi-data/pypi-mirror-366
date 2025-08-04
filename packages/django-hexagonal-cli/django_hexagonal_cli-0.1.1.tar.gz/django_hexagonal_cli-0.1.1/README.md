
# Django Hexagonal Architecture

A command-line tool to generate Django projects and apps following the hexagonal (ports and adapters) architecture.

---

## What is this?
`django-hexagonal-cli` is a CLI utility that helps you quickly scaffold Django projects and apps with a clean hexagonal structure, ready for scalable, maintainable, and testable development.

## Installation

```bash
pip install django-hexagonal-cli
```

This will provide the `django-admin-hex` command.

## Usage

- **Create a new project:**
  ```bash
  django-admin-hex startproject <project_name> [<first_app_name>]
  ```
  This generates a Django project with the recommended hexagonal structure. Optionally, you can create the first app at the same time.

- **Create a new app in an existing project:**
  ```bash
  cd <project_name>
  django-admin-hex startapp <app_name>
  ```
  This creates a new app inside the `apps/` folder, following the hexagonal pattern.

## Project Structure Example
```
project_root/
├── apps/
│   └── <app_name>/
│       ├── application/
│       ├── domain/
│       ├── infrastructure/
│       └── interfaces/
├── config/
├── manage.py
├── pyproject.toml
└── README.md
```

## Why Hexagonal Architecture?
- Promotes separation of concerns
- Makes testing and maintenance easier
- Adapts easily to new frameworks or external services

## Example

This repository includes a working example of a Django project with hexagonal architecture in the `example/` folder. You can explore it to see a real API implementation using this structure.

## Resources
- [Official Django documentation](https://docs.djangoproject.com/en/5.2/)
- [Hexagonal architecture (Alistair Cockburn)](https://alistair.cockburn.us/hexagonal-architecture/)
