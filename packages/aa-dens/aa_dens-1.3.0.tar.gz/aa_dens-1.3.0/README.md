# AA-Dens

*While this app should be functional bugs are expected.
Please report any of them in the issues or send me a PM on discord*

Alliance Auth applications to handle mercenary dens

[![release](https://img.shields.io/pypi/v/aa-dens?label=release)](https://pypi.org/project/aa-dens/)
[![python](https://img.shields.io/pypi/pyversions/aa-dens)](https://pypi.org/project/aa-dens/)
[![django](https://img.shields.io/pypi/djversions/aa-dens?label=django)](https://pypi.org/project/aa-dens/)
[![license](https://img.shields.io/badge/license-MIT-green)](https://gitlab.com/r0kym/aa-dens/-/blob/master/LICENSE)

## Features
- List mercenary dens
- Show other users mercenary dens depending on your roles
- Sends timers over to timberboard or structuretimers

### TODO
- [x] Notify user when a den is reinforced
  - [x] Have an AA notification
  - [x] Route notifications to discord if aa-discordbot is installed
- [ ] Kind of LP store on how to cash out den loots?

### Screenshots
TODO

## Installations

### Step 1 - Check prerequisites

aa-dens is a plugin for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth).
If you don't have Alliance Auth running already, please install it first before proceeding. (see the official [AA installation guide](https://allianceauth.readthedocs.io/en/latest/installation/auth/allianceauth/) for details). \
The minimal supported version of Alliance Auth is 4.6.0.

You will also need the [eveuniverse](https://gitlab.com/ErikKalkoken/django-eveuniverse) module to be properly installed.


### Step 2 - Install app

Make sure you are in the virtual environment (venv) of your Alliance Auth installation. Then install the newest release from PyPI:

```bash
pip install aa-dens
```

### Step 3 - Configure Auth settings

Configure your Auth settings (`local.py`) as follows:

- Add `'dens'` to `INSTALLED_APPS`
- Add below lines to your settings file:

```python
CELERYBEAT_SCHEDULE['dens_update_owners'] = {
    'task': 'dens.tasks.update_all_den_owners',
    'schedule': crontab(minute='0', hour='*/2'),
    'apply_offset': True,
}

CELERYBEAT_SCHEDULE['dens_update_notifications'] = {
    'task': 'dens.tasks.update_all_owners_notifications',
    'schedule': crontab(minute='*/10'),
    'apply_offset': True,
}

CELERYBEAT_SCHEDULE['dens_send_daily_analytics'] = {
  'task': 'dens.tasks.send_daily_analytics',
  'schedule': crontab(minute='0', hour='5')
}
```

For the `send_daily_analytics` task refer to [analytics](#analytics)

### Step 4 - Finalize App installation

Run migrations & copy static files:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

Restart your supervisor services for Auth.

## Analytics

This application will send anonymous analytic data using Alliance Auth built-in [analytics module](https://allianceauth.readthedocs.io/en/v4.3.1/features/core/analytics.html).
If you wish to disable the analytics for this application you can easily do so by removing the `metenox_send_daily_analytics` task.

The collected analytics are
- The number of den owners in your application
- The number of mercenary dens registered

## Permissions

Permissions overview.

| Name             | Description                                                |
|------------------|------------------------------------------------------------|
| basic_access     | Can access the application and add den owners              |
| corporation_view | Can view all dens anchored by members of their corporation |
| alliance_view    | Can view all dens anchored by members of their alliance    |
| manager          | Can view all dens regardless of affiliations               |

## Settings
List of settings that can be modified for the application.
You can alter them by adding them in your local.py file.

| Name                             | Description                                                                                     | Default |
|----------------------------------|-------------------------------------------------------------------------------------------------|---------|
| DENS_ADMIN_NOTIFICATIONS_ENABLED | Decides if admin should be notified about important events like new owners and disabled owners. | True    |


## Commands

The following commands can be used when running the module:

| Name                         | Description                                                        |
|------------------------------|--------------------------------------------------------------------|
| dens_update_owners.py        | Will check all mercenary den owners and update their in space dens |
| dens_update_notifications.py | Will check all den owners and update their notifications           |
