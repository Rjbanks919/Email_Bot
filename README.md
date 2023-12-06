# Self-Hosted Email Bot 🤖
Self-hosted "bot" to receive email commands and respond with data!

## Why?

I wanted a way to access information (such as a snapshot of my home's security
cameras) when all I have is an email connection. Thus, I created this project
which establishes a simple systemd service to poll for emails and respond with
data!

## Getting Started

In order to use this project you will need:

1. A Linux server that uses systemd
2. A [GMail](https://mail.google.com) account for the bot
3. A [Google Cloud](https://console.cloud.google.com) project and OAuth 2.0
   client credentials
4. Some data to return

**Number 3** is especially important, as it is what will allow us to read,
modify, and create emails on the behalf of the email from **number 2**. Once
you have created your credential file, save it as `credentials.json`.

### PyPI Packages

There are a few PyPI packages that you'll need to install to run the `bot.py`
script. Install them with:

```bash
$ python3 -m pip install \
    google-auth \
    google-auth-oauthlib \
    google-auth-httplib2 \
    google-api-python-client \
    requests
```

### Authenticating with Google

To create the systemd service, we need to setup the required files first.

```bash
$ mkdir /opt/Email_Bot/
$ cp bot.py credentials.json email_bot.service /opt/Email_Bot/
```

At this point, you will need to run the Python script for the first time in
order to authenticate with Google and get a `token.json` file. This file will
be used to authenticate the script in the future.

```bash
$ cd /opt/Email_Bot/
$ python3 bot.py

# Login and whatnot, verify token.json was created after
```

### Adding the special sauce

For my application, I simply wanted to send off snapshots from my RTSP security
cameras along with some other small info.

For your application, you might want different information packed in. To add
stuff...

```
ADD MORE INFO HERE RYAN
```

### Setting up the systemd service

With our `token.json` ready to go, our script is ready to be used by a service.

Modify the provided `bot_email.service` file and replace `<YOUR_USER_HERE>`
with the desired user to run the service as.

```
User=myUser
```

Now, place the service with the other systemd services and enable/start it!

```bash
$ cp email_bot.service /etc/systemd/system/
$ systemctl enable email_bot
$ systemctl start email_bot
```

From here, you can verify that things are working as expected by checking the
service status.

```bash
$ systemctl status email_bot
email_bot.service - Self Hosted Email Bot Service
     Loaded: loaded (/etc/systemd/system/email_bot.service; enabled; vendor preset: enabled)
     Active: activating (auto-restart) since Wed 2023-12-06 00:12:06 UTC; 33s ago
    Process: 3734141 ExecStart=/usr/bin/python3 /opt/Email_Bot/bot.py (code=exited, status=0/SUCCESS)
   Main PID: 3734141 (code=exited, status=0/SUCCESS)
        CPU: 327ms
```

As you can see it is loaded, and is restarting automatically every 60 seconds.
With this setup, any new email will be handled when the inbox is polled every
minute. You can adjust this timing as desired.
