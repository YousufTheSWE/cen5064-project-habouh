# Creational Design Pattern Map

## 1. Pattern Mapping

- **Factory Method**: Genuine home — `create_app()` in `main.py` owns the backend wiring flow, where a `create_account_repository()` method allows substituting `SqliteAccountRepository` with an in-memory repository for `tests/test_app.py`.
- **Abstract Factory**: No genuine fit, because our system only uses a single persistence tier (`SqliteAccountRepository` and `Database`) and a single React frontend, with no families of related products to instantiate.
- **Builder**: No genuine fit, because our domain entities and DTOs (`Account`, `CreateAccountBody`, `LoginBody`) contain only two fields (`username`, `password`) and are constructed in a single step without multi-part assembly.
- **Prototype**: No genuine fit, because `Account` instances in `domain/account.py` are created directly from user credentials rather than cloned from existing prototypical objects.
- **Singleton**: No genuine fit, because `Database` in `data/database.py` is instantiated once in `create_app()` and passed into `SqliteAccountRepository` via dependency injection, avoiding global state.

## 2. Single Best Fit: Factory Method

**Why it is the best fit:**
The **Factory Method** pattern is the single best fit because it directly targets the primary point of variation in our backend: how `SqliteAccountRepository` is supplied to `AccountService`.

In `main.py`, `create_app()` owns a shared assembly workflow: it loads configuration, initializes `Database`, wires `AccountService`, registers middleware, configures `register_error_handlers`, and mounts `account_routes`. Currently, line 16 hardcodes `SqliteAccountRepository(database)`.

Applying the Factory Method pattern here:
- **The tell**: An abstract `create_account_repository()` method sits inside the application setup that otherwise owns the entire flow.
- **Subclasses decide**: A concrete production setup returns `SqliteAccountRepository` backed by `database.db`, while a test runner for `tests/test_app.py` can return an in-memory repository to test `AccountService` in isolation without disk I/O.
