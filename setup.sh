#!/bin/sh

[ $# -eq 1 ] || { echo "$0 NAME - create ganglia-pymodule_NAME"; exit 1; }
name=$1
dir=ganglia-pymodule_$name

mkdir $dir
mkdir $dir/{conf.d,junk,python_modules}
cat <<EOF > $dir/README.mkdn
$name
===============
python module for ganglia 3.1.

"$name" send metrics on fixme.

EOF

cat <<EOF > $dir/conf.d/$name.conf
modules {
  module {
    name     = "$name"
    language = "python"
    param device {
        value = "bond0"
    }
    param host {
        value = "goa"
    }
  }
}

collection_group {
  collect_every  = 20
  time_threshold = 90
  metric {
    name  = "foo"
    title = "Title of Foo"
    value_threshold = 1.0
  }
  metric {
    name  = "bar"
    title = "Title of Bar"
    value_threshold = 1.0
  }
}
EOF

cat <<EOF

TODO:
cp skel_xxx.py $dir/python_modules/$name.py
EOF
