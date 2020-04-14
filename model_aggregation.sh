#!/usr/bin/env python3
sectors=("HealthCare" "ConsumerDiscretionary" "RealEstate" "ConsumerStaples" "Financials")
models=(0 1 2 3 )
for s in ${sectors[@]}; do
  echo $s >> out.txt
  echo $s
    for m in ${models[@]}; do
    echo $m >> out.txt
    echo $m
    python3 simulator.py $m -s $s -y 2008-2018  >> out.txt
    done
done
