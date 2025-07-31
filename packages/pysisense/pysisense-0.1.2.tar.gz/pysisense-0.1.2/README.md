# 📊 Sisense SDK (`pysisense`)

**pysisense** is a Python SDK designed for seamless and structured interaction with the **Sisense API**.  
It simplifies complex API operations and allows you to automate and manage **users**, **groups**, **dashboards**, **data models**, and more.

> ✅ Built for automation, debugging, and extensibility.

---

## 📦 Installation

You can install `pysisense` from [PyPI](https://pypi.org/project/pysisense/):

```bash
pip install pysisense
```

For local development, install in editable mode:

```bash
pip install -e .
```

---

## 🚀 Quick Start

### 1️⃣ Configure the YAML

Before running any scripts, update the required YAML files in the [`examples/`](https://github.com/hnegi01/pysisense/tree/main/examples) folder:

- `config.yaml` – for single-environment operations
- `source.yaml` and `target.yaml` – for migration scenarios

These contain fields like:

```yaml
domain: "your-domain.sisense.com"
is_ssl: true
token: "<your_api_token>"
```

⚠️ **Do not commit your tokens. The provided YAMLs contain placeholder structure only.**

### ⚠️ Important: Use a Dedicated Admin Token

Some methods in this SDK require full administrative privileges to interact with Sisense resources (such as ownership changes, user migrations, or folder/dashboard access).

To avoid permission-related issues or incomplete operations:

It is recommended to use a new dedicated Sisense admin user's token when authenticating via your `config.yaml`.

Using restricted or scoped users may result in failures or inconsistent behavior, especially for:

- Folder and dashboard ownership changes
- Granting permissions across environments
- System-wide migrations

---

### 2️⃣ Use Example Scripts

A complete set of usage examples is available under [`examples/`](https://github.com/hnegi01/pysisense/tree/main/examples). Each file demonstrates common operations and usage patterns:

- [`access_management_example.py`](https://github.com/hnegi01/pysisense/blob/main/examples/access_management_example.py)  
  Identity & Governance – Manage users, groups, folder access, and governance operations such as identifying unused assets.

- [`datamodel_example.py`](https://github.com/hnegi01/pysisense/blob/main/examples/datamodel_example.py)  
  Data Modeling – Work with datasets, tables, columns, and schema structures within Sisense data models.

- [`dashboard_example.py`](https://github.com/hnegi01/pysisense/blob/main/examples/dashboard_example.py)  
  Dashboard Lifecycle – Retrieve, update, reassign ownership, and manage shares of Sisense dashboards.

- [`migration_example.py`](https://github.com/hnegi01/pysisense/blob/main/examples/migration_example.py)  
  Environment Migration – Migrate users, dashboards, and data models across Sisense environments (e.g., from dev to prod).

These example files are **not meant to be executed end-to-end**, but rather serve as reference implementations to guide usage within your own environment or automation pipelines.

---

### 3️⃣ Logs

All logs are saved automatically to a local folder:

```
logs/pysisense.log
```

You don’t need to create this folder manually — it will be created at runtime in the **same directory where you run your scripts**.

---

## ✅ Features

- 👥 **User & Group Management** – Create, update, delete, and fetch users or groups
- 📊 **Dashboard Management** – Export, share, and migrate dashboards
- 📦 **Data Models** – Explore, describe, and update schemas and security
- 🔐 **Permissions** – Resolve and apply share rules (users & groups)
- 🔄 **Cross-Environment Migrations** – Move dashboards, models, and users
- 🧠 **Smart Logging & Data Helpers** – Auto log capture, CSV export, and DataFrame conversion
- ➕ **And many more** – Refer to the documentation for full details

---

## 🔧 Design Philosophy

- Pythonic SDK with class-based structure (`Dashboard`, `DataModel`, `AccessManagement`, `Migration`)
- Modular YAML-based authentication
- Built-in logging and exception handling
- Designed for end-to-end automation and real-world use

---

📚 Documentation

Comprehensive module-level documentation is available in the `docs/` folder:

-   [Index](https://github.com/hnegi01/pysisense/blob/main/docs/index.md) – Overview of the SDK structure and modules

-   [API Client](https://github.com/hnegi01/pysisense/blob/main/docs/api_client.md) – Base API wrapper for all HTTP operations  

-   [Access Management](https://github.com/hnegi01/pysisense/blob/main/docs/access_management.md) – Manage users, groups, roles, and permissions  

-   [Data Model](https://github.com/hnegi01/pysisense/blob/main/docs/datamodel.md) – Handle datasets, tables, schemas, security, and deployment  

-   [Dashboard](https://github.com/hnegi01/pysisense/blob/main/docs/dashboard.md) – Retrieve, modify, and share Sisense dashboards  

-   [Migration](https://github.com/hnegi01/pysisense/blob/main/docs/migration.md) – Migrate users, dashboards, and models between environments  

-   [Utils](https://github.com/hnegi01/pysisense/blob/main/docs/utils.md) – Helper functions for export, formatting, and data operations  

You can also explore:

-   Inline method docstrings using `help()` in Python or directly within your IDE.

---

## 🛠️ Contributing

We welcome your contributions!

1. Fork this repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes
4. Open a pull request for review

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 📧 Contact

Maintainer: **Himanshu Negi**  
📩 Email: `himanshu.negi.08@gmail.com`  
🔗 [GitHub Repository](https://github.com/hnegi01/pysisense)
