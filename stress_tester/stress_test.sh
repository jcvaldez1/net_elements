#!/bin/bash

END=5
x=$END 
URL="http://10.147.4.201/cdn-b-east.streamable.com/video/mp4/66o7s37fe.mp4?token=gowKTtkLQdvuX2yLkdhBhg&expires=1555336802"
offset=0
rm ./delay_results.txt
touch ./delay_results.txt

foo(){
  x=1
  echo "$1"
  while [ $x -le $(($1*10)) ]
  do
      real=$(($x+$offset))
      touch ./vids/$real.mp4
      date -u
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
