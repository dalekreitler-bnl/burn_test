#!/bin/bash

argtocsvarg () {
ex $1 <<EOF_EOF_EOF
set nomagic
1
s/\$/${2}${3}/
1,\$g/<$2>/j
1,\$s/<\/$2>/${3}/
1,\$s/<$2>//
wq
EOF_EOF_EOF
}


if [ "${1}xx" == "--helpxx" ]; then
  echo "passxmltocsv.bash spotdata.xml"
  echo "  take an xml file of image, spot_count, spot_no_ice,"
  echo "      d_min, d_min_method_1, d_min_method_2, and     "
  echo "      total_intensity, and converts it to a csv file "
  echo "      on stdout with header line for spread sheet plotting"
  echo " "
  echo "this is not a general xml to csv converter.  You will"
  echo "need to edit the code below for different xml layouts."
  exit


fi

# Put a blank line in front

cp $1 /tmp/${1}$$

ex /tmp/${1}$$ <<EOF_EOF_EOF
1
i

.
wq
EOF_EOF_EOF

argtocsvarg /tmp/${1}$$ "image" ","
argtocsvarg /tmp/${1}$$ "spot_count" ","
argtocsvarg /tmp/${1}$$ "spot_count_no_ice" ","
argtocsvarg /tmp/${1}$$ "d_min" ","
argtocsvarg /tmp/${1}$$ "d_min_method_1" ","
argtocsvarg /tmp/${1}$$ "d_min_method_2" ","
argtocsvarg /tmp/${1}$$ "total_intensity" ""
argtocsvarg /tmp/${1}$$ "response" ""


# cleanup

ex /tmp/${1}$$ <<EOF_EOF_EOF
1
s/response\$//
1,\$s/ ,/,/g
1,\$s/^.*_0//
1,\$s/\.cbf//
wq
EOF_EOF_EOF


cat /tmp/${1}$$


