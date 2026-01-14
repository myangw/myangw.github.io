---
title: "Lessons Learned After One Year: Resignation Retrospective"
date: 2023-05-21T00:00:00+09:00
slug: "lessons-learned-after-one-year-resignation-retrospective"
tags:
  - retrospective
  - lessonLearned
  - product
draft: false
ShowToc: true
TocOpen: false
---

Recently, I made the decision to depart from the organization where I had been employed for slightly over one year.

This was the first company I joined after specifically evaluating the problem domain they were addressing. I resonated deeply with the challenges the organization sought to resolve—more profoundly than at any previous employer—and I consider the work undertaken to have been valuable. The team members were exceptional. This assessment remains unchanged even at this moment of departure. Nevertheless, various factors led me to conclude that the organization and I must pursue divergent paths.

Rather than presenting a comprehensive retrospective encompassing the entirety of my contributions or the rationale behind my resignation, I intend to document the lessons learned that have proven significant and experientially valuable to me, as they occur to me.

## Insights Gained Through Purpose-Driven Organization

Following the completion of my onboarding period, I consistently operated within a purpose-driven organizational structure. The team composition was not functionally segregated by developers alone, but rather comprised cross-functional personnel including developers, designers, and product owners, all unified toward achieving a singular objective. While this initial experience involved trial and error and exhibited certain limitations, it aligned well with my working style and yielded substantial learnings.

### The Imperative of Constantly Considering the "Why" of Work

This consensus was particularly emphasized within the team I collaborated with last year. The fundamental principle was that if we do not comprehend why we must undertake specific work, customers will similarly lack justification for utilizing our product.

During ideation sessions commencing from a blank slate, myriad opinions emerge. Dismissing seemingly plausible features, sophisticated functionalities, and technically intriguing implementations, our primary criterion was consistently: "What value can this work deliver to customers—and does it contribute to our team's objective?" By continuously reinforcing this simple yet explicit standard among team members and incorporating it into our decision-making processes, I came to believe that among the initiatives we undertook, both substantial and minor, not a single one lacked significance.

While this appears self-evident, considering the "why" as an individual developer was critically important. As someone possessing detailed implementation knowledge, I worked to contemplate and propose more effective methods to fulfill objectives. On one occasion, I received technically complex requirements that seemed disproportionate to a relatively simple and lightweight purpose. Upon consulting with the Product Owner, I learned that the specifications had been formulated under the assumption that such technical complexity was necessary due to limited technical understanding. Subsequently, we collaboratively revised the requirements. Through direct experience, I reinforced the conviction that developers who contemplate the "why" contribute significantly more to the team's mission and business objectives than merely functioning as individuals who implement APIs according to prescribed specifications.

### Executing in Small Increments

For problems lacking definitive solutions, it becomes easy to extend the duration spent deliberating and discussing whether approaches will function effectively or whether inaction might be preferable. In such circumstances, we consistently formulated hypotheses, contemplated how to decompose them into smaller components for validation, verified the hypotheses, and then proceeded to subsequent steps. We avoided unnecessarily implementing large-scale features only to subsequently roll back the entirety of the implementation. By developing features with minimal scope, confirming whether users genuinely required the functionality, and then progressively enhancing sophistication and impact, we maintained an iterative approach.

These processes were enabled by establishing a data pipeline capable of validating experiments and cultivating a culture of data-driven decision-making. Having previously experienced the anguish as a practitioner when a senior decision-maker arbitrarily mandated "we must create XX" without substantiation, resulting in uncontrolled specification expansion and planning modifications, I acutely appreciated how this culture represented a more rational methodology for rapidly approaching objectives.

### Retrospectives Facilitate Improvement

We conducted retrospectives at the conclusion of each sprint/iteration (typically approximately two weeks). Categorizing items into Keep/Stop/Try, we collaboratively considered practices to maintain, issues requiring resolution, and initiatives worth attempting. On one occasion, we even composed a "retrospective of the retrospective." While there were items listed under Try that we ultimately failed to attempt, through frequent repetition of this process, the team's working methodology gradually systematized and cohesion improved. As we authored "retrospectives of retrospectives," our retrospective methodology evolved to suit our circumstances. When retrospective sessions approached amid intensive work periods, I would initially approach the conference room with a sense of "oh no, already...," but upon engaging in the retrospective, I consistently recognized it as an essential activity.


## Insights Gained During Reduced Team Composition

### The Absence of Perfectly Optimal or Suboptimal Design

Last year, there was consistently one additional backend developer besides myself on the team. These were highly skilled individuals, and technical discussions regarding new features or tasks typically yielded superior conclusions compared to initial conceptions. Subsequently, from this year onward, I began developing independently, which initially imposed considerable pressure. As the scope of development and operational responsibilities expanded, concerns accumulated. One day, while conversing with a leader from another team, I heard: "Where does perfectly optimal design exist from the outset? It is learned through operational experience," which provided clarity.

