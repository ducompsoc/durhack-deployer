# durhack-nginx/production-deployer

## Stack/Tooling
- Most dependencies are explained by comments in `Pipfile`, which is analogous to `package.json` in a JavaScript project.
  The program that interacts with / restores environment using the `Pipfile` is [pipenv](https://pipenv.pypa.io/en/latest/)
- The main HTTP server is a [Flask](https://flask.palletsprojects.com/en/3.0.x/) application listening on port `3400`
  - Flask implements the [WSGI](https://wsgi.readthedocs.io/en/latest/what.html)
  - This means that in production, you shouldn't just use the Flask development server.
    You should choose a WSGI server ([options](https://flask.palletsprojects.com/en/3.0.x/deploying/))
    and use that to run your WSGI (Flask) application.
  - Joe chose [uWSGI](https://flask.palletsprojects.com/en/3.0.x/deploying/uwsgi/) because they had documentation
    on managing their server/your apps [using a `systemd` service](https://uwsgi-docs.readthedocs.io/en/latest/Systemd.html)
- The application needs to persist some information (specifically, GitHub event IDs of previously processed events)
  - it uses [sqlalchemy](https://www.sqlalchemy.org/), a Python ORM, to access a postgres database
  - it uses [alembic](https://alembic.sqlalchemy.org/en/latest/), a database migration tool, to manage changes to
    the database (hopefully) without losing access to data
- The application employs a task queue to ensure it can respond to webhook requests in a timely manner.
  Joe chose [celery](https://docs.celeryq.dev/en/main/getting-started/introduction.html) for its popularity & because
  it is commonly used with Flask. Celery consists of
  - a message broker to send and receive messages (bring your own, look ahead for Joe's choice)
  - the celery client (a Python library), which enables enqueueing tasks to the broker and registering task handlers to
    be invoked by the broker
  - the celery worker (a command-line app which invokes Python functions registered by the celery client in order to
    handle queued tasks)
- For Celery's message broker, Joe chose to use [RabbitMQ](https://www.rabbitmq.com/) for its popularity and
  redundancy (unprocessed tasks persist through loss of power, etc.)
  - `lsb_release -a` to check your Ubuntu version
  - [Install RabbitMQ](https://www.rabbitmq.com/docs/install-debian#apt-cloudsmith) for your Ubuntu version
  - [Configure RabbitMQ for Celery](https://docs.celeryq.dev/en/latest/getting-started/backends-and-brokers/rabbitmq.html)
    - `sudo rabbitmqctl add_user durhack-nginx-deployer [password]`
    - `sudo rabbitmqctl add_vhost durhack-nginx-deployer`
    - `sudo rabbitmqctl set_permissions -p durhack-nginx-deployer durhack-nginx-deployer ".*" ".*" ".*"`
    - Override the `celery_task_broker_uri` from `config/default.toml` with the appropriate value by adding an entry to
      `config/local.toml`
- The celery worker is a long-running program we wish to run in the background, so we 'daemonize' it (configure an
  init-system to manage it for us)
  - Create a `systemd` service file (at `/etc/systemd/system/durhack-nginx-deployer-worker.service`). It
    should look a bit like this:
    ```ini
    [Unit]
    Description=Celery task queue worker for durhack-nginx-deployer
    After=network.target rabbitmq-server.service
    Requires=rabbitmq-server.service

    [Service]
    Type=forking
    User=durhack-nginx-deployer
    Group=durhack-nginx-deployer
    WorkingDirectory=/var/www/durhack-nginx/production-deployer
    ExecStart=/bin/bash -c "./scripts/start-worker.sh"
    ExecStop=/bin/bash -c "./scripts/stop-worker.sh"
    ExecReload=/bin/bash -c "./scripts/reload-worker.sh"
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
    Make sure you amend the `WorkingDirectory` option appropriately. Notes on creating the `durhack-nginx-deployer` user
    are further on.
- About the `durhack-nginx-deployer` user
  - **Q: Why don't we just use `root`?**
    **A:** running a celery worker as `root` is [ill-advised](https://docs.celeryq.dev/en/main/userguide/daemonizing.html#running-the-worker-with-superuser-privileges-root)
    as celery can theoretically execute arbitrary code.
  - That said, permissions are going to be tricky ...
    - the user needs to be able to run the `certbot` CLI (which requires `root` privileges)
    - the user needs to be able to run `systemctl reload nginx` as `root` (but not any other `systemctl` commands)
    - the user needs to be able to read from/write to the `/etc/nginx/conf.d` directory

    We will have to make use of a few systems to satisfy all constraints.
  - Create the user.
    ```bash
    sudo adduser durhack-nginx-deployer --group --system --disabled-password --home /var/www/durhack-nginx/production-deployer --shell /bin/bash
    ```
    - `--group`: also create a group with the same name as the user, and add the user to it
    - `--system`: create a system user (a user with 'account expiry: never', and a `uid` < 999)
    - `--disabled-password`: do not set a password, but still permit login (for example via `sudo -u` or SSH)
    - `--home ...`: set the home directory (`$HOME`, `~`) for the user to `...`
    - `--shell ...`: set the path to the executable used when creating shells for the user (could be `/bin/zsh` etc.)
  - We create a file in `/etc/sudoers.d` which will be included by `/etc/sudoers`.
    ```bash
    $ cd /etc/sudoers.d
    /etc/sudoers.d$ sudo touch durhack-nginx-deployer`
    ```
  - Add a directive granting `durhack-nginx-deployer` access to `certbot`
    ```bash
    /etc/sudoers.d$ sudo bash -c "cat >> durhack-nginx-deployer"
    # allow `durhack-nginx-deployer` to run `certbot` as `root` without a password and with arbitrary arguments
    durhack-nginx-deployer ALL=(ALL) NOPASSWD: /usr/bin/certbot
    ^C
    ```
  - Add a directive granting `durhack-nginx-deployer` access to `systemctl reload nginx`
    ```bash
    /etc/sudoers.d$ sudo bash -c "cat >> durhack-nginx-deployer"
    # allow `durhack-nginx-deployer` to run `systemctl` as `root` without a password and only with the exact arguments `reload nginx`
    durhack-nginx-deployer ALL=(ALL) NOPASSWD: /usr/bin/systemctl reload nginx
    ^C
    ```
  - We edit the file access control list (FACL) of `/etc/nginx/conf.d` to permit `durhack-nginx-deployer` to
    read from/write to its files.
    ```bash
    $ sudo apt install acl -y
    ...
    $ cd /etc/nginx
    /etc/nginx$ # modify the default ACL for the directory (only affects newly created files)
    /etc/nginx$ sudo setfacl --default -m user:durhack-nginx-deployer:rw conf.d
    /etc/nginx$ # modify the ACL of existing files
    /etc/nginx$ sudo setfacl -R -m user:durhack-nginx-deployer:rw conf.d
    /etc/nginx$ # modify the ACL of the directory to allow execution (necessary for creation/deletion of files within the directory)
    /etc/nginx$ sudo setfacl -m user:durhack-nginx-deployer:rwx conf.d
    ```
  - We are done! `sudo -u durhack-nginx-deployer -i` to start a login shell as `durhack-nginx-deployer`, `ctrl`+`D` to logout.
