#! /bin/sh
# daemon starter script
# based on skeleton from Debian GNU/Linux
# cliechti at gmx.net

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DAEMON=/usr/local/bin/port_publisher.py
NAME=port_publisher
DESC="serial port avahi device publisher"

test -f $DAEMON || exit 0

set -e

case "$1" in
    start)
        echo -n "Starting $DESC: "
        $DAEMON --daemon --pidfile /var/run/$NAME.pid
        echo "$NAME."
        ;;
    stop)
        echo -n "Stopping $DESC: "
        start-stop-daemon --stop --quiet --pidfile /var/run/$NAME.pid
        # \     --exec $DAEMON
        echo "$NAME."
        ;;
    restart|force-reload)
        echo -n "Restarting $DESC: "
        start-stop-daemon --stop --quiet --pidfile \
                /var/run/$NAME.pid
                # --exec $DAEMON
        sleep 1
        $DAEMON --daemon --pidfile /var/run/$NAME.pid
        echo "$NAME."
        ;;
    *)
        N=/etc/init.d/$NAME
        echo "Usage: $N {start|stop|restart|force-reload}" >&2
        exit 1
        ;;
esac

exit 0

