# ADR-0002: Add a way to create account and login [frontend]

**Date:** 2026-09-21
**Status:** pending

## Context

We want to create a frontend for creating accounts and logging into accounts..

## Decision

We created a React frontend that calls the python backend through React's auth modules. And seperated multiple layers (like auth layer, api layer, etc).

## Consequences

It means now that the frontend has been made, the pipeline for creating accounts and logging in has been complete. All that's need is to add auth token support and tidy up the CSS.
Since the modules and frameworks have been decided, any changes to project structure will be very complicated.