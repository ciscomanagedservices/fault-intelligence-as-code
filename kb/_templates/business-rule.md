---
type: business-rule
title: "<% tp.file.title %>"
rule_type: escalation
status: active
owner: ""
effective_date: <% tp.date.now("YYYY-MM-DD") %>
review_date: ""
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags:
  - business-rule
related: []
sources: []
---

# <% tp.file.title %>

## Rule Statement

[The rule in plain language. One or two sentences. "When X, you must Y."]

## Scope

[Who this rule applies to and under what conditions.]

## Details

[Full explanation of the rule — thresholds, timelines, approval chains, exceptions.]

## Decision Tree

[Optional: if the rule has branches, describe them here.]

- If [condition A]: [action]
- If [condition B]: [action]
- Otherwise: [default action]

## Exceptions

[Any documented exceptions to this rule and who may authorize them.]

## Contacts

[Who owns or enforces this rule. Who to contact for exceptions.]

- Rule owner: [[]]
- Escalation contact: [[]]

## Related Rules

-

## Sources

-
