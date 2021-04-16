#!/bin/sh
# Setups up a blockchain instance on port 33767

tmpfile="$$instanceTmpfile.py"
touch $tmpfile

`head -n -1 viceroychain.py >$tmpfile`
`echo "    app.run(port=$1)">>$tmpfile`
python3 $tmpfile

rm $tmpfile