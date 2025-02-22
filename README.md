# durhack-deployer

## Stack/Tooling
- Most dependencies are explained by comments in `Pipfile`, which is analogous to `package.json` in a JavaScript project.
  The program that interacts with / restores environment using the `Pipfile` is [pipenv](https://pipenv.pypa.io/en/latest/)
- The main HTTP server is a [Flask](https://flask.palletsprojects.com/en/3.0.x/) application listening on port `3400`
  - Flask implements the [WSGI](https://wsgi.readthedocs.io/en/latest/what.html)
  - This means that in production, you shouldn't just use the Flask development server.
    You should choose a WSGI server ([options](https://flask.palletsprojects.com/en/3.0.x/deploying/))
    and use that to run your WSGI (Flask) application.
  - Joe chose [uWSGI](https://flask.palletsprojects.com/en/3.0.x/deploying/uwsgi/) because they had documentation on managing their server/your apps
    [using a `systemd` service](https://uwsgi-docs.readthedocs.io/en/latest/Systemd.html)
- The application needs to persist some information (specifically, GitHub event IDs of previously processed events)
  - it uses [sqlalchemy](https://www.sqlalchemy.org/), a Python ORM, to access a postgres database
  - it uses [alembic](https://alembic.sqlalchemy.org/en/latest/), a database migration tool, to manage changes to
    the database without data loss (hopefully)
- The application uses a file-system based 'queue' to allow it to respond quickly to GitHub when new events are delivered,
  despite those events triggering long-running webhook handlers.
  - a 'queue directory' is a directory whose files are queue entries.
  - To add an entry to the queue, a JSON file is created in the queue directory.
    Ideally, these files should be named such that their names in lexicographic order matches the order in which they
    were created.
    Presently, this rule is followed by using the [Epoch timetamp](https://www.epochconverter.com/) (at nanosecond resolution)
    of the instant preceding the file's creation (plus the `.json` file extension) as the file's name.
  - a 'queue worker' is a program which uses a file watcher to listen for changes to a queue directory, runs
    some task for entries added to the queue in turn, and removes queue entries (deletes their file) once the task
    is complete.
  - the `<repository>/queues` directory contains all the queue directories.
  - all webhook events from GitHub are placed into the `main` queue for processing by the 'main queue worker'.
  - the 'main queue worker' processes events by 'forwarding' them to the appropriate 'deployment queue' if the
    event matches a configured deployment, or voids the event otherwise.
  - each 'deployment queue worker' processes events in their queue by running a routine specific to the deployment's
    repository.
    These repository-specific routines are responsible for checking out new changes and performing build/deployment
    steps, e.g. running `pnpm build`.
- About the `durhack-deployer` user
  - **Q: Why don't we just use `root`?**
    **A:** anything that does not need to run as `root`, should not run as `root`.
    Setting up fine-grained access control protects us from ourselves **and** malicious actors.
  - That said, permissions are going to be tricky ...
    - the user needs to be able to run the `certbot` CLI (which requires `root` privileges)
    - the user needs to be able to run `systemctl reload nginx` as `root` (but not any other `systemctl` commands)
    - the user needs to be able to read from/write to the `/etc/nginx/conf.d` directory

    We will have to make use of a few systems to satisfy all constraints.
  - Create the user (and group):
    ```bash
    sudo adduser durhack-deployer --disabled-password --home /home/durhack-deployer
    ```
    - `--disabled-password`: do not set a password, but still permit login (for example via `sudo -u` or SSH)
    - `--home home`: set the home directory (`$HOME`, `~`) for the user to `home`

    (you can leave all the user information fields blank, just keep pressing `Enter` until 'Is the information correct?')
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
