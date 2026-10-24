# Research Navigation and Contribution Audit Handoff (Round R3)

## 1. Executive Decision: Stay on the Authorized RAG Retrieval Theme

- **Selected Paper Direction (In-Scope):** Proceed with the **matched-capacity RAG retrieval boundary / negative-result paper** explaining when and why embedding/subspace geometry loses role and negation information while attempting paraphrase invariance under equal capacity and token budgets.
- **Why R2's Generic Bootstrap Software Paper Is Rejected as Default Pivot:**
  - The user's original question asks *which paraphrase changes semantic RAG retrieval should ignore while retaining facts and relations, under equal capacity/token budgets*.
  - The user authorized *autonomous changes within that broad research theme, with no new spending*.
  - R2's proposal to pivot to a generic fast-bootstrap software paper because the code is polished—and the latest handoff's label of an "easy publishable result"—is an internal stage proposal, not a user decision (`workflow-contract.md`: *"A proposal, a draft, an AI review, or silence is not a user decision"*). Abandoning semantic RAG retrieval for a standalone statistical software paper exits the authorized research theme and would require a new human **Topic** (and/or **Product/MVP**) decision.
  - Under `research-analyze` (`contribution-audit.md`), opportunities are ranked by scientific question importance, expected information gain, evidence gap, and validity—not by how "easy" or positive a spin sounds. A credible negative/boundary result with matched-capacity retrieval evidence directly answers the user's question and satisfies the completion contract.
- **Disposition of R1/R2 Bootstrap Code:** Retain as a **supporting inference method and reusable evaluation asset** (cluster/source-group bootstrap for uncertainty over paraphrase families and source documents in RAG retrieval metrics), not as the standalone topic of the paper.
- **Disposition of the Unconnected Category-Theory Lemma:** **Park / exclude from core manuscript claims.** Under `contribution-audit.md` and `reuse-and-simplification.md`, theory whose assumptions are unconnected to testable retrieval predictions adds no explanatory value. It will only re-enter if a concrete derivation in `research-design` maps its assumptions to a falsifiable retrieval capacity/role-collapse prediction; it must not block empirical analysis or paper drafting.

## 2. Artifact Inventory and Contribution Audit

No experimental numbers, source checks, or user confirmations are invented here. Artifacts are classified by their actual reported state:

| Asset / Location | Current Content | Role | Contribution Type | Evidence & Verification Status | Action & Reason |
| --- | --- | --- | --- | --- | --- |
| `Brief / Authority` (User prompt & delegation) | Semantic RAG paraphrase invariance vs. fact/relation retention under equal capacity/token budgets; tools may change; autonomous changes within theme; zero new spend | Project governance | Scope & constraints | **Verified instruction**; covers in-theme method/protocol refinement and negative/boundary conclusions | **Retain as governing contract** |
| `R0` (Sentence-pair subspace pilot) | Exploratory subspace geometry on sentence pairs; no retrieval outcomes | Supporting mechanism pilot | Explanation / mechanism | **Partial / limited**: establishes geometric representation behaviors on pairs, but lacks downstream RAG retrieval outcomes | **Integrate & connect**: link R0 subspace projections directly to matched-capacity retrieval outcomes |
| `R1` (Source-group bootstrap on R0) | Grouped bootstrap estimator for sentence-pair subspace pilot | Supporting statistical method | Evaluation / uncertainty tool | **Partial**: method works on R0 proxy metrics, not yet applied to retrieval metrics | **Adapt & reuse**: apply to source-grouped retrieval comparisons in R3 |
| `R2` (Polished bootstrap code + software-paper proposal) | Fast source-group bootstrap implementation + handoff proposing generic software paper | Reusable code asset + off-theme proposal | Reusable asset (code); off-topic claim (paper pivot) | Code is reported polished (engineering status requires local test check); topic pivot is **unapproved / out of scope** | **Demote pivot; retain code** for retrieval CIs and reproducibility appendix/package |
| `Candidate Retrieval Evidence` (Role/negation loss under matched capacity) | Matched-capacity retrieval runs showing role/negation loss in geometric subspaces | **Core contribution** | Boundary conditions / negative result & mechanism | **Discovered / requires audit**: raw run manifests, equal-token/capacity parity, split hygiene, and exclusion rules must be audited in `research-analyze` | **Prioritize & strengthen** as the central empirical backbone of the paper |
| `Category-theory lemma` | Abstract categorical lemma with no link to retrieval predictions | Redundant / unconnected material | Unconnected theory | **Unresolved / unsupported relevance**: no mapping from assumptions to retrieval metrics or capacity limits | **Remove from main path / park** unless `research-design` establishes a testable retrieval prediction |

