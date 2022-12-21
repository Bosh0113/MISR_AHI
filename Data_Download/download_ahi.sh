#!/bin/bash
# himawari-wget script (K.Ichii)

trap "" HUP

#BASEDIR=ftp://192.168.1.5/gridded/FD/V20190123
BASEDIR=ftp://hmwr829gr.cr.chiba-u.ac.jp/gridded/FD/V20190123
OUTDIR=.

for iyear in $(seq 2017 2020) ; do

  for imonth in $(seq -f %02g 1 13) ; do

    for iday in $(seq -f %02g 1 31) ; do

      wget -P $OUTDIR -r -l1 -nc --no-parent $BASEDIR/${iyear}${imonth}/4KM/${iyear}${imonth}${iday}/${iyear}${imonth}${iday}????.sat.*
      wget -P $OUTDIR -r -l1 -nc --no-parent $BASEDIR/${iyear}${imonth}/4KM/${iyear}${imonth}${iday}/${iyear}${imonth}${iday}????.sun.*

      # wget -P $OUTDIR -r -l1 -nc --no-parent $BASEDIR/${iyear}${imonth}/VIS/${iyear}${imonth}${iday}????.vis.*
      # wget -P $OUTDIR -r -l1 -nc --no-parent $BASEDIR/${iyear}${imonth}/EXT/${iyear}${imonth}${iday}????.ext.*
      # wget -P $OUTDIR -r -l1 -nc --no-parent $BASEDIR/${iyear}${imonth}/SIR/${iyear}${imonth}??????.sir.*
      # wget -P $OUTDIR -r -l1 -nc --no-parent $BASEDIR/${iyear}${imonth}/TIR/${iyear}${imonth}??????.tir.*

      #wget -P $OUTDIR -r -l1 -nc --no-parent $BASEDIR/${iyear}${imonth}/VIS/${iyear}${imonth}??2[123]??.vis.*
      #wget -P $OUTDIR -r -l1 -nc --no-parent $BASEDIR/${iyear}${imonth}/EXT/${iyear}${imonth}??2[123]??.ext.*
      #wget -P $OUTDIR -r -l1 -nc --no-parent $BASEDIR/${iyear}${imonth}/SIR/${iyear}${imonth}??2[123]??.sir.*
      #wget -P $OUTDIR -r -l1 -nc --no-parent $BASEDIR/${iyear}${imonth}/TIR/${iyear}${imonth}??2[123]??.tir.*

      #wget -P $OUTDIR -r -l1 -nc --no-parent $BASEDIR/${iyear}${imonth}/EXT/${iyear}${imonth}??????.ext.*off.*

    done

  done

done

