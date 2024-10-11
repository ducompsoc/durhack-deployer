# durhack-nginx/production-deployer

## Stack/Tooling 
- Most dependencies are explained by comments in `Pipfile`
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
  it is commonly used with Flask.
- Celery requires a memory transport to send and receive messages; Joe chose to use the Redis broker transport implementation
  backed by [dragonflydb](https://www.dragonflydb.io)
  - dragonfly is installed by [downloading its executable](https://www.dragonflydb.io/docs/getting-started/binary)
    and placing it at `/usr/local/bin/dragonfly`
  - dragonfly does not come with a database client; `sudo apt install redis-tools` then use `redis-cli`
  - a new user `dragonfly` should be created with homedir `/var/lib/dragonfly`
    - `sudo adduser dragonfly --group --system --disabled-password --home /var/lib/dragonfly --shell /bin/bash`
    - `cd /var/lib && sudo chmod o+rx dragonfly` to enable read and execute perms to 'others' on dragonfly homedir
  - dragonfly does not install itself as a systemd service; create a service file at 
    `/etc/systemd/system/dragonfly.service`:
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
    then `sudo systemctl daemon-reload` so that `systemd` will check for new service units  
    then `sudo systemctl start dragonfly`  
