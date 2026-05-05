"""
Test data: 2 clients, 3 meeting transcripts each, 1 email reply each.
"""

TEST_CLIENTS = {
    "finova": {
        "client_id": "finova",
        "client_name": "Sarah Chen",
        "company_name": "FinoVa Capital",
        "industry": "Fintech / Investment Management",
        "attendees": ["Sarah Chen (CFO)", "James Liu (CTO)", "Priya Kapoor (Head of Product)"],
        "augusta_team": ["Marcus Reid (Engagement Lead)", "Aisha Okonkwo (Data Architect)", "Tom Bauer (ML Engineer)"],
        "project_status": "discovery",
    },
    "medbridge": {
        "client_id": "medbridge",
        "client_name": "Dr. Robert Hargrove",
        "company_name": "MedBridge Health",
        "industry": "Healthcare / Digital Health",
        "attendees": ["Dr. Robert Hargrove (CEO)", "Nina Patel (VP Engineering)", "Carlos Vega (Head of Compliance)"],
        "augusta_team": ["Diana Park (Engagement Lead)", "Liam Chen (Solutions Architect)", "Fatima Al-Rashid (QA Lead)"],
        "project_status": "discovery",
    },
}

TRANSCRIPTS = {
    "finova": [
        {
            "id": "finova_t1",
            "title": "FinoVa – Kickoff Call",
            "date": "2025-04-01",
            "content": """
Meeting: FinoVa Capital – Project Kickoff
Date: April 1, 2025
Attendees: Sarah Chen (CFO), James Liu (CTO), Priya Kapoor (Head of Product) | Marcus Reid (Augusta), Aisha Okonkwo (Augusta)

Sarah Chen: Thanks for joining us today. We've been struggling with our data pipeline for about six months now. Our portfolio analytics are running 18 hours behind real-time, which is completely unacceptable when markets are moving fast.

Marcus Reid: Understood, Sarah. Can you walk us through the current architecture?

James Liu: Sure. We're on AWS, pulling data from 12 different broker APIs, then it goes into a Redshift cluster. The transformation layer is a mix of old Airflow DAGs and some Python scripts that, honestly, nobody fully understands anymore.

Aisha Okonkwo: What's the data volume we're talking about?

James Liu: About 2TB of raw trade data per day, plus another 500GB of market data feeds.

Priya Kapoor: The product side is getting really frustrated. We promised our portfolio managers a real-time dashboard by Q3, and we're nowhere close. Our biggest client — Meridian Fund — is threatening to pull $300M if we don't fix this.

Marcus Reid: That's a clear north star. Real-time analytics by Q3. Aisha, what's your initial read?

Aisha Okonkwo: We'd want to look at replacing the batch pipeline with a streaming architecture — probably Kafka plus something like Apache Flink or Spark Streaming. But we need to audit the existing DAGs first.

Sarah Chen: What would that cost us roughly?

Marcus Reid: We'll put together a formal proposal, but ballpark we're looking at a 10-12 week engagement, likely in the $280k-$320k range depending on complexity.

James Liu: That's within our budget if you can guarantee the Q3 timeline.

Marcus Reid: We'll commit to a detailed timeline in the proposal. James, can you get Aisha access to the dev Redshift cluster this week so she can run a data audit?

James Liu: Yes, I'll have credentials to you by Thursday.

Priya Kapoor: One more thing — we need this to be compatible with our existing Tableau dashboards. We can't re-train 40 portfolio managers.

Aisha Okonkwo: Noted. We'll ensure backward compatibility with Tableau.

Marcus Reid: Great. Let me summarize next steps: Aisha gets dev cluster access by Thursday, we deliver a formal proposal by next Friday, and we schedule a technical deep-dive for next Wednesday at 2pm. Does that work?

Sarah Chen: Works for me.
James Liu: Same.

Marcus Reid: Perfect. We'll get moving.
""",
        },
        {
            "id": "finova_t2",
            "title": "FinoVa – Technical Deep-Dive",
            "date": "2025-04-09",
            "content": """
Meeting: FinoVa Capital – Technical Deep-Dive & Architecture Review
Date: April 9, 2025
Attendees: James Liu (CTO), Aisha Okonkwo (Augusta), Tom Bauer (Augusta)

James Liu: Aisha, you've had a week with the cluster. What did you find?

Aisha Okonkwo: Honestly, it's worse than we expected but fixable. We found 47 Airflow DAGs, of which 19 are actively used, 8 are broken and running anyway — silently failing — and the rest are orphaned. The main bottleneck is a transformation job that's doing a full table scan on a 400GB table every 4 hours.

James Liu: I had a feeling. That job was written by a contractor who left in 2022.

Tom Bauer: On the ML side, I see you're also trying to run some risk scoring models in the pipeline?

James Liu: Yeah, that was a mistake. Someone bolted on a TensorFlow model directly into an Airflow DAG. It's killing performance.

Tom Bauer: We'd want to pull those out into a separate model serving layer — probably SageMaker endpoints — and call them asynchronously.

Aisha Okonkwo: Here's the proposed architecture: Replace Airflow with Kafka for streaming ingestion, use dbt for transformations running on Snowflake instead of Redshift, and serve to Tableau via a semantic layer. The risk models go to SageMaker.

James Liu: Why Snowflake over Redshift?

Aisha Okonkwo: Three reasons: better streaming ingestion support, automatic scaling, and your team will find it easier to maintain. Migration from Redshift to Snowflake is also well-documented.

James Liu: Cost comparison?

Aisha Okonkwo: We're estimating roughly 30% cost reduction in compute, though storage will be slightly higher. Net-net probably neutral to 10% savings.

James Liu: That's actually good news for Sarah. She's been pushing us to cut infrastructure costs.

Tom Bauer: We'd also recommend a data quality layer — Great Expectations integrated into the dbt pipeline. You're currently flying blind on data quality.

James Liu: Agreed. The bad data issue cost us 3 hours of analyst time last month chasing a phantom trade discrepancy.

Aisha Okonkwo: Revised timeline: 2 weeks discovery and migration planning, 4 weeks Kafka + Snowflake build, 3 weeks dbt transformation layer, 2 weeks ML model migration, 1 week UAT and go-live. Total: 12 weeks, targeting July 25th go-live — comfortably before Q3 end.

James Liu: Can we run parallel for 2 weeks before cutover? I don't want a hard cutover.

Aisha Okonkwo: Absolutely. We'll build a shadow mode into the plan.

Tom Bauer: One action item for you, James — we need the API specs for all 12 broker integrations. Some of them look non-standard.

James Liu: I'll get those to you by end of week. Fair warning, two of them are undocumented legacy APIs.

Aisha Okonkwo: That's common. We'll reverse-engineer if needed.

James Liu: Alright. I'm feeling good about this. When does Augusta need final sign-off on the proposal to hit the July 25th date?

Aisha Okonkwo: Ideally by April 16th so we can start discovery week April 21st.

James Liu: I'll push Sarah to sign by then.
""",
        },
        {
            "id": "finova_t3",
            "title": "FinoVa – Proposal Review & SOW Negotiation",
            "date": "2025-04-16",
            "content": """
Meeting: FinoVa Capital – Proposal Review & Statement of Work Discussion
Date: April 16, 2025
Attendees: Sarah Chen (CFO), James Liu (CTO), Priya Kapoor (Head of Product) | Marcus Reid (Augusta), Aisha Okonkwo (Augusta), Tom Bauer (Augusta)

Marcus Reid: Thank you all for reviewing the proposal. Sarah, I know you had some questions — let's work through them.

Sarah Chen: Yes. The $315k number — I've had our procurement team look at it and they're pushing back. They want to see it closer to $275k. Also, the payment schedule — 50% upfront is a non-starter for us.

Marcus Reid: I appreciate the transparency. On price: the $315k reflects 12 weeks at our standard rates. We can get to $290k if we reduce the ML model migration scope slightly — specifically, we'd migrate 2 of the 4 risk models in scope, and the other 2 would be Phase 2.

Sarah Chen: Which two models stay in Phase 1?

Tom Bauer: The intraday liquidity risk model and the portfolio concentration model — those are the ones tied to the Meridian Fund reporting. The credit default model and the macro factor model can move to Phase 2 without impacting Q3 commitments.

Priya Kapoor: That works for us. The Meridian reporting is the critical path.

Sarah Chen: Ok, $290k I can work with. On payment — we'd prefer 30% upfront, 40% at midpoint milestone, 30% at delivery.

Marcus Reid: We can do 35/35/30. The 35% upfront covers our initial staffing commitment.

Sarah Chen: Let me check with our CFO counterpart... actually, I have authority up to $300k and payment terms are flexible. 35/35/30 is fine.

Marcus Reid: Great. Then we have a deal in principle.

James Liu: One thing I want documented in the SOW: the parallel run commitment. Two weeks of shadow mode before hard cutover, with a rollback plan.

Aisha Okonkwo: Already in the proposal, section 4.2. We'll also include explicit rollback procedures.

Priya Kapoor: I want to add a success metric to the SOW: portfolio analytics latency must be under 5 minutes end-to-end by go-live.

Aisha Okonkwo: We're targeting sub-2-minute latency based on the architecture, so 5 minutes is very achievable. We'll add it as a formal success criterion.

Sarah Chen: One more thing. Our legal team will need to review the data processing agreement — we deal with PII from fund investors.

Marcus Reid: Of course. We'll send our standard DPA alongside the SOW. Aisha, flag any data handling specifics for legal.

Sarah Chen: Timeline to execute?

Marcus Reid: If we get a redline SOW back by Thursday April 18th, we can countersign by Friday April 19th and kick off discovery Monday April 21st.

Sarah Chen: I'll make sure legal prioritizes it. James, can you own the SOW coordination on your end?

James Liu: On it.

Marcus Reid: Excellent. I'm excited about this partnership. FinoVa has a real opportunity to be a technology leader in the mid-market fund space.

Sarah Chen: That's the goal. Let's make it happen.
""",
        },
    ],
    "medbridge": [
        {
            "id": "medbridge_t1",
            "title": "MedBridge – Discovery Call",
            "date": "2025-04-03",
            "content": """
Meeting: MedBridge Health – Initial Discovery Call
Date: April 3, 2025
Attendees: Dr. Robert Hargrove (CEO), Nina Patel (VP Engineering) | Diana Park (Augusta), Liam Chen (Augusta)

Dr. Hargrove: Thanks for taking the time. We're at an inflection point. We have 2.3 million patient records across 47 clinic partners, and we're trying to build a predictive care platform — specifically, identify patients at risk of preventable readmissions.

Diana Park: That's a compelling problem. What's the current state of your data infrastructure?

Nina Patel: It's a mess, honestly. We have data coming in from 47 different EMR systems — Epic, Cerner, eClinicalWorks, and about 10 others. They're all in different formats. We built a basic ETL pipeline about 18 months ago but it breaks every time a clinic partner upgrades their EMR.

Liam Chen: What's the target state? Build your own models, or leverage existing clinical AI solutions?

Dr. Hargrove: Build our own. We have proprietary outcome data that would give us a competitive edge if we can use it properly. Our hypothesis is that 40% of 30-day readmissions are predictable 7 days before discharge.

Diana Park: What's the regulatory context? I'm assuming you're dealing with HIPAA at minimum.

Carlos Vega (joining late): Sorry I'm late — I'm Carlos, Head of Compliance. Yes, HIPAA is table stakes. We also have two clinic partners who are part of the CMS Innovation Center pilot, so we have additional reporting requirements there.

Liam Chen: Any existing ML infrastructure?

Nina Patel: We have a small data science team — 2 people — who have been experimenting with scikit-learn models on a subset of data. But they're blocked because they can't access production data due to compliance restrictions.

Carlos Vega: That's the core tension. Clinical data, even de-identified, requires a formal data access framework. Right now we have nothing.

Diana Park: So the work is really two-layered: first build a compliant data infrastructure, then build the predictive models on top of it.

Dr. Hargrove: Exactly. And we need to move fast. We have a grant renewal in September — we need to show measurable progress on the predictive capability by August 31st.

Diana Park: That's ambitious but doable. Liam, what's your initial architecture thought?

Liam Chen: I'd think about this as three phases: Phase 1 — federated data ingestion with HL7 FHIR normalization, Phase 2 — a secure, HIPAA-compliant analytical environment (probably Databricks on Azure with PHI controls), Phase 3 — model development and validation. 

Dr. Hargrove: How long?

Liam Chen: Rough estimate: 16-18 weeks for a production-ready system. But you could have a working prototype by week 10.

Diana Park: We'll come back with a formal proposal. One immediate question: do your clinic partners all support FHIR R4, or are some on older standards?

Nina Patel: About 70% support FHIR R4. The rest are mostly HL7 v2 via APIs or raw file exports.

Liam Chen: That's workable. Action item for Augusta: we'll map all 47 integrations and propose a normalized ingestion strategy.

Dr. Hargrove: One constraint I should mention: budget. We have $400k earmarked for this initiative from our Series B. But if you can get us to the August demo, the Board has agreed to release another $200k for Phase 2.

Diana Park: Understood. We'll scope Phase 1 to fit the initial budget.
""",
        },
        {
            "id": "medbridge_t2",
            "title": "MedBridge – Architecture & Compliance Workshop",
            "date": "2025-04-11",
            "content": """
Meeting: MedBridge Health – Architecture & Compliance Workshop
Date: April 11, 2025  
Attendees: Nina Patel (VP Engineering), Carlos Vega (Head of Compliance) | Diana Park (Augusta), Liam Chen (Augusta), Fatima Al-Rashid (Augusta)

Diana Park: We've done our homework this week. Liam and Fatima, let's walk through what we found.

Liam Chen: We mapped all 47 clinic integrations. Here's the breakdown: 31 support FHIR R4 natively, 9 are HL7 v2.x, 4 provide CSV/file drops via SFTP, and 3 are legacy systems with custom APIs. The good news: we can build a universal ingestion layer using Azure API Management as the gateway.

Carlos Vega: What's the data residency situation? Some of our clinic partners in Texas have specific data sovereignty requirements.

Fatima Al-Rashid: We've checked. Azure has compliant regions in South Central US and East US. We'd recommend a multi-region setup: primary in East US, failover in South Central. That covers the Texas requirements.

Carlos Vega: What about the Business Associate Agreements? We'd need BAAs with Augusta and any cloud providers.

Diana Park: Augusta has a standard HIPAA BAA. Microsoft Azure has a pre-signed BAA for covered entities. So that's handled. Fatima, walk us through the security architecture.

Fatima Al-Rashid: The proposal is: all PHI lives in a dedicated Azure environment with Private Endpoints — no public internet exposure. Data science team gets access via Azure Machine Learning with row-level security. Audit logging via Azure Monitor. Encryption at rest (AES-256) and in transit (TLS 1.3). We'd also implement a de-identification pipeline using Microsoft Presidio before data hits the analytical layer.

Carlos Vega: That's thorough. One thing I need: automated compliance reporting. Our CMS clinic partners require monthly data quality reports.

Fatima Al-Rashid: We can build that into the pipeline — dbt test results plus a custom reporting module. Estimated 2 weeks of additional work.

Nina Patel: Let's talk about the FHIR normalization. How do you handle schema drift when a clinic upgrades their EMR?

Liam Chen: Great question. We'd use a schema registry — Apache Avro with a Confluent-compatible registry. Any schema change triggers an automated alert and a validation job before data flows through. If validation fails, the clinic's feed goes into a quarantine queue — data doesn't flow until we validate the new schema.

Nina Patel: That solves my biggest headache. What's the latency on ingestion?

Liam Chen: Near-real-time for FHIR and HL7 — under 60 seconds. For the SFTP file drops, we'd poll every 15 minutes. The legacy custom APIs we'd call every hour.

Diana Park: On the ML side, Fatima — summarize the model environment.

Fatima Al-Rashid: We'd set up an MLflow tracking server on Azure ML. The data science team (Nina's 2 people) would use Azure ML compute clusters with pre-approved environments — no ad hoc package installs. Model deployment via Azure ML endpoints with A/B testing capability.

Nina Patel: My team will love that. Right now they're doing everything on their laptops.

Diana Park: Budget check. Liam, where are we on the $400k envelope?

Liam Chen: We're proposing a 14-week Phase 1 at $385k — tight but doable. That covers: $145k for ingestion layer, $120k for the secure analytical environment, $85k for data science tooling setup, $35k for compliance automation.

Carlos Vega: And the August prototype milestone?

Diana Park: Week 10 — that's around June 27th. We'd have a working predictive model on synthetic data that validates the architecture. Full production data by week 14.

Carlos Vega: I can work with that for the grant reporting.

Nina Patel: One more thing: our CTO — we don't have one right now, we're hiring — wants to see a detailed architecture decision record for each technology choice. Can Augusta provide that?

Diana Park: Absolutely. We'll document all architecture decisions with rationale as we go. That's good practice anyway.

Liam Chen: Action items: Augusta delivers final proposal by April 18th. MedBridge provides list of all clinic partner contacts for integration planning by April 14th. Carlos, can you share the CMS reporting template so we build to that spec?

Carlos Vega: I'll send it today.
""",
        },
        {
            "id": "medbridge_t3",
            "title": "MedBridge – Proposal Sign-off & Kickoff",
            "date": "2025-04-18",
            "content": """
Meeting: MedBridge Health – Proposal Review & Project Kickoff
Date: April 18, 2025
Attendees: Dr. Robert Hargrove (CEO), Nina Patel (VP Engineering), Carlos Vega (Head of Compliance) | Diana Park (Augusta), Liam Chen (Augusta), Fatima Al-Rashid (Augusta)

Dr. Hargrove: We've reviewed the proposal. Overall we're aligned. A few points I want to address before we sign.

Diana Park: Of course. What are the main ones?

Dr. Hargrove: First, the $385k — our Board approved $400k but they want a 10% contingency held in reserve. So effectively you're working with $360k ceiling, and the remaining $40k is our internal buffer.

Diana Park: That's a meaningful change. We'd need to reduce scope slightly. Liam, what comes out?

Liam Chen: We'd defer the automated CMS compliance reporting module — Carlos, you'd get the data quality dashboards but the formatted monthly report generator would move to Phase 2.

Carlos Vega: That's painful but I can manually generate the reports for the first two months if the underlying data is there.

Diana Park: Agreed. We'll move the compliance reporting module to Phase 2.

Dr. Hargrove: Second point — the August 31st grant deadline is firm. I need a contractual milestone: if the prototype isn't demo-ready by August 15th, I need the right to pause payments while we assess.

Diana Park: We understand the stakes. We'll add an August 15th milestone with a formal review. If we haven't hit it, we'll extend the project timeline at no additional cost to you until we do. We can't accept payment withholding but we can offer a service credit.

Dr. Hargrove: That's reasonable. I'll take it.

Nina Patel: I have a practical concern. You mentioned a 14-week timeline starting April 28th — that lands at July 28th. August 15th prototype review gives us less than 3 weeks of buffer. What happens if clinic integrations run long?

Liam Chen: Two things: first, we're front-loading the integrations — we'll tackle the 31 FHIR-native ones in weeks 1-4, which gets us 65% of the data immediately. The complex 16 integrations go in weeks 5-10. Even if the tail-end integrations slip, we have enough data volume for a credible prototype.

Nina Patel: What's the minimum viable dataset for the prototype model?

Liam Chen: Statistically, we need about 50,000 unique patient encounters with discharge outcomes. With 31 FHIR-native clinic partners and your current patient volume, we should hit that by week 6.

Dr. Hargrove: Good. That's the kind of thinking I want to hear.

Carlos Vega: BAAs — Augusta sent the draft. Legal reviewed it and there are two changes: first, we need a 30-day breach notification SLA instead of 60. Second, we need explicit language around subprocessors.

Diana Park: 30-day breach notification is fine — we're already at 15-day internal standard. Subprocessor language, I'll have our legal team update the template today.

Dr. Hargrove: Assuming the BAA is clean, we sign the SOW today. Kickoff April 28th.

Diana Park: Excellent. Fatima, take point on environment provisioning starting April 21st so we're ready to go on the 28th.

Fatima Al-Rashid: On it. I'll also set up the project Slack channel and shared documentation space.

Dr. Hargrove: One last thing — I'd like bi-weekly status reports in a format I can share with my Board. Not just technical updates — business impact framing.

Diana Park: Absolutely. We'll send you a Board-ready one-pager every other Friday.

Dr. Hargrove: Perfect. Let's do this.

Diana Park: Welcome aboard, MedBridge. We're going to build something that genuinely helps patients.
""",
        },
    ],
}

