# durhack-deployer

## Current problems
- Celery is not suited to `async` operations
- Celery is not fit-for-purpose. it is really meant for handling a high volume of small messages. We have a small volume
  of larger messages.

### Ideas
- Use the filesystem as our queue instead of Celery; we can use a file-watcher to detect changes (additions to the queue)
  - i.e. a directory roughly corresponds to a 'queue'. the files within the directory are the queue entries
  - each queue entry can be named with an epoch timestamp such that lexicographic ordering should yield the correct order
    of events
- Each queue worker can run on an `asyncio` event loop
  - 1 worker+queue that handles all GitHub events and forwards them to the appropriate queue, or voids them if
  - 1 worker+queue per repository deployment (i.e. `durhack` and `durhack-staging` should be distinct)
- Use [redis-lock](https://github.com/miintto/redis-lock-py) where inter-process locking is necessary
- Use PM2 to manage the Flask app & worker python processes

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
- To facilitate 'locking' inter-process shared resource to prevent concurrent access, we want an in-memory database.
  Joe chose [dragonfly](https://www.dragonflydb.io), which is "a drop-in Redis replacement".
  - [copy the download link for a dragonfly executable archive](https://github.com/dragonflydb/dragonfly/releases) (usually, `x86-64.tar.gz`)
  - `sudo mkdir /opt/dragonfly/ && cd /opt/dragonfly` - create `/opt/dragonfly` and `cd` into it
  - `sudo wget [paste link]` - download the archive you copied the link for
  - `sudo mkdir ./dragonfly-v1.23.2` - create a directory for the version you downloaded (get version number from GitHub)
  - `sudo tar -xf dragonfly-x86_64.tar.gz -C ./dragonfly-v1.23.2` - unpack the archive into the directory you created
  - `sudo rm dragonfly-x84_64.tar.gz` - remove the archive as we don't need it anymore
  - `sudo ln -s ./dragonfly-v1.23.2 ./dragonfly-current` - create a symlink `dragonfly-current` which points to `dragonfly-v1.23.2`
  - `sudo ln -s /opt/dragonfly/dragonfly-current/dragonfly-x86_64 /usr/local/bin/dragonfly` - create a symlink `dragonfly` in `/usr/local/bin`
    which points to the binary `dragonfly-x84_64` in `/opt/dragonfly/dragonfly-current`
  - `dragonfly --help` to test that dragonfly has successfully been installed
  - `sudo apt install redis-tools` so we can use `redis-cli` as a database client for dragonfly
  - Create a new user `dragonfly` with homedir `/var/lib/dragonfly`
    - `sudo adduser dragonfly --group --system --disabled-password --home /var/lib/dragonfly --shell /bin/bash`
    - `cd /var/lib && sudo chmod o+rx dragonfly` - to others (`o`), add (`+`) read (`r`) and execute (`x`) perms on
      dragonfly's home directory
  - Create a service file at `/etc/systemd/system/dragonfly.service`:
    ```
    [Unit]
    Description=Dragonfly In-Memory Data Store
    After=network.target

    [Service]
    User=dragonfly
    Group=dragonfly
    ExecStart=/usr/local/bin/dragonfly --dir /var/lib/dragonfly
    ExecStop=/usr/bin/redis-cli shutdown
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
  - `sudo systemctl daemon-reload` so that `systemd` will check for new service units,
  - `sudo systemctl start dragonfly` to start dragonfly as a daemon (background process)
- About the `durhack-deployer` user
  - **Q: Why don't we just use `root`?**
    **A:** anything that does not need to run as `root`, should not run as `root`.
    Setting up fine-grained access control protects us from ourselves **and** malicious actors.
  - That said, permissions are going to be tricky ...
    - the user needs to be able to run the `certbot` CLI (which requires `root` privileges)
    - the user needs to be able to run `systemctl reload nginx` as `root` (but not any other `systemctl` commands)
    - the user needs to be able to read from/write to the `/etc/nginx/conf.d` directory

    We will have to make use of a few systems to satisfy all constraints.
  - Create the user.
    ```bash
    sudo adduser durhack-deployer --group --system --disabled-password --home /var/www/durhack-deployer --shell /bin/bash
    ```
    - `--group`: also create a group with the same name as the user, and add the user to it
    - `--system`: create a system user (a user with 'account expiry: never', and a `uid` < 999)
    - `--disabled-password`: do not set a password, but still permit login (for example via `sudo -u` or SSH)
    - `--home ...`: set the home directory (`$HOME`, `~`) for the user to `...`
    - `--shell ...`: set the path to the executable used when creating shells for the user (could be `/bin/zsh` etc.)
  - We create a file in `/etc/sudoers.d` which will be included by `/etc/sudoers`.
    ```bash
    $ cd /etc/sudoers.d
    /etc/sudoers.d$ sudo touch durhack-deployer`
    ```
  - Add a directive granting `durhack-deployer` access to `certbot`
    ```bash
    /etc/sudoers.d$ sudo bash -c "cat >> durhack-deployer"
    # allow `durhack-deployer` to run `certbot` as `root` without a password and with arbitrary arguments
    durhack-deployer ALL=(ALL) NOPASSWD: /usr/bin/certbot
    ^C
    ```
  - Add a directive granting `durhack-deployer` access to `systemctl reload nginx`
    ```bash
    /etc/sudoers.d$ sudo bash -c "cat >> durhack-deployer"
    # allow `durhack-deployer` to run `systemctl` as `root` without a password and only with the exact arguments `reload nginx`
    durhack-deployer ALL=(ALL) NOPASSWD: /usr/bin/systemctl reload nginx
    ^C
    ```
  - We edit the file access control list (FACL) of `/etc/nginx/conf.d` to permit `durhack-deployer` to
    read from/write to its files.
    ```bash
    $ sudo apt install acl -y
    ...
    $ cd /etc/nginx
    /etc/nginx$ # modify the default ACL for the directory (only affects newly created files)
    /etc/nginx$ sudo setfacl --default -m user:durhack-deployer:rw conf.d
    /etc/nginx$ # modify the ACL of existing files
    /etc/nginx$ sudo setfacl -R -m user:durhack-deployer:rw conf.d
    /etc/nginx$ # modify the ACL of the directory to allow execution (necessary for creation/deletion of files within the directory)
    /etc/nginx$ sudo setfacl -m user:durhack-deployer:rwx conf.d
    ```
  - We are done! `sudo -u durhack-deployer -i` to start a login shell as `durhack-deployer`, `ctrl`+`D` to logout.
