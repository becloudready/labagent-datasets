---
doc_id: PUB-gcp-af-cost
title: Google Cloud Well-Architected Framework: Cost optimization pillar
source_url: https://docs.cloud.google.com/architecture/framework/cost-optimization
license: Creative Commons Attribution 4.0 (CC BY 4.0)
attribution: Google LLC
retrieved: 2026-10-23
changes: Converted from HTML to Markdown; navigation and images removed. Wording unchanged.
---

# Google Cloud Well-Architected Framework: Cost optimization pillar

- Home

# Well-Architected Framework: Cost optimization pillar  Last reviewed 2026-10-13 UTC

The cost optimization pillar in the Google Cloud Well-Architected Framework describes principles and recommendations to optimize the cost of your workloads in Google Cloud.

The intended audience includes the following:

- CTOs, CIOs, CFOs, and other executives who are responsible for strategic cost management.
- Architects, developers, administrators, and operators who make decisions that affect cost at all the stages of an organization's cloud journey.

The cost models for on-premises and cloud workloads differ significantly. On-premises IT costs include capital expenditure (CapEx) and operational expenditure (OpEx). On-premises hardware and software assets are acquired and the acquisition costs are depreciated over the operating life of the assets. In the cloud, the costs for most cloud resources are treated as OpEx, where costs are incurred when the cloud resources are consumed. This fundamental difference underscores the importance of the following core principles of cost optimization.

**Note:** You might be able to classify the cost of some Google Cloud services (like Compute Engine sole-tenant nodes) as capital expenditure. For more information, see Sole-tenancy accounting FAQ.

For cost optimization principles and recommendations that are specific to AI and ML workloads, see AI and ML perspective: Cost optimization in the Well-Architected Framework.

## Evaluate workloads using an agent skill

To enable AI agents to evaluate your cloud workloads against the principles and recommendations in this pillar, use the [`google-cloud-waf-cost-optimization`](https://github.com/google/skills/tree/main/skills/cloud/google-cloud-waf-cost-optimization) skill, which is available in the Google Agent Skills repository in GitHub.

To install the skill, run the following command in your agent's client or terminal:

When prompted, specify the AI agents for which you want to install the skill and set the installation scope (project or global).

If you've already installed the skill, you can update it to the latest version by running the following command:

**Note:** If `npx` is not available in your environment, install [Node.js](https://nodejs.org/en/download), which includes `npm` and `npx`.

## Core principles

The recommendations in the cost optimization pillar of the Well-Architected Framework are mapped to the following core principles:

- [**Align cloud spending with business value**](/architecture/framework/cost-optimization/align-cloud-spending-business-value): Ensure that your cloud resources deliver measurable business value by aligning IT spending with business objectives.
- [**Foster a culture of cost awareness**](/architecture/framework/cost-optimization/foster-culture-cost-awareness): Ensure that people across your organization consider the cost impact of their decisions and activities, and ensure that they have access to the cost information required to make informed decisions.
- [**Optimize resource usage**](/architecture/framework/cost-optimization/optimize-resource-usage): Provision only the resources that you need, and pay only for the resources that you consume.
- [**Optimize continuously**](/architecture/framework/cost-optimization/optimize-continuously): Continuously monitor your cloud resource usage and costs, and proactively make adjustments as needed to optimize your spending. This approach involves identifying and addressing potential cost inefficiencies before they become significant problems.

These principles are closely aligned with the core tenets of cloud FinOps. FinOps is relevant to any organization, regardless of its size or maturity in the cloud. By adopting these principles and following the related recommendations, you can control and optimize costs throughout your journey in the cloud.

## Contributors

Author: Nicolas Pintaux \| Customer Engineer, Application Modernization Specialist

Other contributors:

- Anuradha Bajpai \| Solutions Architect
- Daniel Lees \| Cloud Security Architect
- Eric Lam \| Head of Google Cloud FinOps
- Fernando Rubbo \| Cloud Solutions Architect
- Filipe Gracio, PhD \| Customer Engineer, AI/ML Specialist
- Gary Harmson \| Principal Architect
- Jose Andrade \| Customer Engineer, SRE Specialist
- Kent Hua \| Solutions Manager
- Kumar Dhanagopal \| Cross-Product Solution Developer
- Marwan Al Shawi \| Partner Customer Engineer
- Radhika Kanakam \| Program Lead, Google Cloud Well-Architected Framework
- Samantha He \| Technical Writer
- Steve McGhee \| Reliability Advocate
- Sergei Lilichenko \| Solutions Architect
- Wade Holmes \| Global Solutions Director
- Zach Seils \| Networking Specialist

Next

 Align spending with business value   arrow_forward
