# CK-12 Overall System Architecture

This document provides a comprehensive reverse-engineered architectural specification of the **CK-12 Foundation platform** (`https://www.ck12.org`), focusing on the assessment and practice subsystems (`/assessment/ui/browse/practice/`).

---

## 1. System Topology Overview

CK-12 operates as a distributed, high-scale digital learning and adaptive assessment platform. The architecture is organized around the **FlexBook Core (`flxcore`)** platform, decoupling static content delivery, ontology search, user analytics, and the real-time adaptive assessment state machine.

```mermaid
graph TD
    subgraph ClientLayer["Client Tier (Web & Embedded Apps)"]
        Browser["Desktop & Mobile Browsers (Backbone/RequireJS SPA)"]
        LTI["LMS Embeds (Canvas, Google Classroom, Schoology via LTI)"]
        MobileWeb["Mobile Web Client"]
    end

    subgraph EdgeCDN["Edge & Gateway Tier"]
        Cloudflare["Cloudflare / S3 CloudFront CDN"]
        ApiGateway["API Gateway / Routing Proxy (Nginx)"]
    end

    subgraph CoreServices["Backend Service Tier (flxcore)"]
        TaxonomySvc["Taxonomy & Browse Service (/flx/get/info/browseTerm/)"]
        ModalitySearch["Modality Catalog Engine (/flx/search/direct/modality/)"]
        AssessmentEngine["Adaptive Assessment Engine (/assessment/api/)"]
        HintSvc["Dynamic Hint & Remediation Service (/flx/search/hints/)"]
        GamificationSvc["Points & Awards Service (/assessment/api/get/info/pointsAndAwards)"]
        UserProgressSvc["User Progress & Mastery Ledger (/assessment/api/sc/)"]
    end

    subgraph DataTier["Data & Persistence Tier"]
        SolrCluster["Search & KG Index Cluster (Apache Solr / Elasticsearch)"]
        CurriculumDB["Canonical Knowledge Graph DB (PostgreSQL / Relational Ontology)"]
        StudentStateDB["Student Learning States & Timeseries Log (Cassandra / DynamoDB)"]
        MediaS3["Media & Simulation Asset Storage (Amazon S3)"]
    end

    subgraph TelemetryLayer["Telemetry & Analytics Tier"]
        DexterJS["DexterJS Event Pipeline (ClientID: 24839961)"]
        Optimizely["Optimizely Feature Flags & A/B Engine"]
        GTM["Google Tag Manager / Analytics"]
    end

    Browser --> Cloudflare
    LTI --> Cloudflare
    MobileWeb --> Cloudflare

    Cloudflare --> MediaS3
    Cloudflare --> ApiGateway

    ApiGateway --> TaxonomySvc
    ApiGateway --> ModalitySearch
    ApiGateway --> AssessmentEngine
    ApiGateway --> HintSvc
    ApiGateway --> GamificationSvc
    ApiGateway --> UserProgressSvc

    TaxonomySvc --> SolrCluster
    TaxonomySvc --> CurriculumDB
    ModalitySearch --> SolrCluster
    AssessmentEngine --> CurriculumDB
    AssessmentEngine --> StudentStateDB
    HintSvc --> CurriculumDB
    UserProgressSvc --> StudentStateDB
    GamificationSvc --> StudentStateDB

    Browser -.-> DexterJS
    Browser -.-> Optimizely
    Browser -.-> GTM
```

---

## 2. Component Deconstruction

### 2.1 Client Tier: The Assessment SPA
* **Technology Stack**:
  - Module Loader: **RequireJS** (`require.js`) for AMD dynamic bundle loading.
  - Framework: **Backbone.js** (Models, Collections, Views) with **Underscore.js** templating (`<%= subjectName %>`, `<%= branch %>`).
  - Layout Engine: **Foundation Responsive CSS Grid** (`medium-12 large-12 columns`).
  - Core Bundles:
    - `config-bundle.js`: Global configuration and preview image maps.
    - `browse-bundle.js` (174 KB): UI controller for subject trees, concept filters, and pagination.
    - `browse-vendors-bundle.js`: Third-party vendor dependencies (jQuery, lodash/underscore, UI helpers).
    - `dexterScriptConfig.js`: Internal tracking instrumentation.
