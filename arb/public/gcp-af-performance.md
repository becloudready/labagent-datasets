---
doc_id: PUB-gcp-af-performance
title: Google Cloud Well-Architected Framework: Performance optimization pillar
source_url: https://docs.cloud.google.com/architecture/framework/performance-optimization
license: Creative Commons Attribution 4.0 (CC BY 4.0)
attribution: Google LLC
retrieved: 2026-10-23
changes: Converted from HTML to Markdown; navigation and images removed. Wording unchanged.
---

# Google Cloud Well-Architected Framework: Performance optimization pillar

- Home

# Well-Architected Framework: Performance optimization pillar  Last reviewed 2026-10-22 UTC

This pillar in the Google Cloud Well-Architected Framework provides recommendations to optimize the performance of workloads in Google Cloud.

This document is intended for architects, developers, and administrators who plan, design, deploy, and manage workloads in Google Cloud.

The recommendations in this pillar can help your organization to operate efficiently, improve customer satisfaction, increase revenue, and reduce cost. For example, when the backend processing time of an application decreases, users experience faster response times, which can lead to higher user retention and more revenue.

The performance optimization process can involve a trade-off between performance and cost. However, optimizing performance can sometimes help you reduce costs. For example, when the load increases, autoscaling can help to provide predictable performance by ensuring that the system resources aren't overloaded. Autoscaling also helps you to reduce costs by removing unused resources during periods of low load.

Performance optimization is a continuous process, not a one-time activity. The following diagram shows the stages in the performance optimization process:

![Performance optimization process](/static/architecture/framework/images/perf-optimization-process.svg)

The performance optimization process is an ongoing cycle that includes the following stages:

1.  **Define requirements**: Define granular performance requirements for each layer of the application stack before you design and develop your applications. To plan resource allocation, consider the key workload characteristics and performance expectations.

2.  **Design and deploy**: Use elastic and scalable design patterns that can help you meet your performance requirements.

3.  **Monitor and analyze**: Monitor performance continually by using logs, tracing, metrics, and alerts.

4.  **Optimize**: Consider potential redesigns as your applications evolve. Rightsize cloud resources and use new features to meet changing performance requirements.

    As shown in the preceding diagram, continue the cycle of monitoring, re-assessing requirements, and adjusting the cloud resources.

For performance optimization principles and recommendations that are specific to AI and ML workloads, see AI and ML perspective: Performance optimization in the Well-Architected Framework.

## Evaluate workloads using an agent skill

To enable AI agents to evaluate your cloud workloads against the principles and recommendations in this pillar, use the [`google-cloud-waf-performance-optimization`](https://github.com/google/skills/tree/main/skills/cloud/google-cloud-waf-performance-optimization) skill, which is available in the Google Agent Skills repository in GitHub.

To install the skill, run the following command in your agent's client or terminal:

When prompted, specify the AI agents for which you want to install the skill and set the installation scope (project or global).

If you've already installed the skill, you can update it to the latest version by running the following command:

**Note:** If `npx` is not available in your environment, install [Node.js](https://nodejs.org/en/download), which includes `npm` and `npx`.

## Core principles

The recommendations in the performance optimization pillar of the Well-Architected Framework are mapped to the following core principles:

- Plan resource allocation
- Take advantage of elasticity
- Promote modular design
- Continuously monitor and improve performance

## Contributors

Authors:

- Daniel Lees \| Cloud Security Architect
- Gary Harmson \| Principal Architect
- Luis Urena \| Developer Relations Engineer
- Zach Seils \| Networking Specialist

Other contributors:

- Filipe Gracio, PhD \| Customer Engineer, AI/ML Specialist
- Jose Andrade \| Customer Engineer, SRE Specialist
- Kumar Dhanagopal \| Cross-Product Solution Developer
- Marwan Al Shawi \| Partner Customer Engineer
- Nicolas Pintaux \| Customer Engineer, Application Modernization Specialist
- Ryan Cox \| Principal Architect
- Radhika Kanakam \| Program Lead, Google Cloud Well-Architected Framework
- Samantha He \| Technical Writer
- Wade Holmes \| Global Solutions Director

Next

 Plan resource allocation   arrow_forward