Through actual operational experience and enhancing previously minimally-scoped features, I realized that whether decisions were collaboratively determined with conviction regarding their optimality or individually conceived, they could become legacy requiring modification when confronted with specific requirements. Since we cannot perfectly anticipate the future and evolving business circumstances...

When enhancement proved difficult due to past suboptimal decisions, the solution involved incrementally modifying the structure and performing migrations. While this represents costly rework, directly writing suboptimal code and subsequently improving it appears to resonate more profoundly than lessons acquired through reading.

### The Necessity of Rigorous Prioritization

Previously, I did not significantly regard tasks requiring one or two hours as substantial work. When non-developer team members requested work outside the sprint scope, when there was another backend developer on the team, I would readily undertake and expeditiously process such requests. This approach remained feasible while adequately completing sprint commitments. However, when I became the sole backend developer on the team, despite exerting maximum effort, work progressively accumulated. When bugs discovered during QA, business stakeholder query modification requests, sprint tasks, and technical issues I identified simultaneously accumulated, "working overtime" proved insufficient. Since my time and energy were finite... The paramount priority ultimately became fulfilling the minimum completion criteria within the sprint, and for remaining items, I negotiated priorities and timelines with stakeholders. There were backlogs that regrettably had to be deferred, almost abandoned. Nevertheless, this approach enabled sustainable work practices. Moreover, even during less intensive periods, I later realized while organizing my resume that I should have more carefully considered what I should accomplish during those timeframes, beyond the team's mission, regarding personal importance and impact.


## Insights Gained Through Excellent Colleagues

### A Preference for "Unconventional" Individuals

I recall maintaining a reserved demeanor toward team members for nearly two months following my entry. While I was not incapable of communication, as a probationary employee and newly constituted purpose-driven team member, not only the leader but everyone appeared capable of evaluating my performance. During self-introduction, I candidly disclosed my reserved nature to team members, but the expression "reserved" essentially signified "exercising caution to avoid being evaluated as unusual/incompetent."

Fortunately, the team consisted exclusively of individuals who desired to support one another and collectively excel. No one possessed attitudes of arbitrarily judging/evaluating other team members, dismissing opinions, or attempting to establish superiority. As work progressed, I progressively confirmed increasing chemistry with team members. As I tangibly experienced that these individuals endeavored to accomplish work effectively rather than evaluating others, and that I was part of that collective, psychological security gradually developed and expressiveness became uninhibited. At a certain point, we would tease each other saying "XX is really an unconventional person haha," which became a compliment regarding that person's individuality. People are inherently different and possess distinctive thoughts, as do I. When such characteristics are not concealed or confined to invisible frameworks but expressed through healthy methodologies, ideas beneficial to product development emerged more effectively and teamwork improved.

### The Generosity of Praise

Reflecting upon it, I previously tended to silently think "oh, that's good" or "well done" and simply move on. However, as I received innumerable 👍 emojis, custom-created emojis, memes, various reactions of all sizes, and praise, I recognized how encouraging this was and how it enriched workplace experience. (While 👎 emoji occasionally became a playful trend 😊) At some point, I began creating emojis like "best planner" and briefly noting acknowledgments during retrospectives rather than simply moving on. Not forced praise, but cultivating a culture of praising, encouraging, and acknowledging genuine excellence contributed to happiness.

### Self-Understanding
- **Insights Through Feedback**

Providing feedback to someone requires corresponding attention and observation. During my initial performance evaluation season, providing feedback was straightforward for team members with whom I frequently interacted regarding work, but I felt perplexed about what to communicate to team members with less interaction. However, those individuals subsequently observed me with greater attention and composed evaluations, which was humbling. When receiving simple affirmations like "you are performing well," I would persistently inquire about specific aspects (apologetically to leaders...), and through the feedback provided, I heard terminology describing myself that I encountered for the first time and learned about strengths I had underestimated.

- **Insights Through Colleagues' Excellence**

There were moments when I acutely realized how superficial and inadequate I was. When observing team members conducting deep dives to derive initiatives from numerous problem identifications, when receiving technical considerations I had never contemplated, and countless other instances I cannot enumerate, there existed qualities I wished to emulate and gaps I desired to fill. Each instance stimulated me to research and contemplate further, and elevated standards remain in my mind.

---------
Organizing these learnings is something I developed more habitually after joining this organization. Upon review, it appears I wrote more about what was beneficial to me rather than learnings... haha. With gratitude, I must properly conclude this current journey and prepare for the next step. Working methodologies, pursued values, team dispositions, and numerous other aspects will differ, but I anticipate what additional learnings await.