* **Client Routing & Initialization**:
  - When navigating to `/assessment/ui/browse/practice/{subject}/?topicHandle={topic}`, the SPA parses the path and URL query parameters.
  - It triggers parallel asynchronous fetches:
    1. Taxonomy metadata (`/flx/get/info/browseTerm/descendants/{subject}`)
    2. Modality artifacts (`/flx/search/direct/modality/minimal/asmtpractice/{topic}`)
    3. User profile & mastery stats (`/assessment/api/get/info/my`)

### 2.2 Backend Tier: `flxcore` (FlexBook Core Platform)
* **API Signature & Origin**:
  - Responses declare their source in the header metadata: `{"source": "flxcoreExt-25-219", "status": 2006, "QTime": 0}`.
  - The `QTime` parameter confirms that read queries pass through an indexed search engine (Apache Solr or Elasticsearch) rather than hitting relational tables directly.
* **Key Microservices**:
  1. **Taxonomy & Browse Engine**: Serves the hierarchically encoded subject-branch-topic tree (e.g., `SCI.LSC.100`).
  2. **Modality Search Service**: Dispatches all learning modalities bound to a concept.
  3. **Adaptive Test Controller**: Manages student test session lifecycle, dynamically serving questions based on current running mastery.
  4. **Remediation & Hint Engine**: Evaluates student incorrect answers in real time to dispense targeted hints or trigger concept branching.

---

## 3. Data Flow & Adaptive Practice Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant Browser as Browser Client (SPA)
    participant Gateway as API Gateway
    participant FlxCore as flxcore Search & KG
    participant Asmt as Adaptive Engine
    participant Ledger as Student State Ledger

    Student->>Browser: Selects "Foundations of Life Science" Practice
    Browser->>Gateway: GET /flx/search/direct/modality/minimal/asmtpractice/foundations-of-life-science
    Gateway->>FlxCore: Query indexed modality artifacts
    FlxCore-->>Browser: Returns 1.2 MB artifact payload (question IDs, modalities, difficulty bands)
    
    Student->>Browser: Clicks "Start Practice"
    Browser->>Gateway: GET /assessment/api/get/info/test/practice/encodedid/{testId}
    Gateway->>Asmt: Initialize test session
    Asmt->>Ledger: Fetch student concept mastery level
    Ledger-->>Asmt: Current mastery = 45% (Developing)
    Asmt-->>Browser: Returns Question 1 (Medium Difficulty)
    
    Student->>Browser: Submits Incorrect Answer
    Browser->>Gateway: POST /assessment/api/sc/change/concept/
    Gateway->>Asmt: Evaluate response & update Bayesian knowledge state
    Asmt->>Gateway: Fetch remediation hint
    Gateway->>FlxCore: GET /flx/search/hints/?questionId=...
    FlxCore-->>Asmt: Specific misconception hint
    Asmt-->>Browser: Dispenses Hint & branches to foundational prerequisite question
    
    Student->>Browser: Answers 10 questions successfully (Reaches 100% Mastery)
    Browser->>Gateway: POST session completion
    Gateway->>Asmt: Update concept status to "Proficient"
    Asmt->>Ledger: Write persistent achievement record
    Asmt->>Gateway: GET /assessment/api/get/info/pointsAndAwards/concepts/my?eids=...
    Gateway-->>Browser: Award badges, points, and streak increment
```

---

## 4. Telemetry, Analytics, and A/B Testing

1. **DexterJS**:
   - CK-12's proprietary behavioral event logger.
   - Script: `/media/dexterjs/dexterjs.min.js`.
   - Initialized as:
     ```javascript
     window.dexterjs.set('config', {
       clientID: 24839961,
       declarativePlugin: { enabled: true, additionalDomEvents: "touchend" }
     });
     ```
   - Automatically attaches to DOM click/touch events on concepts, modalities, and answer buttons, streaming telemetry back to CK-12 analytics backends.
2. **Optimizely Integration**:
   - Script: `//cdn.optimizely.com/js/28889104.js`.
   - Used for server-side and client-side feature flags, testing question presentation formats, UI layouts, and practice incentives.
3. **Google Tag Manager (GTM)**:
   - Configured only when `!window.assessment_configs.isApp()`. When embedded inside native mobile wrappers or LMS iframes, GTM is suppressed to protect student privacy (COPPA/FERPA compliance).
