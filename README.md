# durhack-nginx-config

This repository tracks [nginx](https://nginx.org/en/) configuration files used for DurHack projects, both in development
and production. 

## Directory Structure
```text
.
├── production-deployer  
│   └── ...  # Python project installed on the DurHack VPS which auto-deploys production configuration files
├── development-sites-available
│   ├── ...  # contains development nginx configuration files
│   └── api.durhack-dev.com
├── production-sites-available
│   ├── ...  # contains production nginx configuration files 
│   └── api.durhack.com
├── production-sites-enabled
│   ├── ...  # contains symbolic links to files in production-sites-available
│   └── api.durhack.com -> ../production-sites-available/api.durhack.com
└── README.md
```

## As a developer, how do I use this repository?

1. If you are on Windows, [set up Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install)
   and ensure you are using the 'Ubuntu' terminal for all further steps.
2. **(Optional, Recommended)** Set up SSH public-key authentication for GitHub.
   1. As a preface, it's worth reading about [SSH (wikipedia)](https://en.wikipedia.org/wiki/Secure_Shell#Definition) 
      so you understand why you are doing this.
   2. first, [check for existing SSH keys on your machine](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/checking-for-existing-ssh-keys).
   3. next, [generate a new SSH key and add it to the ssh-agent](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent).
   4. finally, [add your new SSH key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).
3. Navigate using `cd` to someplace you are happy to keep the project, for example `~/Projects`
   ```bash
   $ cd ~  # change directory to your 'home' directory (usually /home/[username])
   ~$ mkdir -p Projects  # create the directory 'Projects' if it does not exist
   ~$ cd Projects  # change directory to 'Projects' inside your current working directory
   ~/Projects$
   ```
4. Check out the repository
   ```bash
   # If you set up SSH keys...
   ~/Projects$ git clone -- git@github.com:ducompsoc/durhack-nginx.git ./durhack-nginx  
   #               you can specify a different directory to clone into ^^^^^^^^^^^^^^^ 
   
   # If you didn't... 
   # generate a GitHub Personal Access Token with access to this repository:
   # https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
   #                    vvvvv replace <PAT> with your personal access token
   ~/Projects$ git clone -- https://<PAT>@github.com/ducompsoc/durhack-nginx.git ./durhack-nginx  
   #                         you can specify a different directory to clone into ^^^^^^^^^^^^^^^ 
   ```
5. Install [nginx](https://nginx.org/en/) using the [official installation instructions for Ubuntu](https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-open-source/#installing-prebuilt-ubuntu-packages).
   
   You can choose either method (i.e. 'from an ubuntu repository' vs. 'from the official NGINX repository'); the latter
   is slightly preferable, but the difference doesn't matter for contributing to DurHack projects.
6. Verify the nginx installation succeeded by querying the status of its `systemd` service:
   ```bash
   $ sudo systemctl status nginx
   🟢 nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; disabled; vendor preset: enabled)
     Active: active (running) since Mon 2024-10-07 12:29:36 BST; 11h ago
     ...
   ```
   Press `q` to exit the interactive `systemctl status` session.
   1. **(Optional)** Familiarise yourself with using `systemctl` to interact with `systemd` services more thoroughly
   2. `systemctl restart [service]`: fully re-start a service
   3. `systemctl reload [service]`: reload a service's configuration (not supported by all services; sometimes you have to `restart`)
   4. `systemctl stop [service]`: stop (deactivate) a service
   5. `systemctl start [service]`: start (activate) a service
   6. `systemctl enable [service]`: 'enable' a service - when enabled, a service will start when the computer turns on
   7. `systemctl disable [service]`: 'disable' a service
   8. `systemctl edit [service]`: edit the service definition's 'override' file; avoid making changes unless you know what you are doing!
   9. use `systemctl status nginx` again to verify that you left the nginx service **enabled** and **active**.
7. Navigate to nginx's configuration root and take a look around.
   ```bash
   $ cd /etc/nginx
   /etc/nginx$ ls
   conf.d  fastcgi.conf  fastcgi_params  koi-utf  koi-win  mime.types  modules-available  modules-enabled  nginx.conf  
   proxy_params  scgi_params  sites-available  sites-enabled  snippets  uwsgi_params  win-utf
   ```
   The relevant entries are 
     - `nginx.conf`: the 'root' config file, which invokes nginx's `include` directive to import other nginx config files.
     - `conf.d`: a directory containing configuration files. By convention, one file <-> one site; `nginx.conf` attempts 
       to `include` all files whose names end in `.conf` in this directory.
8. Create a symbolic link in the `conf.d` directory for each file in the `development-sites-available` folder
   of this repository
   ```bash
   /etc/nginx$ cd conf.d
   /etc/nginx/conf.d$ for file in /home/[username]/Projects/durhack-nginx/development-sites-available/*; do
       basename="${file/*\//}"
       sudo ln -s $file "./$basename.disabled"
   done
   /etc/nginx/conf.d$ ls
   ... '[api.durhack-dev.com].disabled'
   ```
9. Enable the sites you desire by renaming the links such that their filenames end in `.conf`
   ```bash
   /etc/nginx/sites-enabled$ sudo mv '[api.durhack-dev.com].disabled' '[api.durhack-dev.com].conf'
   /etc/nginx/sites-enabled$ ls
   ... '[api.durhack-dev.com].conf'
   ```
10. Ask nginx to reload its configuration (i.e. implement the changes you have specified)
   ```bash
   $ sudo systemctl reload nginx
   ```
11. Edit your `/etc/hosts` file to map `durhack-dev.com` domain names to local loopback addresses
   ```bash
   $ sudo nano /etc/hosts
   ```
   ```text
   # leave alone any entries that were present before you touched the file
   127.0.0.1       localhost
   ::1             localhost
   # ...
   
   # add entries for the project(s) you intend to work on
   127.0.0.1       durhack-dev.com api.durhack-dev.com
   ::1             durhack-dev.com api.durhack-dev.com
   
   127.0.0.1       live.durhack-dev.com
   ::1             live.durhack-dev.com
   
   127.0.0.1       megateams.durhack-dev.com
   ::1             megateams.durhack-dev.com
   
   127.0.0.1       jury.durhack-dev.com
   ::1             jury.durhack-dev.com  
   ```
   press `ctrl`+`x`, then `y`, then `enter` to save changes and exit.
   
12. Verify your changes by making an HTTP request:
   ```bash
   $ curl http://durhack-dev.com 
   <html>
   <head><title>502 Bad Gateway</title></head>
   <body>
   <center><h1>502 Bad Gateway</h1></center>
   <hr><center>nginx/1.18.0 (Ubuntu)</center>
   </body>
   </html>
   # 'bad gateway' is good! nginx is working as intended, but the corresponding project's server isn't running yet
   ```
13. Done! You have successfully installed nginx configurations for DurHack projects. Assuming you have also completed
    any project-specific setup, you should be ready to develop!

## Caveats / FAQs

**Q: Where's `development-sites-enabled`?**

**A:** `development-sites-enabled` is intentionally omitted. 
This makes sense - each developer should be able to choose which sites they wish to enable!  
`production-sites-enabled` exists as a simple method of controlling which production sites are deployed without 
deleting/recovering their configuration files.

**Q: What happens if an invalid production site configuration is automatically deployed?**

**A:** The nginx service running on the VPS will fail to reload (silently). The last 'valid' configuration should remain
active, though - so the deployer should continue to work, enabling fixes to be deployed automatically. 

**Q: What happens if the `deploy.durhack.com` site is disabled?**

**A:** The production configuration deployer will break. Someone technically minded will have 
to connect to the VPS using `ssh` and manually re-enable the site. 

**Q: The production site configurations appear to listen on port 80 and don't seem to set any SSL/TLS options. How is 
SSL/TLS configured to enable the use of `https` in production?**

**A:** The auto-deployer uses [certbot](https://certbot.eff.org/) to request certificates from [Let's Encrypt](https://letsencrypt.org/)
for the appropriate domain names and amend the production nginx configurations accordingly.
