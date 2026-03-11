"""
Sample briefing data for demo mode.

Contains realistic sample data for a fictional account "Acme Analytics"
(a PostHog customer) to demonstrate the full pipeline without any
external integrations configured.
"""
from datetime import datetime, timezone


SAMPLE_BRIEFING_REQUEST = {
    "account": "Acme Analytics",
    "topic": "Q3 renewal discussion",
    "attendees": [
        "Sarah Chen (VP Engineering)",
        "Mike Torres (Account Owner)",
    ],
}


SAMPLE_DECOMPOSED_QUERIES = [
    {
        "query": "Acme Analytics account overview health score ARR",
        "source_name": "notion",
        "rationale": "Pull the CRM account page for current health, ARR, plan tier, and CSM details",
    },
    {
        "query": "Acme Analytics meeting notes conversations",
        "source_name": "notion",
        "rationale": "Find recent meeting notes and past conversation history with the account",
    },
    {
        "query": "Acme Analytics account plan renewal timeline expansion",
        "source_name": "google_drive",
        "rationale": "Locate the account plan document with renewal dates and expansion opportunities",
    },
    {
        "query": "Acme Analytics product feedback feature requests",
        "source_name": "google_drive",
        "rationale": "Find any product briefs or feedback documents related to this account",
    },
    {
        "query": "session replay SDK bundle size performance",
        "source_name": "github",
        "rationale": "Check for recent engineering work on session replay, a key feature for Acme",
    },
    {
        "query": "Acme Analytics integration issues bug reports",
        "source_name": "github",
        "rationale": "Look for any open issues or recent bug reports that involve this account",
    },
]


