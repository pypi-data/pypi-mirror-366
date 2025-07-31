import setuptools

setuptools.setup(
    name="perun_proxy_utils",
    python_requires=">=3.9",
    url="https://gitlab.ics.muni.cz/perun/perun-proxyidp/perun-proxy-utils.git",
    description="Utilities and monitoring probes for Perun ProxyIdP",
    include_package_data=True,
    packages=setuptools.find_namespace_packages(include=["perun.*"]),
    install_requires=[
        "setuptools",
        "pymongo~=4.3",
        "asyncssh~=2.13",
        "docker~=7.1",
        "beautifulsoup4~=4.12",
        "requests~=2.31",
        "PyYAML>=5.4,<7.0",
        "check_nginx_status~=1.0",
        "pyotp~=2.9",
        "perun.connector~=3.8",
        "privacyidea~=3.9",
        "flask~=1.1",
        "idpyoidc~=2.1",
        "sqlalchemy~=1.4",
    ],
    extras_require={
        "ldap": [
            "ldap3~=2.9.1",
            "check_syncrepl_extended~=2020.13",
        ],
        "postgresql": [
            "psycopg2-binary~=2.9",
        ],
        "oracle": [
            "cx-Oracle~=8.3",
        ],
    },
    entry_points={
        "console_scripts": [
            "run_probes=perun.proxy.utils.run_probes:main",
            "check_custom_command=perun.proxy.utils.nagios.check_custom_command:main",
            "check_dockers=perun.proxy.utils.nagios.check_dockers:main",
            "check_exabgp_propagation="
            "perun.proxy.utils.nagios.check_exabgp_propagation:main",
            "check_ldap=perun.proxy.utils.nagios.check_ldap:main",
            "check_ldap_syncrepl=check_syncrepl_extended.check_syncrepl_extended:main",
            "check_mongodb=perun.proxy.utils.nagios.check_mongodb:main",
            "check_nginx=check_nginx_status.check_nginx_status:main",
            "check_oidc_login=perun.proxy.utils.nagios.check_oidc_login:main",
            "check_rpc_status=perun.proxy.utils.nagios.check_rpc_status:main",
            "check_saml=perun.proxy.utils.nagios.check_saml:main",
            "check_user_logins=perun.proxy.utils.nagios.check_user_logins:main",
            "check_php_syntax=perun.proxy.utils.nagios.check_php_syntax:main",
            "check_webserver_availability="
            "perun.proxy.utils.nagios.webserver_availability:main",
            "check_privacyidea=perun.proxy.utils.nagios.check_privacyidea:main",
            "check_pgsql=perun.proxy.utils.nagios.check_pgsql:main",
            "metadata_expiration=perun.proxy.utils.metadata_expiration:main",
            "print_docker_versions=perun.proxy.utils.print_docker_versions:main",
            "run_version_script=perun.proxy.utils.run_version_script:main",
            "separate_oidc_logs=perun.proxy.utils.separate_oidc_logs:main",
            "separate_ssp_logs=perun.proxy.utils.separate_ssp_logs:main",
            "sync_usable_token_types=perun.proxy.utils.sync_usable_token_types:main",
            "oracle2postgresql=perun.proxy.utils.oracle2postgresql:main",
        ]
    },
)
