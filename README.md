# accountability_project

# Follow:
more info on how to use Docker Files: 
https://app.clickup.com/2475352/docs/2bhar-988/2bhar-113


# Steps below unnecessary using docker files
## install environment
## python3 -m venv env || or windows python -m venv

## activate environment
### python3 env/bin/activate || deactivate for exit environment

## install packages
### pip3 install -r requirements.txt || or windows pip install -r

## Pending invite cleanup
Run `python manage.py cleanup_expired_invites` to delete `PendingInvite` rows where `accepted=False` and the invite expired more than 30 days ago. Accepted invites are never deleted.

Options:
- `--older-than-days N` retention window after expiry (default 30, `0` = everything already expired). The window keeps the "This invite has expired." message working for recently expired links.
- `--dry-run` preview the deletion count without deleting.

Scheduling: the `invite_cleanup` service in `docker-compose.yml` runs it every 24h. Outside Docker Compose, run it daily from your platform's scheduler, for example:
`0 3 * * * /path/to/python /path/to/manage.py cleanup_expired_invites`


