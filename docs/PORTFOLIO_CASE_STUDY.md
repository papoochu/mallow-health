# Mallow — Portfolio Case Study 🌿

## Summary

Mallow is a personal health-data dashboard and intelligent health companion that explores how wearable and wellness measurements can be made more understandable without turning descriptive statistics into medical diagnoses.

I built the project across two application stacks:

- a deployed Python + Streamlit web application
- a React Native + Expo + TypeScript mobile application

The project combines data ingestion, statistical analysis, deterministic natural-language querying, anomaly detection, automated testing, and privacy-conscious product design.

---

## The problem

Health data is often presented as isolated values:

- today's resting heart rate
- last night's sleep
- a single HRV measurement

Those numbers are difficult to interpret without personal context.

A second problem is that health software can easily overstate what a statistical pattern means. A correlation may be presented as if it implies cause. A model may label a point unusual and make it sound medically dangerous. A generic reference range can obscure an individual's own recent pattern.

Mallow was designed around a narrower, safer question:

> What can the person's own recent data describe, and how can that description be communicated clearly without pretending it is a diagnosis?

---

## Product approach

Mallow uses several complementary analytical views.

### Personal baselines

The application calculates recent personal averages, standard deviation, and z-scores.

Instead of "normal / abnormal," the interface uses language such as:

- Near your usual range
- Somewhat above your baseline
- Unusually below your baseline

This describes statistical distance from the person's recent history.

### Trends

Mallow uses least-squares regression and evaluates both relative change and fit quality.

The UI distinguishes:

- no clear trend
- gradual change
- clear change

The output explicitly says that a recent trend is not a prediction.

### Relationships

Pairwise non-missing measurements are aligned and analyzed with Pearson correlation.

The application reports strength and direction while explicitly separating association from causation.

### Period comparisons

Recent windows are compared with the equally sized period immediately before them.

The language remains descriptive: higher, lower, or approximately the same.

### Multivariate anomaly detection

The web application uses Isolation Forest to identify whether the latest overall measurement pattern is statistically unusual relative to recent history.

The model is supplemented with baseline deviations so the result remains interpretable.

---

## Data architecture

A major design goal was to avoid coupling the analytics to one data source.

The web application can receive:

- deterministic synthetic records
- imported Apple Health ZIP/XML data

The mobile application is structured around:

- deterministic demo data
- a native device-health service boundary

All of those paths ultimately produce structured health records consumed by reusable analytics modules.

That means the product can change data sources without rewriting the entire analysis layer.

---

## Apple Health integration strategy

### Web

The web app supports manual Apple Health export import.

The parser:

- streams XML rather than loading the entire export at once
- converts supported units
- merges overlapping sleep records
- separates deep and REM sleep
- derives pulse pressure and mean arterial pressure
- preserves missing data

The deployed public demo remains synthetic-only so private exports are not sent to a public portfolio instance.

### Mobile

The mobile app includes a native device-health service layer designed for HealthKit / Health Connect access.

Because physical iOS installation requires Apple signing, final HealthKit validation is intentionally deferred until the final project stage.

The code is therefore documented as **integration-ready**, not as physically validated.

That distinction is deliberate: the portfolio should show what was actually tested.

---

## Intraday design

The mobile application includes a Today screen with intraday measurements.

Intraday records are modeled separately from daily summaries.

This avoids a subtle but important analytical error: an afternoon heart-rate sample should not be compared directly with a daily resting-heart-rate baseline as if they represented the same physiological context.

The Today view summarizes:

- latest measurement
- today's average
- minimum / maximum
- number of samples
- throughout-day timeline

---

## Ask Mallow

Ask Mallow is intentionally deterministic.

Instead of sending health questions to an unrestricted language model, it maps natural-language questions onto existing calculations.

For example:

- "How has my HRV changed this month?" → trend analysis
- "What is related to my sleep?" → strongest correlations
- "How does this week compare with last week for resting heart rate?" → adjacent-period comparison

This makes the result traceable to a known function and reduces the risk of unsupported medical interpretation.

---

## Engineering decisions

### Shared behavior across two stacks

The web analytics were first implemented in Python and then ported into TypeScript for the mobile application.

The implementations preserve the same concepts and thresholds for:

- personal baselines
- trend classification
- relationship strength
- comparison wording
- data support

This provided a useful cross-language consistency challenge rather than simply rebuilding the UI.

### Deterministic synthetic data

Synthetic data is generated from fixed seeds.

The generator includes controlled relationships such as:

- sleep ↔ HRV
- sleep ↔ resting heart rate
- meal-like glucose rises
- intraday activity-related heart-rate changes

This makes the public demo reproducible and gives automated tests stable behavior.

### Missing data

Real-data mode never silently falls back to synthetic measurements.

If a measurement is unavailable, it stays unavailable.

### Test strategy

The project currently includes:

- 34 Python tests
- 23 TypeScript tests
- 57 total automated tests

CI runs the Python and mobile suites independently.

Tests focus on analytical behavior and edge cases rather than superficial snapshots.

---

## Safety and privacy design

Mallow deliberately avoids several common failure modes.

It does not:

- diagnose illness
- recommend treatment
- interpret statistical anomaly as medical danger
- call data-support labels "clinical confidence"
- claim correlation implies causation
- invent missing real measurements
- upload private health exports to the public demo

The public deployment is synthetic-only.

---

## Current limitations

The project is a portfolio prototype rather than a medical device.

Important limitations include:

- no prospective clinical validation
- no clinician-facing workflow
- no authentication or production user accounts
- correlations do not control for confounders
- linear trends may miss nonlinear behavior
- native iOS HealthKit access still requires final physical-device validation
- Ask Mallow is deterministic rather than conversationally generative

---

## What I would validate next

The final planned project stage is physical iOS validation.

That includes:

- Apple Developer enrollment
- signed EAS development build
- real HealthKit authorization flow
- Apple Watch / Apple Health measurement reads
- denied-permission behavior
- real intraday sample handling
- final iPhone screenshots and demo recording

At that point the documentation can be updated from **integration-ready** to **validated on a physical iOS device**.

---

## What this project demonstrates

Mallow is intended to demonstrate more than dashboard design.

It combines:

- full-stack product thinking
- Python data engineering
- statistical reasoning
- machine-learning anomaly detection
- React Native / TypeScript development
- native-health integration architecture
- privacy-aware product decisions
- deterministic NLP routing
- automated testing
- continuous integration
- careful communication of uncertainty

The main engineering lesson was that health-data software benefits from treating **data source, analysis, presentation, and medical interpretation as separate concerns**.
