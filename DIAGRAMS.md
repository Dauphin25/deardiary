# DearDiary — UML Diagrams

## 1. Component Diagram

Shows the major Django applications, their internal modules, and how they connect to each other and external services.

```mermaid
graph TD
    Browser([🌐 Web Browser])

    Browser -->|HTTP requests| Router

    subgraph DearDiary ["DearDiary — Django Application"]

        subgraph DiaryProject ["⚙️ DiaryProject (config)"]
            Router["urls.py\nMain Router"]
            Settings["settings.py\nConfiguration"]
        end

        subgraph diary ["📔 diary app"]
            DViews["views.py\n(CRUD, PDF export,\nresponse handling)"]
            DModels["models.py\n QuestionSet · Question\n AnswerSession · Answer\n QuestionSetStyle · NewsItem"]
            DForms["forms.py\n(QuestionSet & Question forms)"]
            DAdmin["admin.py\n(Inline question admin)"]
            DTags["templatetags/\ndiary_extras.py"]
        end

        subgraph users ["👤 users app"]
            UViews["views.py\n(register, login, logout,\nprofile, upgrade, set_language)"]
            UModels["models.py\n CustomUser · UserProfile\n Notification"]
            UForms["forms.py\n(CustomUserCreationForm)"]
            UUtils["utils.py\n(get_limits, can_answer_more,\ncan_create_qset)"]
            USignals["signals.py\n(auto-create UserProfile)"]
        end

        subgraph pages ["📄 pages app"]
            PViews["views.py\n(home, page_detail,\ndownload_share_card)"]
            PModels["models.py\n(Page — CMS)"]
        end

        subgraph Templates ["🖼️ Templates"]
            Base["base.html\nheader.html / footer.html"]
            DiaryTpl["style_basic/classic/\ngrunge/retro.html"]
            HomeTpl["home.html\nleaderboard · carousel"]
            UserTpl["register.html\nlogin.html · profile.html"]
        end

        subgraph i18n ["🌍 Locale (i18n)"]
            EN["English"]
            KA["Georgian"]
            DE["German"]
            RU["Russian"]
        end
    end

    subgraph External ["External / Infrastructure"]
        DB[("SQLite3\nDatabase")]
        Playwright["Playwright\n(PDF · Share-card PNG)"]
        QRLib["qrcode\nlibrary"]
        CKEditor["CKEditor\nRich Text"]
    end

    Router --> DViews
    Router --> UViews
    Router --> PViews

    DViews --> DModels
    DViews --> DForms
    DViews --> Playwright
    DViews --> DiaryTpl

    UViews --> UModels
    UViews --> UForms
    UViews --> UUtils
    UViews --> UserTpl
    USignals --> UModels

    PViews --> PModels
    PViews --> Playwright
    PViews --> QRLib
    PViews --> HomeTpl

    DModels --> DB
    UModels --> DB
    PModels --> DB
    PModels --> CKEditor

    UUtils --> UModels
    DViews --> UUtils

    Settings -.->|configures| diary
    Settings -.->|configures| users
    Settings -.->|configures| pages
```

---

## 2. Activity Diagram — Core User Flow

Shows the end-to-end journey: registration → diary creation → sharing → answering → viewing responses.

```mermaid
flowchart TD
    A([Start: User visits DearDiary]) --> B{Authenticated?}

    B -- No --> C[Register / Login]
    C --> D{Registration\nor Login?}
    D -- Register --> E[Fill CustomUserCreationForm]
    E --> F[Create CustomUser\n+ UserProfile via signal]
    F --> G[Redirect to Homepage]
    D -- Login --> H[Authenticate credentials]
    H --> I{Valid?}
    I -- No --> C
    I -- Yes --> G

    B -- Yes --> G

    G[Homepage\nNews · Leaderboard\nProfile summary] --> J{User action?}

    J -- Create Diary --> K[Go to /diary/create/]
    K --> L[Fill title, description,\nselect visual style]
    L --> M{Free plan limit\nreached?}
    M -- Yes --> N[Show upgrade banner\n→ /users/upgrade/]
    N --> J
    M -- No --> O[Save QuestionSet\nwith UUID + slug]
    O --> P[Add / Edit Questions\n/diary/my-question-set/slug/]
    P --> Q[Copy shareable link\n/diary/answer/share/uuid/]
    Q --> R([Share link with friends])

    J -- View my diaries --> S[/diary/\nList of owned question sets]
    S --> T[Select a diary]
    T --> U[Owner view:\nstats + list of respondents]
    U --> V{Action?}
    V -- View response --> W[/diary/response/session_id/\nRead answers]
    W --> X{Download PDF?}
    X -- Yes --> Y[Playwright renders PDF\n/diary/response/session_id/download/]
    X -- No --> U
    V -- Edit questions --> P

    J -- View notifications --> Z[/users/profile/\nNotification list + stats]

    subgraph FriendFlow ["Friend / Respondent Flow"]
        R --> AA([Friend opens UUID link])
        AA --> AB{Friend authenticated?}
        AB -- No --> AC[Redirect to login]
        AC --> AB
        AB -- Yes --> AD{Owns this diary?}
        AD -- Yes --> AE[Redirect: cannot answer own diary]
        AD -- No --> AF{Weekly answer\nlimit reached?}
        AF -- Yes --> AG[Show limit message\nwith upgrade prompt]
        AF -- No --> AH[Render answer form\nin selected theme style]
        AH --> AI[Friend fills in answers]
        AI --> AJ[POST → create AnswerSession\n+ Answer records]
        AJ --> AK[Increment weekly_answer_count\non friend's UserProfile]
        AK --> AL[Create Notification\nfor diary owner]
        AL --> AM[Redirect friend to Homepage]
    end

    AL -.->|Owner sees notification| Z
```

---

## 3. Sequence Diagram — Answering a Shared Diary

Detailed interaction between the browser, Django views, models, and the database when a friend answers a diary.

```mermaid
sequenceDiagram
    actor Friend as Friend (Browser)
    participant View as diary/views.py<br/>answer_shared_question_set()
    participant QS as QuestionSet model
    participant UP as UserProfile model
    participant AS as AnswerSession model
    participant Notif as Notification model
    participant DB as SQLite3

    Friend->>View: GET /diary/answer/share/<uuid>/
    View->>DB: QuestionSet.objects.get(share_uuid=uuid)
    DB-->>View: QuestionSet instance
    View->>UP: can_answer_more(request.user)
    UP->>DB: SELECT weekly_answer_count, next_reset
    DB-->>UP: counts
    UP-->>View: True / False

    alt Limit reached
        View-->>Friend: 403 / redirect with message
    else Can answer
        View-->>Friend: Render answer form (theme template)
        Friend->>View: POST answers[]
        View->>DB: BEGIN TRANSACTION
        View->>AS: AnswerSession.objects.create(question_set, respondent)
        AS->>DB: INSERT AnswerSession
        loop For each question
            View->>DB: INSERT Answer(session, question_text, answer_text)
        end
        View->>UP: increment weekly_answer_count
        UP->>DB: UPDATE UserProfile
        View->>Notif: Notification.objects.create(owner notified)
        Notif->>DB: INSERT Notification
        View->>DB: COMMIT
        View-->>Friend: Redirect to homepage
    end
```
