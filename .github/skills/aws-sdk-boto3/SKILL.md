---
name: aws-sdk-boto3
description: Use when working on reusable Boto3 client, paginator, waiter, and credential-resolution patterns for AWS integrations such as S3.
---

# AWS SDK Boto3

## Summary

Use this skill for reusable Boto3 usage patterns. Keep project-specific adapter contracts and artifact naming outside this skill.

## Apply This Skill When

- Creating AWS clients or sessions in Python.
- Using S3 client operations such as `put_object`, `get_object`, `upload_file`, and `download_file`.
- Handling pagination or waiter behavior.
- Configuring credentials and profile-based sessions safely.

## Rules

- Prefer session or environment-based credential resolution over hardcoded values.
- Use paginators for potentially long listings.
- Use waiters when existence checks need controlled polling semantics.
- Keep AWS client construction centralized instead of scattered across modules.
- Let Boto3 manage signature generation and retries rather than reimplementing request signing.

## Official Sources

- Boto3 S3 reference: https://docs.aws.amazon.com/boto3/latest/reference/services/s3.html
  The S3 client reference exposes low-level operations, paginators, waiters, and resources for object and bucket workflows.
- Boto3 credentials guide: https://docs.aws.amazon.com/boto3/latest/guide/credentials.html
  Boto3 searches for credentials in a defined order and recommends shared credentials files, environment variables, roles, or login sessions instead of hardcoding secrets.

## Useful Takeaways

- `boto3.client('s3')` is the low-level entry point when you want explicit API control.
- S3 paginators are available for object listings and should be used instead of assuming single-response completeness.
- Boto3's credential provider chain stops at the first valid source, so local config and environment decisions must be deliberate.
- Shared profiles and temporary credentials are safer defaults than embedding access keys in code.

## Validation Focus

- Credential loading follows AWS guidance.
- Long listings use paginators.
- Object operations use the correct client methods.
- AWS client creation is deterministic and testable.