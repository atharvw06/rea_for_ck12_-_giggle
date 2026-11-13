# Giggle Academy Knowledge Graph System & Isolation Architecture

This document analyzes the learning graph structure, developmental skill ontologies, and multi-layered isolation mechanisms of **Giggle Academy** based on empirical reverse engineering of client bundles, API endpoints, and event telemetry.

---

## 1. Learning Graph Structure: The Adventure Map DAG

Unlike CK-12's academic textbook taxonomy, Giggle Academy transforms its Knowledge Graph into a **Gamified Journey / Adventure Map Directed Acyclic Graph (DAG)**.

```mermaid
graph TD
    subgraph WorldMap["1. The Adventure World Map DAG (Macro-Graph)"]
        Island1["Island 1: Alphabet & Phonics Kingdom"]
        Island2["Island 2: Numbers & Animal Farm"]
        Island3["Island 3: Storybook Wonderland"]
        Island4["Island 4: Math Explorers"]
        Island1 --> Island2
        Island2 --> Island3
        Island3 --> Island4
    end

    subgraph LevelNodes["2. Level Nodes (Micro-Graph)"]
        Level1["Level 1.1: Letter A Sound & Shape"]
        Level2["Level 1.2: Letter B Sound & Shape"]
        Level3["Level 1.3: Blending Sound 'at' (Cat, Bat)"]
        Level4["Level 1.4: Sight Word 'The'"]
        Level5["Level 1.5: Decodable Story: The Cat"]
        Level1 --> Level2
        Level2 --> Level3
        Level3 --> Level4
        Level4 --> Level5
    end

    subgraph MultimodalActivities["3. Multi-Sensory Modalities per Node"]
        Song["Song / Nursery Rhyme (/songs)"]
        Game["Interactive Phonics Game"]
        Speaking["AI Speech Evaluation (/growth-center/speaking)"]
        Story["Audio Storybook (/story/read/:id)"]
        Worksheet["Printable Activity Sheet (/worksheets)"]
    end

    Island1 --> Level1
    Level1 --> Song
    Level1 --> Game
    Level1 --> Speaking
    Level5 --> Story
    Level5 --> Worksheet
```

### 1.1 The Developmental Skill Ontologies

Giggle Academy partitions early childhood knowledge into three distinct developmental pillars:

1. **Early Literacy & Phonics Graph**:
   - *Stage 1 (Phonemic Awareness)*: Sound discrimination, rhyming, beginning sounds.
   - *Stage 2 (Letter-Sound Correspondence)*: Single consonants and short vowels (A, B, C...).
   - *Stage 3 (CVC Blending)*: Consonant-Vowel-Consonant words (cat, dog, pen, sun).
   - *Stage 4 (High-Frequency Sight Words)*: Non-phonetic words (the, was, you, said).
   - *Stage 5 (Decodable Reading & Fluency)*: Contextual children's storybooks with real-time word highlighting.
   - *Stage 6 (Oral Expression)*: Speech recognition verification via `/api/growth-center/speaking/query/{id}`.

2. **Early Numeracy & Logic Graph**:
   - *Stage 1 (Subitizing & One-to-One Correspondence)*: Counting up to 5 with visual objects.
   - *Stage 2 (Numeral Recognition & Writing)*: Associating digits `0-9` with quantities.
   - *Stage 3 (Basic Operations & Comparison)*: Bigger/smaller, addition within 10 using animated physical metaphors.
   - *Stage 4 (Spatial & Geometry)*: Shapes, patterns, sorting.

3. **Life Skills, Habits & Socio-Emotional Graph**:
   - Hygiene, manners, sharing, bedtime routines, and safety taught through musical rhymes and animated cartoons.

---

## 2. Knowledge Graph Isolation Strategies

Teaching children across diverse cultures, languages, and developmental ages requires sophisticated graph isolation.