### Defensible Framing (`Observation -> Explanation -> Conditions -> Meaning`)
- **Observation:** Under matched embedding/index capacity and equal token budgets, enforcing paraphrase-invariant geometric subspaces preserves surface-paraphrase similarity but degrades retrieval discrimination on role swaps and negation reversals (subject to audit of the exact run records and source-group bootstrap intervals).
- **Explanation:** Low-rank or invariance-projected subspaces compress directional/relational coordinates needed to separate non-commutative role bindings and polarity reversals from benign lexical/syntactic paraphrases.
- **Conditions:** Equal capacity/token budgets across comparators; grouped resampling by source document/paraphrase family; explicit separation of benign paraphrases vs. truth/relation-altering edits.
- **Meaning:** Semantic RAG retrieval cannot treat paraphrase invariance as pure geometric subspace quotienting without a capacity-allocated relational/polarity channel or hybrid scoring mechanism.

## 3. What May Proceed Immediately Without User Questions

Under the user's existing startup/theme delegation (*"autonomous changes within that broad research theme, no new spending"*) and `workflow-contract.md` (*"Advance already authorized work. Do not treat every handoff as a new approval"*), the next agent may immediately execute the following work using **free-only** model routes and local compute:

1. **Reject R2's off-theme pivot and lock Round R3 on the RAG role/negation boundary paper** (no approval needed because this stays inside the original theme and restores alignment with the user's question).
2. **Execute `research-analyze` (Evidence & Contribution Audit on Matched-Capacity Retrieval + R0/R1 Integration):**
   - Inspect the raw run manifests, configurations, seeds, and split definitions for the matched-capacity retrieval evidence.
   - Verify that capacity (embedding dimension, index size, memory footprint) and token budgets are strictly matched across baselines and subspace variants.
   - Apply the polished R1/R2 source-group bootstrap to the retrieval records to compute cluster-robust confidence intervals across paraphrase families and source documents.
   - Build the formal Claim-Evidence Map (estimand, denominator, dependence structure, source-group bootstrap CI, and `supported / limited / contradicted / unresolved` status).
3. **Execute `research-design` / `research-implement` (Bounded Mechanism & Ablation Check, Zero Spend):**
   - Connect R0's sentence-pair subspace metrics (e.g., variance explained in paraphrase vs. role/negation directions) to the retrieval failure modes as an explanatory mechanism check.
   - Quarantine the unconnected category-theory lemma unless a direct finite-dimensional linear/subspace proposition already explains the capacity trade-off more simply (`reuse-and-simplification.md`).
4. **Prepare M3 Principal-Conclusions Package & Draft Outline (`research-write` preparation):**
   - Queue findings for consolidated review at Milestone **M3** (principal conclusions) rather than stopping after every sub-step.

## 4. What Is Needed From the User (Non-Blocking Unless Triggered)

No immediate user reply is required to execute Round R3 above. Ask the user **only** for the following items where human authority or missing external context applies:

1. **Topic Override Confirmation (Only if the user actually wants the R2 software pivot):**
   - *Default action without reply:* Proceed with the semantic RAG paraphrase-invariance / role-negation boundary paper and keep the fast bootstrap as supporting inference code + artifact.
   - *User input needed only if:* You explicitly want to abandon or sideline the RAG retrieval study to pursue a standalone generic bootstrap software paper instead (reopens **Decision 1: Topic** and **Decision 5: Product/MVP**).
2. **Target Venue, Year/Track, and Goal Mode Binding (Before M4/M5 packaging):**
   - Which target venue/track (e.g., ACL, EMNLP, NAACL, NeurIPS, ICLR) should govern page limits, formatting, anonymity, and reproduction-package requirements?
   - Should this thread bind a native full-paper Codex Goal (`create_goal`) once in a live run, or remain a stage-managed project via handoff records? (Research and M3 analysis proceed without waiting for this.)
3. **External Artifact Paths (Only if not already present in the workspace):**
   - If the matched-capacity retrieval run logs, R0/R1/R2 repositories, or category-theory draft reside outside the current workspace root, provide their local paths.