EMAIL_REPLIES = {
    "finova": {
        "id": "finova_email1",
        "from": "james.liu@finova.com",
        "from_name": "James Liu",
        "subject": "Re: FinoVa Data Pipeline – SOW and Kickoff Planning",
        "date": "2025-04-19",
        "content": """
Hi Marcus,

Quick update from our side — legal has approved the SOW with minor redlines attached (see document). The main changes are:
1. Added a force majeure clause (standard for us)
2. Changed "business days" to calendar days in section 6.3 for the notification timelines
3. Minor IP clarification in section 8 — we own any custom connectors built for our broker APIs

Sarah has signed off. I'll get the countersigned copy to you by EOD.

On kickoff logistics — April 21st works. Can we make it 10am EST? Our morning standup ends at 9:45. Also, we'll need Augusta to sign into our Jira instance rather than using a separate project management tool. Hope that's okay.

One concern I wanted to flag early: two of our broker API integrations (TradeDesk Pro and LegacyBond Connect) have rate limits that we didn't account for in the architecture discussions. TradeDesk Pro caps at 500 requests/minute and LegacyBond Connect is even more restrictive at 100 requests/minute. During peak hours (9:30am-4pm EST) we're already hitting these limits with our current system. Streaming ingestion might make this worse. Can Aisha think about this before Monday?

Also, I spoke with our Head of Security. He wants to schedule a 30-minute security review call with Aisha to go over the Snowflake access configuration before we grant cluster access. Can you coordinate that for next week?

Looking forward to getting started.

Best,
James

P.S. — Sarah asked me to mention that Meridian Fund's PM, David Walsh, might join the April 28th kickoff as an observer. He's been driving the urgency on our end. Worth knowing.
""",
    },
    "medbridge": {
        "id": "medbridge_email1",
        "from": "nina.patel@medbridge.health",
        "from_name": "Nina Patel",
        "subject": "Re: MedBridge Phase 1 – Pre-Kickoff Checklist & Access Setup",
        "date": "2025-04-22",
        "content": """
Hi Diana,

Thanks for the pre-kickoff checklist. Going through each item:

1. Azure subscription access — DONE. I've added Liam and Fatima as Owners on the dev subscription. Production access will follow after compliance sign-off, which Carlos expects by April 25th.

2. Clinic partner contacts list — DONE. See attached spreadsheet. Quick note: 3 of the clinics (Riverside Medical Group, Summit Orthopedics, and Blue Ridge Family Care) are in the middle of EMR migrations. Riverside is moving from eClinicalWorks to Epic (expected cutover: May 15th), Summit is upgrading Cerner versions (no cutover date yet), and Blue Ridge is the most complex — they're consolidating two legacy systems into a new Athena instance. Liam should know these are going to be non-trivial integrations.

3. BAA execution — Our legal team returned the updated version this morning. The subprocessor language looks good. We're ready to countersign.

4. Data science team intro — I'm looping in Marcus Ng and Priya Singh (our two data scientists) on this email. Fatima, can you schedule a 1-hour onboarding session with them for Azure ML access? They're eager to get started. One thing to know: Marcus Ng has a background in survival analysis which might actually be very relevant for the readmission modeling.

5. One issue I need to raise: our IT department is pushing back on giving Augusta direct database access to the staging environment. Their concern is around credential management and the audit trail. Can we set up a VPN + jump server access model instead? Our IT lead (Frank Torres) is available to discuss.

On the project communication side — we're a Slack-first culture. Can the Augusta team join our workspace? I'll send invites to Diana, Liam, and Fatima.

Also — small but important — Dr. Hargrove has asked that we keep him in the loop on any significant architectural decisions before they're finalized. He's more technical than he lets on in meetings, and he gets unhappy if he feels blindsided. Just a heads up for the team.

Excited to kick this off on Monday!

Nina

P.S. — Fatima, I noticed you used Microsoft Presidio for the de-identification layer. We actually evaluated Presidio 18 months ago and found it struggled with clinical abbreviations (e.g., "pt" for patient, "dx" for diagnosis). Do you have a plan for that? It's a real risk for our data quality.
""",
    },
}
