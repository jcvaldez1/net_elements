#!/bin/bash

END=10
x=$END 
URL="devstack.com/video.mp4"
while [ $x -gt 0 ]; 
do 
    
    y=$END
    while [ $y -gt 0 ]; 
    do 
      python3 recorder.py $y $URL&
      y=$(($y-1))
    done

  x=$(($x-1))
done
