# Retiring an agent — checklist

<!-- Copy into the active checklist when an agent is retired. Each line is verified, not assumed. -->

- [ ] Scheduled jobs removed from every profile (list them first; updates can duplicate jobs elsewhere)
- [ ] Gateway / service stopped and disabled; autostart entries removed
- [ ] Channels closed: bot tokens revoked, webhooks removed, bridges stopped
- [ ] Keys revoked or rotated; profile-local secrets deleted
- [ ] Data decided: archived (where, until when) or deleted; copies of personal data removed
- [ ] Lessons generalized into docs/KNOWN_ERRORS.md; specifics that would tempt a restore removed
- [ ] Card moved to docs/archive/ with the retirement date and reason; system overview updated
- [ ] One week later: no job ran, no key was used, no message was sent in its name