SAMPLE_SEARCH_RESULTS = [
    # Notion: CRM account page
    {
        "query": "Acme Analytics account overview health score ARR",
        "source_name": "notion",
        "title": "Acme Analytics - Account Overview",
        "content": (
            "**Account:** Acme Analytics\n"
            "**Plan:** Enterprise (annual)\n"
            "**ARR:** $187,000\n"
            "**Health Score:** 82/100 (Good)\n"
            "**CSM:** Rachel Kim\n"
            "**Contract End:** September 30, 2025\n"
            "**Seats:** 47 licensed, 39 active\n"
            "**Key Contacts:** Sarah Chen (VP Eng, champion), David Park (CTO, exec sponsor)\n\n"
            "**Usage Highlights:**\n"
            "- Session replay: 2.3M sessions/month (up 40% QoQ)\n"
            "- Feature flags: 156 active flags across 3 environments\n"
            "- Funnels: 28 active funnels, most used by product team\n\n"
            "**Notes:** Strong product-led adoption. Engineering team expanding. "
            "Sarah has been vocal about session replay performance and SDK bundle size."
        ),
        "url": "https://notion.so/acme-analytics-account-abc123",
        "score": 0.96,
    },
    # Notion: Meeting notes
    {
        "query": "Acme Analytics meeting notes conversations",
        "source_name": "notion",
        "title": "Acme Analytics - QBR Notes (June 12)",
        "content": (
            "**Attendees:** Sarah Chen, Rachel Kim, Mike Torres\n\n"
            "**Key Discussion Points:**\n"
            "1. Session replay SDK bundle size is a concern. Sarah mentioned it adds ~180KB "
            "to their production bundle. Would like to see it under 100KB.\n"
            "2. Very happy with feature flags. Rolled out to all 3 engineering teams.\n"
            "3. Asked about self-serve data warehouse export. Currently using the API "
            "but want a native connector.\n"
            "4. Renewal conversation starting soon. Sarah hinted at potentially upgrading "
            "to include the data pipeline add-on.\n\n"
            "**Action Items:**\n"
            "- [Rachel] Share session replay SDK roadmap with Sarah\n"
            "- [Mike] Prepare renewal proposal with data pipeline pricing\n"
            "- [Sarah] Send list of top 5 feature requests from her team"
        ),
        "url": "https://notion.so/acme-qbr-june-def456",
        "score": 0.93,
    },
    {
        "query": "Acme Analytics meeting notes conversations",
        "source_name": "notion",
        "title": "Acme Analytics - Support Escalation (May 28)",
        "content": (
            "**Context:** Sarah Chen raised a P1 about session replay dropping frames "
            "on their checkout flow pages. Issue was traced to a conflict with their "
            "Stripe Elements integration.\n\n"
            "**Resolution:** Engineering shipped a patch (v2.14.3) within 48 hours. "
            "Sarah was appreciative of the fast turnaround. She specifically thanked "
            "the engineering team in a follow-up email.\n\n"
            "**Takeaway:** Good recovery. The fast response strengthened the relationship. "
            "However, Sarah noted this is the second session replay issue in 3 months."
        ),
        "url": "https://notion.so/acme-escalation-may-ghi789",
        "score": 0.88,
    },
    # Google Drive: Account plan
    {
        "query": "Acme Analytics account plan renewal timeline expansion",
        "source_name": "google_drive",
        "title": "Acme Analytics - FY25 Account Plan",
        "content": (
            "**Renewal Date:** September 30, 2025\n"
            "**Current ARR:** $187,000\n"
            "**Target Renewal ARR:** $220,000 (+18%)\n\n"
            "**Expansion Opportunities:**\n"
            "1. Data Pipeline add-on ($28,000/yr) - Sarah expressed interest at QBR\n"
            "2. Additional seats (8 new engineers joining in Q3) - ~$5,000/yr\n\n"
            "**Risks:**\n"
            "- Session replay performance concerns (SDK bundle size)\n"
            "- Competitor evaluation: Sarah mentioned Amplitude is pitching them\n\n"
            "**Strategy:**\n"
            "- Lead with the session replay improvements shipping in v3.0\n"
            "- Offer early access to data pipeline for a 2-year commitment\n"
            "- Highlight ROI: their support ticket volume dropped 35% after adopting feature flags"
        ),
        "url": "https://docs.google.com/document/d/acme-account-plan-2025",
        "score": 0.94,
    },
    # Google Drive: Product brief
    {
        "query": "Acme Analytics product feedback feature requests",
        "source_name": "google_drive",
        "title": "Product Brief: Session Replay v3.0",
        "content": (
            "**Release Target:** August 2025\n\n"
            "**Key Improvements:**\n"
            "- SDK bundle size reduced from 180KB to 62KB (tree-shakeable modules)\n"
            "- New privacy controls: automatic PII masking with ML-based detection\n"
            "- Performance: 40% reduction in CPU overhead during recording\n"
            "- Network replay: full XHR/fetch request visualization\n\n"
            "**Customer Requests Addressed:**\n"
            "- Acme Analytics: bundle size reduction (primary driver)\n"
            "- TechCorp: PII masking for HIPAA compliance\n"
            "- DataFlow Inc: network request visibility\n\n"
            "**Competitive Positioning:**\n"
            "Smallest SDK in the market (Amplitude: 95KB, Hotjar: 112KB, ours: 62KB)"
        ),
        "url": "https://docs.google.com/document/d/session-replay-v3-brief",
        "score": 0.91,
    },
    # GitHub: SDK optimization PR
    {
        "query": "session replay SDK bundle size performance",
        "source_name": "github",
        "title": "PR #4821: Reduce session replay SDK bundle size by 65%",
        "content": (
            "## Summary\n"
            "Refactored the session replay SDK to use tree-shakeable ES modules. "
            "Customers can now import only the recording features they need.\n\n"
            "## Changes\n"
            "- Split monolithic SDK into 6 sub-modules (core, network, console, dom, "
            "performance, privacy)\n"
            "- Core module: 42KB (down from 180KB for full bundle)\n"
            "- Full bundle with all modules: 62KB (tree-shaking removes unused code)\n"
            "- Added lazy loading for network and console recorders\n\n"
            "## Performance\n"
            "- 40% reduction in main thread CPU usage during recording\n"
            "- 55% faster initialization time\n"
            "- Memory usage down from 12MB to 7MB average\n\n"
            "**Status:** Merged to main, shipping in v3.0"
        ),
        "url": "https://github.com/posthog/posthog/pull/4821",
        "score": 0.95,
    },
    # GitHub: Bug report
    {
        "query": "Acme Analytics integration issues bug reports",
        "source_name": "github",
        "title": "Issue #4987: Session replay conflicts with Stripe Elements iframes",
        "content": (
            "**Reported by:** Acme Analytics (via support)\n\n"
            "**Description:** Session replay drops frames and causes visual glitches "
            "when Stripe Elements payment forms are present on the page. The iframe "
            "mutation observer conflicts with Stripe's own DOM manipulation.\n\n"
            "**Root Cause:** Our MutationObserver was trying to serialize cross-origin "
            "iframe content, causing SecurityError exceptions that interrupted recording.\n\n"
            "**Fix:** Added cross-origin iframe detection and graceful fallback to "
            "placeholder rendering. Shipped in v2.14.3.\n\n"
            "**Status:** Closed (fixed)"
        ),
        "url": "https://github.com/posthog/posthog/issues/4987",
        "score": 0.87,
    },
    {
        "query": "Acme Analytics integration issues bug reports",
        "source_name": "github",
        "title": "Issue #5102: Feature flag evaluation latency spikes on large rule sets",
        "content": (
            "**Description:** Customers with 100+ feature flags experience occasional "
            "latency spikes (>500ms) during flag evaluation. Affects SDK initialization.\n\n"
            "**Investigation:** The flag rule engine evaluates all flags sequentially. "
            "For large rule sets with complex targeting, this becomes a bottleneck.\n\n"
            "**Proposed Fix:** Implement parallel evaluation and caching of recently "
            "evaluated flags. Expected to reduce p99 latency from 500ms to <50ms.\n\n"
            "**Status:** Open, assigned to SDK team for v3.1"
        ),
        "url": "https://github.com/posthog/posthog/issues/5102",
        "score": 0.79,
    },
]


