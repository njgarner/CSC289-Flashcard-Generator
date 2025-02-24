# Flashcard Generator User Guide

## Scope & Overview

The following guide will provide instructions for using our software/system, describe how users work, and describe the tasks they perform. It will also document every menu, function, and procedure in our application. This will include any precautions necessary to circumvent errors and malfunctions.

---

> ## **``Table of Contents``**

> ### <br>*Introduction*: <small>Explain the product, functionalities, and organization of sections</small>
> ### <br>*Process*: <small>Define the process for using the product</small>
> ### <br>*Diagram*: <small>Visual aid on user interaction</small>


> ### <br>*Workflow*: <small>Describe the tasks for achieving specific goals</small>
> ### <br>*Instructions*: <small>Step-by-step on user interactions</small>
> ### <br>*Conventions*: <small>Rules for naming, coloring, and grouping code</small>

> ### <br>*Errors & Malfunctions*: <small>Precautionary procedures in case of emergency</small>


---

## Introduction


### Process


### Diagram:
```mermaid
flowchart LR
    Client -- request --> Webserver
    Webserver -- WSGI --> DjangoApp/Project
    DjangoApp/Project -- ORM --> DjangoORM
    DjangoORM -- close --x Database/MySQL
```
```mermaid
flowchart LR
    Database/MySQL -- results --> DjangoORM
    DjangoORM -- process --> DjangoApp/Project
    DjangoApp/Project -- generate response --> Webserver
    Webserver -- response --x Client
```


```mermaid
flowchart TD
    A[Client] -- Enters --> B{Web / Internet}
    D[Server / AWS] -- Manages / Delivers --> G{Database / MySQL}
    B -- Requests --> C[Domain / URL]
    C[Domain / URL] -- Accesses --> D
    D -- Contains --> E[Software / Django]
    E -- Creates  --> F[Data]
    F -- Stores   --> G 
```


## Workflow
```mermaid
erDiagram
    DECK ||--o{ USER : creates
    DECK {
        string deckName
        string category
        string description
        string[] preset
    }
    APP ||--o{ USER : creates
    USER {
        string(99) username "Only 99 characters are allowed"
        string password
        string email
    }
    DECK ||--o{ FLASHCARD : contains
    FLASHCARD {
        string question
        string answer
    }
    CLIENT ||--o{ APP : visits
```
```mermaid
erDiagram
    USER ||--o{ DECK : creates
    USER {
        string username
        string password
        string email
    }
    DECK ||--|{ FLASHCARD : contains
    DECK {
        string deckName
        string category
        string description
        string[] preset
    }
    FLASHCARD {
        string question
        string answer
        float proficiency
    }
```

### Instructions


### Conventions


## Errors & Malfunctions
