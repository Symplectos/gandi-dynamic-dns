# Gandi Dynamic DNS
Python script to update DNS records managed by [Gandi](https://gandi.net). Useful for home servers with dynamic IP addresses.

Uses the [ipify API](https://www.ipify.org/) to get the public IPv4 and IPv6 addresses of the server running the script.
Each specified record in a specified domain is then updated, if, and only if, the A or AAAA record known by Gandi does not match the corresponding IP address returned by ipify.

## Installation
Installation is straightforward.

### Clone the Repository
```
git clone https://gitlab.com/Symplectos/gandi-dynamic-dns.git GandiDynamicDNS
```

### Create Python Environment
```
cd GandiDynamicDNS
python3 -m venv env
```

### Install Libraries
The script requires the **[requests](https://2.python-requests.org/en/master/)** library. All requirements can be
installed by invoking pip:

```
source bin/env/activate
pip install -r requirements
```

### Configuration
To configure the script, a **.do.conf** file must be created in the root folder of the project:

```
touch .do.conf
```

The configuration requires two sections, a **Gandi** section containing a valid API Access Key,
and a **DNS** section, containing the specific domain and specific records to update. Multiple records can be specified
by simply putting each record into a new line:

```
[Gandi]
key = ***

[DNS]
domain = myDomain.eu
records = sub1
          sub2
```

## Cronjob
To automatically run the script periodically, create a cronjob
```
crontab -e
```

```
*/5 * * * * cd /pathToFolder && /pathToFolder/env/bin/python3 /pathToFolder/gandiDynDNS.py
```

## Manual Run
To manually run the script, activate the environment and then invoke the Python interpreter.

### Activate the Environment
```
source env/bin/activate
```

### Run
```
python gandiDynDNS.py
```

## Logging
The script automatically logs its last run in the **gandiDynDNS.log** file.

<br />

---

# References
* [Gandi API](https://api.gandi.net/docs/livedns/)
* [ipify API](https://www.ipify.org/)

# Repositories

Main Repository on [GitLab](https://gitlab.com/Symplectos/gandi-dynamic-dns).

Push Mirrors:
* [Codeberg](https://codeberg.org/Symplectos/gandi-dynamic-dns) <3
* [GitHub](https://github.com/Symplectos/gandi-dynamic-dns)