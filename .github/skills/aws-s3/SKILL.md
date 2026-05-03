---
name: aws-s3
description: Use when working on reusable Amazon S3 concepts, consistency rules, object naming, and storage-access behavior for artifact storage features.
---

# AWS S3

## Summary

Use this skill for reusable S3 behavior, naming, and access rules. Keep repo-specific artifact naming policy and publish workflow rules in the agent file.

## Apply This Skill When

- Designing object-key layouts and bucket usage patterns.
- Reasoning about S3 consistency, overwrite behavior, and object identity.
- Choosing access-control and public-access defaults.
- Mapping application artifact concepts onto buckets, objects, prefixes, and metadata.

## Rules

- Treat bucket, key, and optional version ID as the full object identity.
- Prefer IAM and bucket policy controls over ACLs.
- Keep public access blocked unless there is a reviewed exception.
- Design object keys to be stable, URL-safe, and free of path-normalization traps.
- Remember that multi-key updates are not atomic and concurrent writers to the same key are last-writer-wins.

## Official Sources

- S3 overview: https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html
  S3 provides strong read-after-write consistency for PUT and DELETE operations, but concurrent writers to the same key still use last-writer-wins semantics.
- Object key naming: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-keys.html
  Object keys are UTF-8 strings up to 1,024 bytes, are case-sensitive, and prefixes are just naming conventions over a flat object space.

## Useful Takeaways

- Strong read-after-write consistency makes publish verification simpler after a successful upload.
- Prefixes create an inferred hierarchy only; S3 itself remains a flat namespace.
- Avoid period-only path segments and awkward special characters in keys because different tools normalize them differently.
- Modern S3 guidance favors Object Ownership and policies over ACL-heavy designs.

## Validation Focus

- Keys are deterministic and safe.
- Access policy assumptions match AWS guidance.
- Application logic does not assume cross-key atomicity.
- Read-after-write behavior is used correctly without assuming write locks.