SAMPLE_BRIEF_MARKDOWN = """# Pre-Meeting Brief: Acme Analytics

**Meeting Topic:** Q3 renewal discussion
**Generated:** {generated_at}

---

## Account Snapshot

| Field | Details |
|-------|---------|
| **Plan** | Enterprise (annual) |
| **ARR** | $187,000 |
| **Health Score** | 82/100 (Good) |
| **Contract End** | September 30, 2025 |
| **CSM** | Rachel Kim |
| **Seats** | 47 licensed, 39 active |
| **Key Champion** | Sarah Chen (VP Engineering) |

**Usage:** Session replay at 2.3M sessions/month (up 40% QoQ). 156 active feature flags. 28 active funnels used by the product team.

## Relationship History

- **June 12 QBR:** Sarah raised SDK bundle size concerns (180KB, wants under 100KB). Interested in data pipeline add-on. Positive on feature flags.
- **May 28 Escalation:** P1 session replay issue with Stripe Elements. Patched within 48 hours (v2.14.3). Sarah appreciated the fast response, but noted it was the second replay issue in 3 months.
- **Overall sentiment:** Strong product-led adoption. Engineering team is expanding. Sarah is an active champion but holds us to high standards on reliability.

## Open Concerns to Address

1. **Session replay SDK bundle size** (180KB) has been a recurring concern. Sarah specifically asked for it to be under 100KB.
2. **Reliability track record:** Two session replay issues in the last 3 months. Sarah values fast response but wants fewer incidents.
3. **Competitive pressure:** Amplitude is actively pitching Acme. Need to reinforce differentiation.

## Relevant Product Updates

- **Session Replay v3.0** (shipping August 2025): SDK reduced from 180KB to 62KB with tree-shakeable modules. This directly addresses Sarah's top concern. Our 62KB bundle is the smallest in the market (Amplitude: 95KB, Hotjar: 112KB).
- **PR #4821 merged:** 65% bundle size reduction, 40% less CPU usage, 55% faster init.
- **Stripe iframe bug (Issue #4987):** Fixed in v2.14.3. Cross-origin iframe detection added.
- **Feature flag latency (Issue #5102):** Open issue for large rule sets. Fix planned for v3.1.

## Suggested Talking Points

1. **Lead with the v3.0 SDK improvements.** The 62KB bundle size directly solves Sarah's top concern and beats every competitor. Share the PR and benchmark data.
2. **Acknowledge the reliability concerns.** Reference the fast Stripe fix turnaround and explain the architectural improvements in v3.0 that prevent similar issues.
3. **Propose the renewal with data pipeline add-on.** Target: $220K ARR (+18%). Offer early access to data pipeline in exchange for a 2-year commitment.
4. **Counter the Amplitude pitch.** Highlight: smallest SDK, self-hostable, open-source core, and their existing 35% reduction in support tickets from feature flags.
5. **Mention the 8 new engineering hires.** Opportunity for seat expansion (~$5K/yr). Offer onboarding support for the new team members.
"""


