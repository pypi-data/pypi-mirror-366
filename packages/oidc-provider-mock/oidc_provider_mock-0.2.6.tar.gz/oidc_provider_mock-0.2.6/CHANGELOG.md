# Changes

## v0.2.6 - 2025-08-01

- Add `--host` option to CLI
- Drop support for Authlib v1.4
- Display more detailed error message when client_id is wrong or missing
- Don’t log stack traces on client errors

## v0.2.5 - 2025-05-27

- Suppress deprecation warnings introduced in Authlib v1.6.

## v0.2.4 - 2025-04-19

- Suppress exception logging on client errors in token endpoint.
- Use correct error code "invalid_grant" when refresh token is not valid.

## v0.2.3 - 2025-04-18

- Add HTTP endpoint to revoke all tokens for a user.

## v0.2.2 - 2025-04-14

- Set initial focus to `sub` input in authorization form.

## v0.2.1 - 2025-03-20

- Add required `httpx` production dependency.
