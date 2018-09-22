#!/bin/bash

trap "exit" INT
read -p "The accounts will total about 300GB in size: continue? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then


  #make directories
  for year in 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017
  do
    mkdir $year
  done


  #use the python script to download the files
  python3 download_files.py


  #unzip the files
  for year in 2008 2009 2010 2011 2012 2013 2014 2015 2016 2017
  do
    cd $year
    unzip '*.zip'
    rm *.zip
    cd ../
  done

fi