## 5. Shared Round Package (`R3`)

| Part | Record for Round `R3` |
| --- | --- |
| **Question / Evidence** | **Round ID:** `R3`. **Gap:** `R0` has subspace geometry on sentence pairs without retrieval outcomes; `R1`/`R2` provide source-group bootstrap code but proposed an off-theme software pivot; matched-capacity retrieval evidence on role/negation loss exists as a candidate direction; category-theory lemma is unconnected to retrieval predictions. **Competing explanations:** (H1) Geometric paraphrase-invariance subspaces intrinsically collapse non-commutative role/negation signals under fixed capacity/token budgets; (H2) Apparent role/negation retrieval loss is an artifact of unmatched capacity/token tokenization or within-source correlation. |
| **Action / Rationale** | **Stage:** `research-analyze` -> `research-design` (mechanism link) -> `research-write` (M3-gated). **Work:** (1) Reconcile matched-capacity retrieval run records and verify equal capacity/token controls; (2) Run R1/R2 source-group bootstrap on retrieval metrics (benign paraphrase recall/nDCG vs. role-swap and negation contrast sets); (3) Map R0 subspace projection coordinates to retrieval errors; (4) Park the unconnected category-theory lemma. **Minimal discriminating check:** Compare source-group-bootstrapped retrieval accuracy on benign paraphrases vs. role/negation edits across matched-capacity subspace ranks. |
| **Resources / Authority** | **Cost:** `0` new spend (`free_only: true`, local CPU/existing artifacts only). **Allowance:** Strict zero-new-spend rule per user instruction. **Authority:** Covered by user delegation for autonomous changes within the semantic RAG paraphrase/retrieval theme. |
| **Decision / Stop** | **If supported** (role/negation loss persists under verified equal capacity/tokens with narrow grouped-bootstrap CIs): consolidate at M3 as the core negative/boundary contribution and route to `research-write`. **If refuted** (discrepancy disappears once capacity/token budgets are properly matched): report the baseline/protocol correction as the finding and re-evaluate which paraphrase changes remain invariant. **If inconclusive** (wide bootstrap CIs or missing retrieval splits): run one bounded local zero-cost evaluation pass on existing embeddings or close with explicit limitation. **Stop condition:** Do not run paid API/GPU jobs or open-ended feature searches. |
| **Actual Outcome** | **Execution status:** `proposed / unexecuted` (this turn is a bounded synthetic routing and contribution-audit exercise with no network, model calls, or project writes). |

## 6. Five-Part Handoff and Resumption Record

1. **Artifacts:**
   - Handoff and round specification: `<workspace>/.build/research-focus-20261025/baseline-behavior.md` (revision `R3-plan-v1`).
   - Upstream project state referenced (unmodified): `R0` (sentence-pair subspace pilot), `R1` (source-group bootstrap pilot), `R2` (polished bootstrap code + invalidated software-paper handoff), candidate matched-capacity retrieval records, and unconnected category-theory lemma draft.
2. **Evidence:**
   - Inspected workflow rules in `<workspace>/.build/research-focus-20261025/before-source/research-navigate/SKILL.md`, `references/workflow-contract.md`, `references/stage-map.md`, `references/model-routing.md`, `references/reuse-and-simplification.md`, `references/decision-support.md`, `references/goal-execution.md`, and `research-analyze/SKILL.md` + `references/contribution-audit.md`.
   - Scenario state evaluated directly from supplied project history; no experimental metrics or source checks were fabricated.
3. **Status:**
   - **Navigation & contribution-audit routing:** `completed`.
   - **Round `R3` empirical audit & bootstrap-retrieval integration:** `proposed / unexecuted` (ready for immediate execution by next agent).
   - **Paper status:** `incomplete` (at `M1/M2 -> M3` transition: reconciling matched-capacity retrieval evidence and principal conclusions for M3).
   - **Action authorization:** In-theme RAG boundary paper is **authorized** under existing user delegation; R2 generic software pivot is **unauthorized** without an explicit Topic decision override.
4. **Open Issues:**
   - Raw run manifest and exact capacity/token parity checks for the matched-capacity retrieval candidate must be verified from project files in `research-analyze`.
   - Category-theory lemma lacks a bridge to retrieval predictions and is quarantined from the critical path.
   - Target venue profile is unset (needed before M4/M5 blind venue reviews, non-blocking for M3).
