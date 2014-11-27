django-deflect
==============

A Django short URL redirection application.

Settings
--------

**DEFLECT_ASYNC_CONCURRENCY**

   When using the ``checkurls`` management command, this sets the concurrency
   level of the asyncronous requests used to validate the target URLs.

**DEFLECT_NOOVERRIDE**

   Setting this to ``True`` causes ``utm_nooverride`` to be injected for a
   tracking URL redirect.

**DEFLECT_REQUESTS_TIMEOUT**

   When requests are made to validate target URLs, this configures the timeout
   value used by the ``requests`` library.