SAMPLE_BRIEF_SECTIONS = [
    {
        "heading": "Account Snapshot",
        "content": (
            "| Field | Details |\n"
            "|-------|--------|\n"
            "| **Plan** | Enterprise (annual) |\n"
            "| **ARR** | $187,000 |\n"
            "| **Health Score** | 82/100 (Good) |\n"
            "| **Contract End** | September 30, 2025 |\n"
            "| **CSM** | Rachel Kim |\n"
            "| **Seats** | 47 licensed, 39 active |\n"
            "| **Key Champion** | Sarah Chen (VP Engineering) |\n\n"
            "**Usage:** Session replay at 2.3M sessions/month (up 40% QoQ). "
            "156 active feature flags. 28 active funnels used by the product team."
        ),
    },
    {
        "heading": "Relationship History",
        "content": (
            "- **June 12 QBR:** Sarah raised SDK bundle size concerns (180KB, wants "
            "under 100KB). Interested in data pipeline add-on. Positive on feature flags.\n"
            "- **May 28 Escalation:** P1 session replay issue with Stripe Elements. "
            "Patched within 48 hours (v2.14.3). Sarah appreciated the fast response, "
            "but noted it was the second replay issue in 3 months.\n"
            "- **Overall sentiment:** Strong product-led adoption. Engineering team "
            "is expanding. Sarah is an active champion but holds us to high standards "
            "on reliability."
        ),
    },
    {
        "heading": "Open Concerns to Address",
        "content": (
            "1. **Session replay SDK bundle size** (180KB) has been a recurring concern. "
            "Sarah specifically asked for it to be under 100KB.\n"
            "2. **Reliability track record:** Two session replay issues in the last 3 months. "
            "Sarah values fast response but wants fewer incidents.\n"
            "3. **Competitive pressure:** Amplitude is actively pitching Acme. "
            "Need to reinforce differentiation."
        ),
    },
    {
        "heading": "Relevant Product Updates",
        "content": (
            "- **Session Replay v3.0** (shipping August 2025): SDK reduced from 180KB "
            "to 62KB with tree-shakeable modules. This directly addresses Sarah's top "
            "concern. Our 62KB bundle is the smallest in the market (Amplitude: 95KB, "
            "Hotjar: 112KB).\n"
            "- **PR #4821 merged:** 65% bundle size reduction, 40% less CPU usage, "
            "55% faster init.\n"
            "- **Stripe iframe bug (Issue #4987):** Fixed in v2.14.3. Cross-origin "
            "iframe detection added.\n"
            "- **Feature flag latency (Issue #5102):** Open issue for large rule sets. "
            "Fix planned for v3.1."
        ),
    },
    {
        "heading": "Suggested Talking Points",
        "content": (
            "1. **Lead with the v3.0 SDK improvements.** The 62KB bundle size directly "
            "solves Sarah's top concern and beats every competitor. Share the PR and "
            "benchmark data.\n"
            "2. **Acknowledge the reliability concerns.** Reference the fast Stripe fix "
            "turnaround and explain the architectural improvements in v3.0 that prevent "
            "similar issues.\n"
            "3. **Propose the renewal with data pipeline add-on.** Target: $220K ARR "
            "(+18%). Offer early access to data pipeline in exchange for a 2-year "
            "commitment.\n"
            "4. **Counter the Amplitude pitch.** Highlight: smallest SDK, self-hostable, "
            "open-source core, and their existing 35% reduction in support tickets "
            "from feature flags.\n"
            "5. **Mention the 8 new engineering hires.** Opportunity for seat expansion "
            "(~$5K/yr). Offer onboarding support for the new team members."
        ),
    },
]


def get_sample_briefing_request() -> dict:
    """Return the sample briefing request."""
    return SAMPLE_BRIEFING_REQUEST.copy()


def get_sample_decomposed_queries() -> list:
    """Return the sample decomposed queries."""
    return [q.copy() for q in SAMPLE_DECOMPOSED_QUERIES]


def get_sample_search_results() -> list:
    """Return the sample search results."""
    return [r.copy() for r in SAMPLE_SEARCH_RESULTS]


def get_sample_brief() -> dict:
    """Return the sample brief with current timestamp."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return {
        "account": "Acme Analytics",
        "topic": "Q3 renewal discussion",
        "generated_at": now,
        "sections": [s.copy() for s in SAMPLE_BRIEF_SECTIONS],
        "markdown": SAMPLE_BRIEF_MARKDOWN.format(generated_at=now),
    }
