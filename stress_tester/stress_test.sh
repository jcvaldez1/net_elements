#!/bin/bash

END=5
x=$END 
URL="http://10.147.4.69/cdn-b-east.streamable.com/video/mp4/66o7scf87.mp4?token=cPXKJUYTDjSLyj8LFE3-2g&amp;expires=1552672212"
offset=0
rm ./delay_results.txt
touch ./delay_results.txt

foo(){
  x=1
  echo "$1"
  date -u
  while [ $x -le $(($1*10)) ]
  do
      real=$(($x+$offset))
      touch ./vids/$real.mp4
      python3 recorder.py $real $URL >> delay_results.txt &
      pids[${x}]=$!
      x=$(($x+1))
  done 

  # wait for all pids
  for pid in ${pids[*]}; do
      wait $pid
  done
  sleep 5
  echo "Test #$1 Results : " >> delay_results.txt;
  echo "All processes done"

}

for i in {1..5}
do
    # first make thread sendin $i*10 requests
    foo $i
    # adjust offset
    offset=$(($offset+$(($i*10))))
    # do till $END
    #sleep 10
done

wait 
echo "All done"
