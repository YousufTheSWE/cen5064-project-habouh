# PostClient

<!-- CI badge: after Session 4, replace ORG/REPO and the workflow filename, then uncomment:
![CI](https://github.com/ORG/REPO/actions/workflows/ci.yml/badge.svg)
-->

**Student:** Yousuf Habouh · **Course:** CEN 5064 Software Design, Fall 2026 · **Partner:** [@ghechavarria]

## Project (approval paragraph — write this by Sun Aug 30)

The system will implement a chatting application, which will be called PostClient. I'll make this project by implementing a backend that allows for account creation and community creation, and a frontend that showcases posts on the involved communities for a user. I am making this because one of the main reasons users use the internet is to communicate with each other, and this will offer one more avenue of communication.

Business Rules:
- A user can be the owner of 10 communities at most.
- A user can subscribe to 200 communities at most (subscription is an option that enables notifications on new posts)
- A community needs exactly 1 owner at all time.
- A user can either upvote once, downvote once, or not vote for any single post/comment.
- A user can only be signed in on 3 devices at once.

Core Features:
- A person can make an account.
- An account can make a community which they would own by default.
- Accounts can create Posts under a community.
- Accounts can post comments under a post or other comments.

## How to run

```
[Exact commands to build and run your system from a clean clone.
Update this every time the steps change — your partner and your
instructor will follow it literally on conference days.]
```

## Architecture

### Tier breakdown (Session 2 studio)

| Tier | Responsibilities in THIS system |
|------|--------------------------------|
| Presentation | [what your UI layer does] |
| Service | [what your use-case/orchestration layer does] |
| Domain | [your entities and business rules] |
| Data | [how and where data is stored] |

### C4 — Context & Container (Session 3 studio)

```mermaid
%% Replace this placeholder with YOUR system's context diagram.
flowchart TB
    user([User]) -->|uses| system[Your System]
    system -->|stores data in| db[(Database)]
```

```mermaid
%% Container view: your containers should match the tier table above.
flowchart TB
    subgraph YourSystem [Your System]
        ui[Web UI / CLI<br/>Presentation] --> api[Application / Service]
        api --> domain[Domain Model]
        domain --> db[(Database<br/>Data tier)]
    end
```

### UML — Class & Sequence (Session 3 studio)

```mermaid
%% Class diagram: your 3–4 core domain classes.
classDiagram
    class ExampleEntity {
        -id: Long
        -name: String
        +doSomething()
    }
```

```mermaid
%% Sequence diagram: ONE core use case, end to end.
sequenceDiagram
    actor U as User
    participant UI
    participant S as Service
    participant D as Data
    U->>UI: action
    UI->>S: request
    S->>D: save/load
    D-->>S: result
    S-->>UI: response
    UI-->>U: confirmation
```

## Architecture Decision Records

Decisions live in [`docs/adr/`](docs/adr/). Start with ADR-001 in Session 4.

| # | Decision | Status |
|---|----------|--------|
| [001](docs/adr/adr-001.md) | [What I am building and why] | [proposed] |

## Weekly log (optional but recommended)

A one-line note per week keeps your commit story readable:

- Week 1 (Aug 24): repo created, three ideas drafted
- Week 2 (Aug 31): ...
