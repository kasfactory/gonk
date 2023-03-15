# Gonk

![gonk](https://c.tenor.com/T0z4i7XQhUkAAAAd/gonk-gonk-droid.gif "Gonk")

## Setup

### Install the library:

```bash
pip install gonk
```

You can add contribution add-ons:

For Mercure support:

```shell
pip install gonk[mercure]
```

For Django Rest Framework support:

```shell
pip install gonk[drf]
```

Or both of them:

```shell
pip install gonk[drf,mercure]
```

### Add the application to `INSTALLED_APPS` in Django `settings`:

```python
INSTALLED_APPS = [
    # ...
    'gonk',
]
```

### Launch migrations:

```bash
python manage.py migrate
```

## Usage

### Create taskrunner

```python
# taskrunners.py
from gonk.taskrunners import TaskRunner
from gonk.decorators import register, register_beat
from celery.schedules import crontab


# Register taskrunner
@register('my_taskrunner')
class MyTaskRunner(TaskRunner):
    def revert(self):
        # Specific implementation
    
    def run(self):
        # Specific implementation


# Register scheduled taskrunner
@register_beat('scheduled_taskrunner', crontab(minute='*'))
class ScheduledTaskRunner(TaskRunner):
    def revert(self):
        # Specific implementation
    
    def run(self):
        # Specific implementation
```

We have to import the taskrunner within every app.
The best way to do so is in `apps.py`

```python
class MyAppConfig(AppConfig):
    # ...

    def ready(self):
        from . import taskrunners
```


### Launch task

```python
from gonk.tasks import Task

args = {}
Task.create_task('my_taskrunner', args)
```

### Revert task

```python
from gonk.tasks import Task

t = Task.objects.last()
t.revert()
```

### Cancel task

```python
from gonk.tasks import Task

t = Task.objects.last()
terminate: bool = False
t.cancel(terminate=terminate)
```

### Checkpoints

You can add checkpoints to register transcendent events within the task. Every checkpoint can send a notification
to the user to get feedback of the status and progress of the task.

```python
# taskrunners.py
from gonk.taskrunners import TaskRunner


class MyTaskRunner(TaskRunner):
    def run(self):
        # Specific implementation
        self.task.log_status('STARTED', checkpoint=False)
        self.task.log_status('Checkpoint 1', checkpoint=True)
        self.task.log_status('FINISHED')
```

### Command to list registered taskrunners

We can list the registered taskrunner with the command `list_taskrunners`.

```bash
python manage.py list_taskrunners
```

### Command to launch tasks manually

We can create tasks using the command `create_tasks`.

```bash
python manage.py create_task --help
usage: manage.py create_task [-h] [--input INPUT] [--raw-input RAW_INPUT] [--queue QUEUE] [--when WHEN] [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color]
                             [--skip-checks]
                             task_type

positional arguments:
  task_type             Task type identifier

options:
  -h, --help            show this help message and exit
  --input INPUT         File input -- can be redirected from standard output
  --raw-input RAW_INPUT
                        Raw string input -- Must be in json format
  --queue QUEUE         Celery queue name in which the task will be run
  --when WHEN           Scheduled task run date -- ISO Format

```

**Examples:**

```bash
python manage.py create_task <task_type> --raw-input='{}'
cat file.json | python manage.py create_task <task_type> --queue="celery" --input -
```

## Setup

| Environment variable | Type | Description |
| -------- |  ----------- | ----------- |
| KEEP_TASK_HISTORY_DAYS | int | Number of days to keep the tasks |
| DEFAULT_NOTIFICATION_EMAIL | str | Default e-mail to notify |

## Django Rest Framework

> To use Django Rest Framework extension we have to install with the `drf` extra. 

In our project `urls.py` we have to add the Gonk urls:

```python
from django.urls import path, include

urlpatterns = [
    # ...
    path('tasks/', include('gonk.contrib.rest_framework.urls')),
]
```

## Notifications with Mercure

> To use Mercure extension we have to install with the `mercure` extra. 


To send notifications with Mercure we have to setup the following environment variables:

| Variable | Type | Description |
| -------- |  ----------- | ----------- |
| MERCURE_HUB_URL | str | Mercure service URL |
| MERCURE_JWT_KEY | str | Mercure's JWT Token to publish events |

```python
# taskrunners.py
from gonk.taskrunners import TaskRunner
from gonk.contrib.notifications.mercure import MercureNotificationMixin


class MyTaskRunner(MercureNotificationMixin, TaskRunner):
    # Specific implementation

```

## Development

### Clone repository
```bash
git clone git@github.com:kasfactory/gonk.git && cd gonk
```

### Install poetry

```bash
pip install poetry
```

### Install dependencies

```bash
poetry install
```

### Run docker-compose

```bash
docker-compose up -d
```

### Launch celery worker

```bash
poetry run celery -A test_app worker
```

### Launch celery beat

```bash
poetry run celery -A test_app beat
```

> At this point, we have to ensure that `gonk.tasks.to_run`, `gonk.tasks.to_revert` and 
> `gonk.tasks.to_schedule` tasks are detected


## Credits

### Authors

- [Francisco Javier Lendínez](https://github.com/FJLendinez/)
- [Pablo Moreno](https://github.com/pablo-moreno/)

