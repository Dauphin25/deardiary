# DearDiary — დიაგრამები

## ER დიაგრამა — მონაცემთა ბაზის სქემა (PNG)

![ER დიაგრამა](diagrams/er_diagram_ka.png)

> `*` = პირველადი გასაღები (PK) · `>` = გარე გასაღები (FK)
> ლურჯი = users app · მწვანე = diary app · იასამნისფერი = pages app

---

## აქტივობის დიაგრამა (PNG)

![აქტივობის დიაგრამა](diagrams/activity_diagram_ka.png)

---

## კომპონენტების დიაგრამა

სისტემის მთავარი ნაწილები და მათი კავშირები.

```mermaid
graph TD
    Browser([ბრაუზერი])

    Browser -->|HTTP| Router["urls.py — მარშრუტიზატორი"]

    subgraph App ["DearDiary — Django"]
        subgraph diary ["📔 diary"]
            DV["views.py"]
            DM["models.py\nQuestionSet · Question\nAnswerSession · Answer"]
        end

        subgraph users ["👤 users"]
            UV["views.py"]
            UM["models.py\nCustomUser · UserProfile\nNotification"]
        end

        subgraph pages ["📄 pages"]
            PV["views.py"]
        end
    end

    subgraph External ["გარე სერვისები"]
        DB[("SQLite3")]
        PW["Playwright\nPDF / PNG"]
        QR["QR კოდი"]
    end

    Router --> DV & UV & PV
    DV --> DM --> DB
    UV --> UM --> DB
    PV --> PW & QR
    DV --> PW
```

---

## აქტივობის დიაგრამა (Mermaid)

მომხმარებლის მთავარი მარშრუტი: რეგისტრაცია → დღიურის შექმნა → გაზიარება → პასუხი → ნახვა.

```mermaid
flowchart TD
    A([დაწყება]) --> B[რეგისტრაცია / შესვლა]
    B --> C[მთავარი გვერდი]
    C --> D[დღიურის შექმნა]
    D --> E[კითხვების დამატება]
    E --> F[ლინკის გაზიარება]

    F -->|UUID ლინკი| G[მეგობარი ხსნის ლინკს]
    G --> H{ლიმიტი?}
    H -- გადაჭარბებულია --> I[პრემიუმი საჭიროა]
    H -- კარგია --> J[პასუხების შეყვანა]
    J --> K[გაგზავნა]
    K --> L[შეტყობინება მფლობელს]

    F --> M[პასუხების ნახვა]
    L -.-> M
    M --> N[PDF-ის გადმოწერა]
    N --> O([დასასრული])
```