5. **Next Step:**
   - **Stage:** `research-analyze` (primary) with conditional mechanism link in `research-design`.
   - **Concrete work package (`R3-WP1`):** Audit the matched-capacity retrieval runs for equal capacity/token budget compliance, apply the R1/R2 source-group bootstrap to compute grouped uncertainty over benign-paraphrase vs. role/negation retrieval outcomes, link R0 subspace projection metrics to the failure boundary, and assemble the Claim-Evidence Map for Milestone **M3**.

### Dispatch and Model-Routing Record (`free_only: true`, Zero New Spend)

| Branch / Role | Stage | Requested Model & Effort | Actual Served | Free / Quota Pool | Write Scope & Status |
| --- | --- | --- | --- | --- | --- |
| Primary statistical & contribution analysis (`R3-WP1a`) | `research-analyze` | `workbuddy-ai/deepseek-v4.1-flash` (`max`) | `unexecuted` | Free (`workbuddy-ai`, max 2 concurrent) | `analysis/r3_retrieval_bootstrap/`; ready to dispatch (check channel data policy before sending unpublished text) |
| Contribution & reuse audit synthesis (`R3-WP1b`) | `research-analyze` | `workbuddy-ai/step-5-preview` (`high`) | `unexecuted` | Free (`workbuddy-ai`) | `analysis/r3_contribution_map/`; ready to dispatch |
| Bootstrap-to-retrieval evaluation wiring (`R3-WP1c`, if glue script needed) | `research-implement` / `research-analyze` | `opencode-zen/glm-5.3-flash-free` (`max`) | `unexecuted` | Free (`opencode-zen`; verify trial data policy) | `src/eval_retrieval_bootstrap/`; conditional on missing glue script |
| Finite-dimensional subspace/capacity math check (`R3-WP2`) | `research-design` | `opencode-zen/beam-free` (`max`) | `unexecuted` | Free (`opencode-zen`) | `theory/subspace_role_bound/`; checks linear/subspace collapse vs. parked category lemma |
| Covered Cursor branch | `research-analyze` | `cursor/grok-4.6` (`medium`, Fast off) | `skipped / unexecuted` | Shared Cursor subscription pool | Skipped: live subscription window/coverage unverified in this synthetic exercise and no new spending is permitted |
| Paid Codex / Vertex escalations (`gpt-6-astra`, `gpt-6.1-sol`, `gemini-4-argon`) | Integration / M3 Review | Not requested (`free_only: true`) | `unexecuted` | Paid pools blocked by `no new spending` unless pre-covered zero-marginal-cost quota is verified | Use cross-family free reviewer (`workbuddy-ai/step-5-preview` vs. `workbuddy-ai/deepseek-v4.1-flash` / `opencode-zen/space-bunny-free`) at M3 and explicitly record free-tier review limitations |
| Advisory structured decision (`jev_decide.py`) | `research-navigate` | `typesafe/jev-latest` | `unexecuted` | Paid/account-covered (`unknown` coverage -> no call) | Not called: local synthetic constraint + unknown credit coverage + hard scope constraint already eliminates R2 off-theme pivot |

### Compact Resumption & Optimizer Queue Snapshot

- `round`: `R3`; `milestone`: `M2 -> M3` (principal conclusions gate pending `R3-WP1` execution).
- `valid_coverage`: `R0` sentence-pair geometry scripts (valid as mechanism probe only); `R1/R2` source-group bootstrap implementation (valid as reusable inference tool).
- `stale_or_invalidated`: `R0` pair-only conclusions (insufficient as standalone RAG claims); `R2` generic software-paper framing (invalidated as out-of-scope topic exit); `category-theory lemma` (quarantined, `unresolved` relevance).
- `stage_status`: `research-navigate` routing complete; `research-analyze` `R3-WP1` `ready` (`unexecuted` in synthetic exercise).
- `paper_status`: `incomplete`; native Goal binding `not_bound` (no Goal tool call permitted in this synthetic exercise).
- `optimizer_event`: Queued one idempotent stage event for `research-navigate` (`R2->R3` redirection: retained R1/R2 bootstrap asset and matched-capacity retrieval candidate; identified weakness where R2 handoff drifted outside authorized research theme toward an "easy" software pivot; cost: 0 external calls).
