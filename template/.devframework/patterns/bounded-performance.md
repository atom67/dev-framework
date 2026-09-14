# Bounded work and user-visible performance

## Problem and applicability

A fast small dataset can hide work proportional to every record, image and layout element.
Main OS optimized inner timings while users still saw multi-second freezes. Apply to growing
lists, queries, imports and batch jobs.

## Invariant and protocol

Work per interaction has a measured budget at representative volume. Measurement ends at
the user-visible outcome, not merely when data is assigned to a widget.

1. Record data size/distribution, cold/warm cache, device class and concurrent workload.
   Measure database/network, transformation, binding and rendered result separately; report
   percentiles/outliers over repeated trials. Establish product-specific budgets first.
2. Bound materialized rows through pagination/windowing/virtualization. Check the actual
   panel/template: changing layout can disable virtualization. Count realized elements.
   Decoding large images into thumbnail-sized slots wastes work.
3. Move slow I/O/image decoding off the UI/event loop; bound concurrency, decoded size,
   caches and queues. Cancel obsolete work; validate thread affinity when handing results back.
4. Avoid per-item aggregate queries and notification storms: batch/group queries, inspect
   plans at real cardinality and batch collection updates. Not every correlated subquery is
   slow: indexes/optimizer/measurements decide. A collection reset may lose focus/scroll state.
5. Keep locks short; capture immutable input under its owning thread/lock before slow work.
   Copying an already concurrently mutated collection is not safe. Revalidate before commit.
6. Avoid full cascading refreshes for one counter. Declare acceptable staleness, update
   the affected projection and specify overload behaviour.

## Failure tests

- Small/large lists, cold/warm images and rapid navigation/cancellation.
- Plant a nonvirtualizing panel: realized-row/latency checks must detect the regression.
- Count queries/notifications; plant per-row work and detect growth.
- Concurrent UI edits during background scanning use a snapshot, not a mutable live list.
- Measure click-to-render, not assignment duration; record memory/cache/queue ceilings.

## Observability

Latency p50/p95/p99 with sample count, rows read/realized, query count, decoded bytes,
cache hit/eviction rate, queue depth and event-loop stalls under the same before/after load.
Keep diagnostics engineer-accessible without assigning log hunting to the product owner.

## Limits

Not a portable WPF implementation or universal millisecond target. Panels, image freezing,
SQL pragmas and cache warmup are workload choices, not global defaults. Average latency
does not prove tail latency, accessibility or correctness. CI timings need stable runners;
operation counts are often more deterministic. Pair with AGENTS.md section 5 cost analysis.
