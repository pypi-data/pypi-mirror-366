# Core Module

The core module contains the fundamental components of doteval, including the `@foreach` decorator and essential evaluation functions.

## @foreach Decorator

The main decorator that transforms functions into evaluations. This is the primary entry point for most users.

**Usage**: `@foreach("param1,param2", dataset)`

::: doteval.foreach

## ForEach Class

The configurable version of the foreach decorator that allows custom retry strategies, concurrency, and storage backends.

::: doteval.ForEach

## Core Functions

Essential functions for advanced usage and programmatic access.

::: doteval.core
