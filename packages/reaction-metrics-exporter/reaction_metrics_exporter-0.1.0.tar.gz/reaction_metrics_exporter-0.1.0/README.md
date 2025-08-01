
<!-- TOC ignore:true -->
# reaction-metrics-exporter

> [!note] 💚 A lot of inspiration has been drawn from [`dmarc-metrics-exporter`](https://github.com/jgosmann/dmarc-metrics-exporter).

Export [OpenMetrics](https://prometheus.io/docs/specs/om/open_metrics_spec/) for [reaction](https://reaction.ppom.me/). The exporter continuously monitors and parses reaction's logs and state. 

The following metrics are collected and exposed through an HTTP endpoint:

- `reaction_match_total`: total number of matches;
- `reaction_action_total`: total number of actions;
- `reaction_pending_count`: current number of pending actions.

All metrics are labelled with `stream` and `filter`. Action-related metrics have an additional `action` label.

<!-- TOC ignore:true -->
## Table of contents

<!-- TOC -->

- [Quick start](#quick-start)
- [The matches dilemma](#the-matches-dilemma)
- [Usage details](#usage-details)
- [Real-world setup](#real-world-setup)
- [Visualising data](#visualising-data)
- [Development setup](#development-setup)

<!-- /TOC -->

# Quick start

> [!caution] ⚠️ Do not use in production; see [real-world setup](#real-world-setup).

## Prerequisites

- `python>=3.10` and `pip`;
- `reaction==2` (tested up to `v2.1.2`);
- [`libsystemd`](https://www.freedesktop.org/software/systemd/man/latest/libsystemd.html);
- [`pkg-config`](https://www.freedesktop.org/wiki/Software/pkg-config/).

## Install

```bash
python3 -m pip install reaction-metrics-exporter
```

It is recommended to install the exporter in a [virtualenv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).

## Configure

Create a configuration file, *e.g.* `config.yml`:

```yaml
metrics:
  # export all possible metrics
  export:
    matches:
    actions:
    pending:

reaction:
  # as you would pass to `reaction test-config`
  config: /etc/reaction
  logs:
    # monitor logs for `reaction.service`
    systemd:

persist:
  # save metrics from time to time
  folder: ~/.local/share/reaction-metrics-exporter
```

>>> [!tip] Using a log file ?
```yaml
reaction:
  # ...
  logs:
    # replace with you log path
    file: /var/log/reaction.log
```
>>>

## Run

```bash
python3 -m reaction_metrics_exporter -c /etc/reaction-metrics-exporter/config.yml start
```

Metrics are exposed at http://localhost:8080/metrics.

> [!note] 💡 Metrics are written on disk on exit and reloaded on subsequent starts.

# The matches dilemma

`reaction` matches often contains valuable information, such as IP addresses. Exporting them as metrics' labels is kind of hackish; they should in theory be sent to a log database, but these are heavy and less common. The default configuration is conservative and **do not export them**.

## How matches can become a problem

Quoting the [Prometheus docs](https://prometheus.io/docs/practices/naming/):

> CAUTION: Remember that every unique combination of key-value label pairs represents a new time series, which can dramatically increase the amount of data stored. Do not use labels to store dimensions with high cardinality (many different label values), such as user IDs, email addresses, or other unbounded sets of values.

For example, metrics exported from [the SSH filter](https://reaction.ppom.me/filters/ssh.html) look like:

```
reaction_matches_total{stream="ssh",filter="failedlogin",ip="X.X.X.X"}: N
```

`N` being the number of matches for this unique combination of labels.

> ⚠️ Each new IP address will therefore create a new line in the exported data **and** a new time serie in the TSDB. For large instance, this can result in storage and performance issues.

## Choosing exported matches

You need to explicitly specify which patterns you want to export.

For example, to export `ip` matches of the `failedlogin` filter from the `openssh` stream:

```yaml
metrics:
  for:
    ssh:
      failedlogin:
        ip:
```

If you use the pattern `ip` in multiple streams, you can avoid repetition by exporting it globally:

```yaml
metrics:
  all:
    ip:
```

## Pre-treating matches

In some cases, you may want to transform matches prior to exporting. You can do so with [Jinja2](https://jinja.palletsprojects.com/en/stable/) expressions.

For example, for an `email` pattern, you could to keep only the domain part in metrics: first to reduce cardinality, second to avoid storing too much personal data in the TSDB. This can be achieve with:

```yaml
metrics:
  all:
    email: "{{ email.split('@') | last }}
```

## Tweaking metrics

To delete a metric from exports, simply remove the corresponding key in the configuration. You can alternatively disable matches export for individual metrics as these are essentially redundant.

To include meta-metrics (Python, GC, CPU...), add the `internals` key.

In this example...

```yaml
metrics:
  export:
    matches:
      labels: false
    actions:
    internals:
```

- matches will be exported with limited labels (stream and filters);
- actions will be exported with all matches;
- pending actions will **not** be exported;
- meta-metrics will be exported.

## Automatically forgetting metrics

You can configure the exporter to forget metrics periodically:

```yaml
persist:
  # you can use any number followed by M (minutes), H (hours), d (days),
  # w (weeks), m (months) or y (years) 
  forget: 1m
```

This approach has a drawback: any plot relying on the absolute values of counters will reset. In practice, such plots are rare and `rate` or `increase`-like functions are used instead. Fortunately, these ignore breaks in monotonicity.

Besides, it is possible to approximate counters as if they hadn't been reset using VictoriaMetrics: see the [visualization section](#visualization).

> 🕧 The duration depends on your setup. Start without `forget` and monitor the size of the HTTP response and the size of your TSDB.

> [!tip] 💡 A backup file is created before forgetting.

# Usage details

## Configuration

You can either provide a YAML file or a JSON file. Albeit not recommended, you can run the exporter without a configuration file.

The default configuration looks like this:

```json5
{
    // only stdout is supported atm
    "loglevel": "INFO",
    "listen": {
        "port": 8080,
        "address": "127.0.0.1"
    },
    "metrics": {
        "all": {},
        // ⚠️ no metrics exported by default!
        "export": {},
        "for": {}
    },
    "reaction": {
        "config": "/etc/reaction",
        "logs": {
            "systemd": "reaction.service"
        },
        // same default as reaction
        "socket": "/run/reaction/reaction.sock"
    },
    "persist": {
        // in seconds (e.g. 10 minutes)
        "interval": 600,
        "folder": "/var/lib/reaction-metrics-exporter",
        // never-ish
        "forget": "10y"
    }
}
```

## Ingesting existing logs

You may want to calculate metrics from existing logs. Whilst possible, there are several limitations:

- the exporter **needs the configuration to be aligned with the logs**, especially for stream, filters and patterns.
- any previously exported metrics **will be erased** to avoid duplication.

The following command reads all known logs, calculate metrics, saves them and exits.

```bash
python3 -m reaction_metrics_exporter -c config.yml init
```

You can then launch the usual command (`start`).

> 👉 Use this command if something has gone wrong with your metrics (*hopefully not*) and that you have kept the logs.

## Commands

```
usage: python -m reaction_metrics_exporter [-h] [-c CONFIG] [-f] [-y] {init,start,clear,defaults,test-config}

positional arguments:
  {init,start,clear,defaults,test-config}
                        mode of operation; see below

options:
  -h, --help            show this help message and exit
  -c, --config CONFIG   path to the configuration file (JSON or YAML)
  -f, --force           force clear even if backup is impossible, then delete backup
  -y, --yes             disable interaction. caution with init and clear

command:
    init: read all existing logs, compute metrics, save on disk and exit
    start: continuously read **new** logs, compute and save metrics; serve HTTP endpoint
    clear: make a backup and delete all existing metrics (-f to force)
    defaults: print the default configuration in json
    test-config: validate and output configuration in json
```

# Real-world setup

## Create an unprivileged user

The exporter should run with an unprivileged, system user. Among numerous reasons:
- the exporter is exposed on the web;
- it parses arbitrary data;
- it has a lot of dependencies;
- I am neither a developer nor a security expert.

This user should be able to read [journald](https://www.freedesktop.org/software/systemd/man/latest/systemd-journald.service.html) logs and to communicate with `reaction`'s socket.

First create a user and a group, then add the user to the `systemd-journal` group.

```bash
# creates group automatically
/sbin/adduser exporter-reaction --no-create-home --system
usermod -aG systemd-journal exporter-reaction
```

Then, open an editor to modify `reaction`'s service:

```bash
systemctl edit reaction.service
```

Paste the following under the `[Service]` section:

```systemd
# Files (inc. socket) created by reaction will be owned by this group
Group=reaction-metrics-exporter
# Files (default /run/reaction) will be writable by the group
RuntimeDirectoryMode=0775
```

Restart reaction:

```bash
systemctl daemon-reload
systemctl restart reaction
```

Check that you should be able to communicate with `reaction` and to read the journal as the user.

```bash
sudo su reaction-metrics-exporter
reaction show
journalctl -feu reaction
```

## Running with systemd

A [service file](./reaction-metrics-exporter.service) file is provided: save it to `/etc/systemd/systemd`.

You may need to adjust the configuration path in the `ExecStart=` directive. 

> 💡 Persistence directory is created automatically by systemd in `/var/lib`.

Enable and start the exporter:

```bash
systemctl daemon-reload
systemctl enable --now reaction-metrics-exporter.service
```

Follow the logs with:

```bash
journalctl -feu reaction-metrics-exporter.service
```

## Running with Docker

> [!caution] ⬆️ Make sure you completed the [rootless setup](#create-an-unprivileged-user).

Start inside the [docker](./docker) directory. 

Create a `.env` file:

```ini
UID=
GID=
JOURNAL_GID=
```

Values can be found out of command `id exporter-reaction`.

You may need to adjust the default mounts in [`compose.yml`](./docker/compose.yml). Expectations are:
- `reaction`'s configuration mounted on `/etc/reaction`;
- `reaction`'s socket mounted on `/run/reaction/reaction.sock`;
- `journald` file mounted on `/var/log/journal`.

A [sample configuration file](./docker/config.yml) is provided. Tweak it to fit your needs.

If you want to [`init`](#ingesting-previous-logs):

```bash
docker compose up rme-init
```

To start exposing metrics:

```bash
docker compose up -d rme && docker compose logs -f
```

The exporter is mapped to the host's `8081` port by default.

>>> [!tip] Optionally, you can build the image yourself:
```bash
docker compose build
```
>>>

# Visualising data

🚧 WIP !

# Development setup

In addition of the prerequisites, you need [Poetry](https://python-poetry.org/).

```bash
# inside the cloned repository
poetry install
# run app
poetry run python -m reaction_metrics_exporter [...]
# run tests
poetry run pytest
```