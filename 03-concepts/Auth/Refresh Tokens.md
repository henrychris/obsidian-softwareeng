[RFC](https://datatracker.ietf.org/doc/html/rfc6749#section-1.5)
# Security Considerations
[RFC - Security Considerations](https://datatracker.ietf.org/doc/html/rfc6749#section-10.4)

- The auth server must verify the binding between the client identity and refresh token whenever the user authenticates.
- Implement refresh token rotation. Issue a new refresh token each time a new access token is issued. The previous refresh token should be invalidated and retained. In the event the refresh token is compromised and used, the auth server can tell there was a breach.
- If the user changes their password or resets their password - invalidate all refresh tokens.
- On sign out, revoke all refresh tokens for that device.
- If a compromise is detected - when an invalidated token is reused - invalidate all refresh tokens, and prompt user the reauthenticate.
# Notes
- The access token should live for 15 minutes. The refresh token should live for 1 month.
- Refresh tokens TTL is 1 month. That is, we need to make sure the user reauthenticates at least once every 30 days, right? So we need to track so that new refresh tokens keep the issuance/expiry date of the previous one in mind. Or is this necessary?

example auth response
```json
{
    "access_token":"2YotnFZFEjr1zCsicMWpAA",
    "expires_in":3600,
    "token_type": "bearer",
    "refresh_token":"tGzv3JOkF0XG5Qx2TlKWIA",
    "refresh_token_expires_in": 36000
}
```

