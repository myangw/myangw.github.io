---
title: "Designing Data-Intensive Applications: Chapter 1 Summary"
date: 2022-01-02T00:00:00+09:00
slug: "designing-data-intensive-applications-chapter-1-summary"
tags:
  - Designing Data-Intensive Applications
  - System Design
draft: false
ShowToc: true
TocOpen: false
---

Since November 2021, I have been studying Martin Kleppmann's 'Designing Data-Intensive Applications' through a study group. This remarkably compact yet profound treatise contains substantial undigested material. While the study group approaches conclusion, I shall revisit particularly significant chapters through review-oriented summarization.

# Preface

### Forces Driving Database and Distributed System Development

- Handling enormous data quantities and traffic volumes → necessitated novel tool creation
- Enterprises require agility and rapid market adaptation
- Free open-source software proliferation
- CPU clock speed growth stagnation, multicore processors standardization, network acceleration → continuous parallelization expansion
- IaaS platforms such as AWS enable distributed system development for modest teams
- High availability demands for services

### Data-Intensive Applications

Applications wherein data quantity, complexity, and transformation velocity constitute principal challenges.

↔ Compute-intensive: CPU cycles constitute bottlenecks

### Study Content

- Enduring principles independent of rapid technological change and trends
- Core algorithms, principles, and trade-offs of data systems
    - Data system operational mechanisms + operational rationale
- Capability determination for appropriate technology selection + methodology for combining tools to establish robust application architecture foundations

### Reference Materials Collection

[https://github.com/ept/ddia-references](https://github.com/ept/ddia-references)

# Chapter 1. Reliable, Scalable, and Maintainable Applications

This chapter addresses terminology and approaches employed throughout the treatise.

## Conceptualizing Data Systems

- Rationale for encompassing databases, queues, caches, et cetera under the comprehensive terminology "data systems"
    - Novel tools are optimized for diverse use cases, no longer fitting traditional classifications precisely
        - Redis: datastore utilizing message queues, Apache Kafka: message queue guaranteeing persistence, et cetera
    - No single tool satisfies both data processing and storage across extensive requirement spectrums

- Three considerations for superior data system design:
    - Reliability
    - Scalability
    - Maintainability

## Reliability

- "Continues operating correctly even when faults occur"
    - Applications perform expected functions
    - Systems accommodate unexpected usage
    - Performance satisfies sufficient use cases under anticipated load and data quantities
    - Systems prevent unauthorized access and misuse

- Fault: Potential failures
    - System components deviating from specifications
    - ≠ Failure: Entire system cessation providing user services
- Fault-tolerant or resilient: Capable of fault anticipation and adaptation
- Zero fault probability proves impossible; design importance lies in preventing faults from causing failures
    - [Netflix's Chaos Monkey](https://netflixtechblog.com/the-netflix-simian-army-16e57fbab116) deliberately induces faults for fault-tolerance system testing (https://github.com/netflix/chaosmonkey)

### Fault Categories and Solutions

- Hardware faults: Component failures
    - Solution → Add redundancy to hardware components
        - RAID disk configuration, dual power supplies, hot-swap CPUs
        - Utilize redundant components during replacement
    - Recently: Data quantity and computation increases → more equipment → increased hardware fault rates
        - Cloud platforms like AWS prioritize flexibility and elasticity over individual equipment reliability
        - → Transition toward systems tolerating entire equipment loss through software fault-tolerance techniques or hardware redundancy addition

- Software faults: Systematic errors within systems
    - Unlike random, mutually independent hardware faults, correlation among nodes causes greater system errors
        - Linux kernel bugs, resource-consuming processes, service degradation, cascading failures
    - Solutions: No rapid remedies
        - Careful consideration of system assumptions and interactions
        - Comprehensive testing, process isolation, monitoring

- Human errors
    - Design systems minimizing error possibilities
    - Provide sandbox environments with real data but no user impact
    - Thorough testing at all levels
    - Rapid rollback for configuration changes, gradual new code rollout
    - Monitoring for performance metrics and error rates
    - Operational training and practice

## Scalability

Capacity for stable operation under increased load

Scalability represents not binary presence/absence but rather considerations regarding 'how to address system growth in specific manners' and 'how to allocate resources for additional load handling.'

### Load Description

- Representable through load parameters
    - Load parameter examples:
        - Web server requests per second
        - Database read/write ratios
        - Concurrent active users in chat rooms
        - Cache hit rates
    - Load parameter averages may prove significant, or extreme minority cases may dominate
        - Example: 2012 Twitter architecture evolution
            - Two principal operations: tweet posting (average 4.6k requests/second, peak 12k+), home timeline reading (300k requests/second average)
            - Individual user tweet posting necessitates appearance across numerous follower timelines - fan-out
            - Solutions evolved: 1→2→3
                1. Global tweet collection insertion. Home timeline requests locate all followed users, retrieve all tweets, temporally sort and merge. → Read-time expense
                2. Maintain per-user home timeline caches. User tweet posting inserts into follower caches. → Pre-computation at write-time reduces read-time computation
                3. Hybrid: Predominantly method 2, but extremely high-follower users excluded from fan-out, separately retrieved and merged at read-time → Single writes become excessive for numerous followers

### Performance Description

- Output measurement approaches:
    - How does performance respond to increased load parameters?
    - What resource increases maintain performance?

- Critical performance metrics:
    - Batch processing systems - throughput: Records processable per second/dataset. Total task duration
    - Online systems - response time: Duration between client request and response receipt

- Response time should be conceptualized as measurable value distribution rather than singular numbers, as identical requests yield varying response times
- Arithmetic means prove inadequate metrics. Actual user delay experience quantities prove critical
    - → Percentiles and medians prove appropriate
        - Sort fastest to slowest times
        - Half of user requests exceed median duration
        - Tail latency percentiles (95th, 99th, 99.9th) determine outlier severity
            - Amazon employs 99.9th percentile. Though affecting 1 in 1000, that individual often represents VIP customers with maximal account data
        - Minority slow request processing delays subsequent processing: head-of-line blocking
            - → Client-side response time measurement proves critical

### Load Response Approaches

- Scale up (vertical scaling), Scale out (horizontal scaling)

Practical approach combinations prove necessary.

- Stateful single-node data systems possess substantial distributed implementation complexity → Conventional wisdom maintains single-node databases scaling up until high-availability requirements emerge
    - Recent distributed system tooling and abstraction improvements are changing conventions

- Elastic systems automatically add computing resources upon load increase detection prove useful for unpredictable loads, but manually scaled systems prove simpler with fewer operational surprises

- Universal, all-situation scaling architecture proves nonexistent
    - Architecture-determining factors: Read/write quantities, storage data quantities, data complexity, response time requirements, et cetera
    - Assumptions regarding principal operations and infrequent operations prove critical for architectural decisions

## Maintainability

Design to reduce maintenance pain and avoid legacy creation

### Operability: Facilitating Operational Convenience

- Enable easy repetitive task performance, allowing operations teams to focus on higher-value activities
    - Monitoring, automation, documentation, comprehensible operational models, et cetera

### Simplicity: Managing Complexity

- Eliminate accidental complexity through superior abstraction
- Example: High-level programming languages conceal machine code, CPU registers, system calls

### Evolvability: Facilitating Change

- Requirements evolve continuously
- Agile methodologies: TDD, refactoring
- Create simple, comprehensible systems
