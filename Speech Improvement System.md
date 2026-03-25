# Speech Improvement System — Project Handoff

## What This Is

A daily speech training system with two workflows. Each workflow records audio/video, runs it through analysis tools, and produces JSON metrics. Those metrics feed into an LLM (Gemini) for coaching feedback. Results are logged over time to track progress.

---

## Two Tools

### Tool 1: Speech Analysis Tool (existing)

- **Input:** `.mp4`, `.mov`, `.mkv` video OR `.txt` transcript
- **What it does:** Transcribes audio via Whisper, then analyzes the **text**
- **Output:** JSON appended to a history file

**Output schema:**
```json
{
  "date": "ISO timestamp",
  "source_file": "filename",
  "file_id": "hash",
  "metrics": {
    "transcript": "full text",
    "statistics": {
      "total_words": int,
      "unique_words": int,
      "total_filler_words": int,
      "filler_word_percentage": float
    },
    "readability": {
      "score": float,
      "interpretation": "string"
    },
    "filler_words": {
      "word": count
    },
    "word_frequency": [["word", count]]
  }
}
```

### Tool 2: Articulation Analyzer (new)

- **Input:** `.mp4`, `.mov`, `.mkv`, `.m4a`, `.wav` audio/video
- **Pipeline:** ffmpeg converts to 16kHz mono `.wav` → faster-whisper transcribes with word-level confidence → opensmile (eGeMAPS) extracts acoustic features
- **What it does:** Analyzes **how it sounds**, not what was said
- **Output:** JSON appended to `metrics_history.json`

**Output schema:**
```json
{
  "date": "ISO timestamp",
  "source_file": "filename",
  "metrics": {
    "text": "transcript",
    "word_count": int,
    "weak_words": [
      {
        "word": "string",
        "start": float,
        "end": float,
        "probability": float
      }
    ],
    "pause_count": int,
    "avg_pause_duration_sec": float,
    "speech_rate_sps": float,
    "f1_variance_sd": float,
    "f2_variance_sd": float,
    "mean_hnr": float
  }
}
```

**Key metrics explained:**
- `weak_words`: Words where Whisper confidence < 0.7. Low confidence = poorly articulated.
- `f1_variance_sd`: Jaw opening range. Higher = more dynamic jaw movement. Should increase over time.
- `f2_variance_sd`: Tongue position range. Higher = more distinct vowel shaping.
- `mean_hnr`: Voice clarity. Clean speech = 15-20+. Low = muffled.
- `speech_rate_sps`: Syllables per second. Normal = 3-5. Too high = rushing/slurring.
- `pause_count` / `avg_pause_duration_sec`: Gap detection between words (threshold: 0.4s+).

---

## Two Workflows

### Workflow A: Daily Pen Reading (30 min)

**Purpose:** Train jaw articulation mechanically. Track clarity improvement over time.

**Data flow:**
```
User reads book with pen in teeth (30 min)
        ↓
    Records audio
        ↓
    Runs Tool 2 (Articulation Analyzer)
        ↓
    JSON appended to metrics_history.json
        ↓
    User pastes JSON into Gemini (Daily Articulation Prompt)
        ↓
    Gemini returns: weak word analysis + ONE focus for tomorrow
        ↓
    User copies response into articulation_log.md
```

**Runs:** Every day
**Tools used:** Tool 2 only
**Output files:** `metrics_history.json`, `articulation_log.md`

---

### Workflow B: 5-Min Free Talk (video)

**Purpose:** Practice structured speaking. Combine word-level, audio-level, and visual self-review into one feedback loop.

**Data flow:**
```
User picks a topic + framework (3-2-1, CCC, or Rule of Three)
        ↓
    Records 5-min video of themselves talking
        ↓
    Runs Tool 1 (Speech Analysis) → JSON with text metrics
    Runs Tool 2 (Articulation Analyzer) → JSON with audio metrics
        ↓
    User self-reviews video:
      - Pass 1 (muted): notes on body language, hands, posture, eyes
      - Pass 2 (eyes closed): notes on pace, tone, fillers, thought completion
        ↓
    Three inputs merge → pasted into Gemini (5-Min Talk Prompt)
      1. Speech Analysis JSON
      2. Articulation Analysis JSON
      3. Manual self-review notes (plain text)
        ↓
    Gemini returns: grade on structure/clarity/articulation/delivery/body +
                    ONE biggest problem + ONE drill for next session
        ↓
    User copies response into speech_log.md
```

**Runs:** Every other day
**Tools used:** Tool 1 + Tool 2
**Output files:** Speech Analysis JSON, `metrics_history.json`, `speech_log.md`

---

### Weekly Review

**Data flow:**
```
All 7 daily articulation JSONs from the week
        ↓
    Pasted into Gemini (Weekly Prompt)
        ↓
    Gemini returns: trend analysis (weak words repeating?, F1/F2 trend,
                    HNR trend, speech rate trend) + next week's focus
        ↓
    Appended to logs
```

---

## File Structure

```
project/
├── tool1/                    # Speech Analysis Tool
│   ├── main.py
│   └── (outputs speech analysis JSON)
├── tool2/                    # Articulation Analyzer
│   ├── main.py
│   └── metrics_history.json  # Append-only. All daily records.
├── recordings/               # Raw audio/video files
├── articulation_log.md       # Daily Gemini feedback (pen reading)
├── speech_log.md             # Every-other-day Gemini feedback (free talk)
└── prompts/
    ├── daily_articulation.md
    ├── five_min_talk.md
    └── weekly_review.md
```

---

## JSON Storage Pattern

Both tools **append** to their respective JSON files. Structure is a JSON array:

```json
[
  { "date": "2026-02-20T14:40:49", "source_file": "day1.m4a", "metrics": { ... } },
  { "date": "2026-02-21T14:35:12", "source_file": "day2.m4a", "metrics": { ... } },
  { "date": "2026-02-22T14:42:33", "source_file": "day3.m4a", "metrics": { ... } }
]
```

This makes it simple to: load the array, filter by date range, compute trends across sessions, and visualize progress over time.

---

## Dependencies

**Tool 1 (Speech Analysis):**
- Python 3.8+
- openai-whisper, nltk, matplotlib, textstat
- ffmpeg

**Tool 2 (Articulation Analyzer):**
- Python 3.8+
- faster-whisper, opensmile, syllables
- ffmpeg (for audio conversion to 16kHz mono wav)

---

## What This Handoff Does NOT Cover

- Frontend (to be built separately)
- Video playback or visual analysis tooling (body language is manual self-review)