```mermaid
graph LR
    subgraph LinguisticIsolation["1. Linguistic Graph Isolation"]
        EnglishDAG["English Phonics DAG (Alphabet -> CVC -> Blends)"]
        SpanishDAG["Spanish Syllabic DAG (A,E,I,O,U -> Ma,Me,Mi,Mo,Mu)"]
        ChineseDAG["Chinese Character & Pinyin DAG"]
    end

    subgraph SharedMechanics["Shared Game Mechanics Engine"]
        Engine["Drag & Drop, Tracing, Balloon Pop, Memory Match"]
    end

    subgraph CohortIsolation["2. Age-Cohort Track Isolation"]
        ToddlerTrack["Toddler Track (Ages 2-4: Songs, Sensory, Motor)"]
        PreKTrack["Pre-K Track (Ages 4-5: Letters, Numbers, Shapes)"]
        ElementaryTrack["Early Elementary (Ages 6-7: Reading, Math, Logic)"]
    end

    subgraph EdgeIsolation["3. Offline Edge Sub-Graph Slice"]
        CloudMaster["Central Cloud Master KG (creator.giggleacademy.com)"]
        LocalSlice["Local Device Sub-Graph Slice (SQLite in APK)"]
    end

    subgraph Personalization["4. Onboarding Diagnostic Isolation"]
        Diagnostic["Diagnostic Assessment"]
        CustomCourse["Personalized Learning Path (onboarding_custom_course_ready)"]
    end

    EnglishDAG --- Engine
    SpanishDAG --- Engine
    ChineseDAG --- Engine

    CloudMaster -->|offline_lesson_manage| LocalSlice
    Diagnostic --> CustomCourse
```

### 2.1 Linguistic & Phonics Graph Isolation
* **The Problem**: Phonics cannot be translated literally between languages. English is an alphabetic language relying on phonemes and digraphs (`sh`, `ch`, `th`). Spanish is syllable-timed and taught via open syllables (`ma`, `me`, `mi`, `mo`, `mu`). Chinese uses logographic characters with Pinyin tones. Attempting to use a single unified graph with string translations would result in nonsensical phonics lessons.
* **Giggle Academy's Solution**:
  - **Complete Linguistic DAG Isolation**: Each language has its own independent Knowledge Graph topology.
  - **Shared Interaction Mechanics**: While the curriculum DAG is completely isolated per language, the interactive *game engines* (tracing letters, matching pairs, balloon-popping words, rhythm-tapping songs) are reusable components parameterized by the language-specific graph nodes.

### 2.2 Age-Cohort & Developmental Milestone Isolation
* **The Problem**: Presenting a 3-year-old with multi-digit subtraction or abstract grammar causes frustration, while presenting an 8-year-old with single-letter matching causes boredom.
* **Giggle Academy's Solution**:
  - The master graph is strictly partitioned into **Developmental Tracks**:
    - `Track 1 (Toddler, 2-4)`: Sensory perception, colors, animal sounds, nursery rhymes.
    - `Track 2 (Preschool, 4-5)`: Alphabet, single phonemes, numbers 1-20, shapes.
    - `Track 3 (Early Elementary, 6-7)`: Decodable reading, sentences, addition/subtraction.
  - Prerequisite edges cannot cross track boundaries upwards without passing a formal **Level-Up Milestone Quiz** (`quiz_level_up_invite_popup`).

### 2.3 Edge Sub-Graph Slices & Offline-First Isolation
* **The Problem**: Children frequently play on tablets in offline environments (in vehicles, flights, or developing regions with intermittent internet). A cloud-dependent graph traversal would break the gameplay experience.
* **Giggle Academy's Solution**:
  - The full curriculum is authored and stored centrally on `creator.giggleacademy.com`.
  - When the app is connected, the client downloads a bounded **Sub-Graph Slice** via `offline_lesson_manage`.
  - This slice contains:
    1. A localized SQLite database specifying the next 10-20 level nodes, unlock conditions, and prerequisite states.
    2. Associated multimedia assets (audio phonics files, sprite sheets, and animations).
  - The local game loop operates entirely on this self-contained sub-graph slice. When network connectivity is restored, student milestone events are batched and synced to the cloud.

### 2.4 Diagnostic Onboarding & Personalized Path Isolation
* **The Problem**: Children enter the app with wildly varying skill levels (some already know the alphabet at age 3, others do not at age 5).
* **Giggle Academy's Solution**:
  - On first launch, a brief interactive diagnostic game evaluates baseline literacy and numeracy.
  - The engine fires the telemetry event `onboarding_custom_course_ready`.
  - Instead of forcing the child into Level 1.1 or modifying the global curriculum, the engine constructs a **Virtual Custom Path** by unlocking and filtering appropriate nodes from the master DAG, providing an immediate tailored trajectory.
