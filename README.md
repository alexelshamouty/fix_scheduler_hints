# fix_scheduler_hints

After dragging nova from old versions like kilo and upgrading the whole infrastructure I found out the the nova-manage migration's were not always in point.

There has been multiple cases were I had to patch the DB to fix old VM's schemas in multiple places.

This was one of them. Sadly in the request_spec the infomration needed for scheduler_hints were not available. And that broke the migration as a side effect of trying to reschedule the machine on a different host.

This fixes it by grapping the server group from another table using the instance ID to check it's membership in a group and then fixing the request_spec json information in the DB if needes be
