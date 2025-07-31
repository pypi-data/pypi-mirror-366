# Perun proxy utils

Scripts and monitoring probes related to Perun ProxyIdP.

## Installation

Install via pip:

```sh
pip install perun.proxy.utils
```

There are several extras which are required only for some scripts:

- `[ldap]` for check_ldap and check_ldap_syncrepl
  - this also requires
    installing [build prerequisites of the python-ldap library](https://www.python-ldap.org/en/latest/installing.html#build-prerequisites)
- `[postgresql]` for check_pgsql and oracle2postgresql
- `[oracle]` for oracle2postgresql

## Scripts

### run_probes

- script designed to execute multiple monitoring probes
- output is compatible with CheckMK
- it is required to put configuration file to `/etc/run_probes_cfg.yaml`
- default timeout in seconds for all checks is set by `default_timeout` in the config, and each check can optionally have its own `timeout` setting overriding the default one.


For usage instructions, run:

```sh
run_probes
```

### separate_ssp_logs

Script removes all logs from test accounts from SimpleSAMLphp logs.

For usage instructions, run:

```sh
separate_ssp_logs.py --help
```

### separate_oidc_logs

Script removes all logs from test accounts from mitreID logs.

For usage instructions, run:

```sh
separate_oidc_logs.py --help
```

### metadata_expiration

This script checks whether there are some metadata close to expiration date.

For usage instructions, run:

```sh
metadata_expiration.py --help
```

### print_docker_versions

This script collects system info, docker engine info and the versions of running
containers and then prints it to the stdout in the JSON format.

For usage instructions, run:

```sh
print_docker_versions --help
```

### run_version_script

- This scripts runs the print_docker_versions script on the given machines. The
  collected versions are then printed as a MD table to the stdout

For usage instructions, run:

```sh
run_version_script --help
```

### sync_usable_token_types.py

Collects information about the usable token types of each privacyIDEA user and sends it
to Perun. Each user with usable tokens in privacyIDEA is assigned a list of their types,
for example: `['backupcode', 'totp']`. A token is considered usable when it is **active
** and it is not **locked** or
**revoked** and its rollout state allows logging in.

Requires configuration
of [perun connector](https://gitlab.ics.muni.cz/perun/perun-proxyidp/perun-connector)
module to work properly. It also needs to be executed in the same environment as
privacyIDEA to acquire its Flask context (e.g. inside privacyIDEA docker container).

For more usage instructions, run:

```sh
sync_usable_token_types --help
```

Example:

```sh
python3 sync_usable_token_types.py
    --mfa-active-tokens-attr-name "attr_name"
    --perun-user-id-regex "\d+"
    --perun-connector-config-path "/path/to/file"
```

### oracle2postgresql.py
Synchronizes data from Oracle db to PostgreSQL db.

Requires config file located at `/etc/oracle2postgresql_cfg.yaml` and [Oracle client](https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html).
#### Functionality
1. Attribute Import:

Imports attributes from Oracle database tables to the PostgreSQL database, into a table compatible with [simplesamlphp-module-sqlattribs](https://github.com/tenet-ac-za/simplesamlphp-module-sqlattribs). Each attribute is specified with a corresponding SQL SELECT statement.

2. Table Import:

Imports tables from the Oracle database to the PostgreSQL one. Supports both full and incremental synchronization.
For full synchronization, all records from the source table are imported.
For incremental synchronization, only records modified since the last synchronization are imported, based on designated change columns.
The full sync in turned off by default. Run with `-f` or `--full_sync` flag to turn it on.

Attributes and tables intended for import are stated in the config. 
Target table names from PostgreSQL are hardcoded due to the possibility of needing to create them.

## Nagios probes

All nagios scripts are located under `nagios` directory.

### check_mongodb

Nagios monitoring probe for mongodb.

Tested options:

- connect
- connections
- replication_lag
- replset_state

(some possible options may not work since there are constructs which are not supported
by the latest mongodb versions)

For usage instructions, run:

```sh
check_mongodb --help
```

### check_saml

SAML authentication check compatible with SimpleSAMLphp and mitreID.

Basic OIDC check can be triggered by adding `--basic-oidc-check` switch. This checks
for `state` and `code` parameters in the result url after a log in attempt.

For more usage instructions, run:

```sh
check_saml --help
```

Example:

```sh
python3 check_saml
    --username "my_username"
    --password "my_password"
    --username-field "j_username"
    --password-field "j_password"
    --postlogout-string "Successful logout"
```

### check_user_logins

Check users which login in repeatedly more often than a specified threshold (logins per
seconds).

For usage instructions, run:

```sh
check_user_logins --help
```

Example:

```sh
python3 check_user_logins
    -p /var/log/proxyaai/simplesamlphp/simplesamlphp/simplesamlphp.log
    -l 5
    -s 60
    -r "^(?P<datetime>.{20}).*audit-login.* (?P<userid>[0-9]+)@muni\.cz$"
    -d "%b %d %Y %H:%M:%S"
```

### check_ldap

Check whether an LDAP server is available.

For usage instructions, run:

```sh
check_ldap --help
```

### check_ldap_syncrepl

Check whether an LDAP replica is up to date with the provider.

For usage instructions, run:

```sh
check_ldap_syncrepl --help
```

### check_privacyidea

Check whether privacyidea is available by performing TOTP authentication via the API.
Use caching arguments for avoiding failure when one TOTP code is used two times.

For usage instructions, run:

```sh
check_privacyidea --help
```

### check_pgsql

Check connection to PostgreSQL using a configurable query.

For usage instructions, run:

```sh
check_pgsql --help
```

### check_oidc_login

Check that OIDC auth process works by acting as an OIDC client (RP) attempting to
authenticate against an OIDC server (OP). Supports clients with PKCE and non-PKCE
authentication. Additional tag `-pkce` must be added to test PKCE log in. Using client
secret is always enforced since some clients might require it on top of PKCE.

Target OIDC server (OP) should **not** require authentication for this probe to
work. It **does not** test the credentials' validity but rather the OIDC auth process. This
can be achieved, for example, by setting up SATOSA's reflector backend.

For usage instructions, run:

```sh
check_oidc_login --help
```

Example:

```sh
python3 check_oidc_login
    --redirect-uri "http://localhost:44322/signin-oidc"
    --client-id "my_oidc_client_id"
    --client-secret "my_oidc_pkce_secret"
    --issuer "https://id.muni.cz"
    -vvv # verbose debug output
    -pkce
```
