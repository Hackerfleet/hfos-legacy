Warning
=======

This module requires an installed libldap.so and is currently not fully
suited for ordinary LDAP operation since it is a prototype to connect HFOS' authentication
module with c-base' uid/pin LDAP service.

On Debian you can just do:

 .. code-block:: sh

    $ sudo apt-get install libldap2-dev