#!/usr/bin/env bash
# 원자료 내려받기. 사용법: tools/fetch_sources.sh <내려받을 폴더>
# 받은 파일은 저장소에 넣지 않아요. build_world_data.py가 이 폴더를 읽어 data/world.json을 만들어요.
set -u
OUT="${1:?folder}"; mkdir -p "$OUT/wb"
WB="SH.DYN.MORT SH.DYN.NMRT SH.STA.MMRT SH.PRV.SMOK SH.PRV.SMOK.MA SH.PRV.SMOK.FE SH.XPD.CHEX.PC.CD SH.XPD.OOPC.CH.ZS
SE.ADT.LITR.ZS SE.PRM.CMPT.ZS SE.SEC.CMPT.LO.ZS SE.TER.ENRR SL.UEM.TOTL.ZS SL.UEM.1524.ZS SL.TLF.CACT.FE.ZS SL.AGR.EMPL.ZS
SL.EMP.VULN.ZS SH.DYN.AIDS.ZS SH.HIV.ARTC.ZS VC.IHR.PSRC.P5 SH.STA.TRAF.P5 SH.STA.SUIC.P5 SP.M18.2024.FE.ZS SI.POV.DDAY
SI.POV.LMIC SI.POV.UMIC SI.POV.GINI EG.ELC.ACCS.ZS SH.H2O.BASW.ZS SH.STA.BASS.ZS IT.NET.USER.ZS SP.URB.TOTL.IN.ZS
SN.ITK.DEFC.ZS SH.STA.STNT.ZS SL.TLF.0714.ZS SP.ADO.TFRT SH.MED.PHYS.ZS SM.POP.TOTL.ZS SH.DTH.COMM.ZS SH.DTH.NCOM.ZS
SH.DTH.INJR.ZS SH.DYN.NCOM.ZS SH.ALC.PCAP.LI NY.GDP.PCAP.PP.CD SH.STA.BRTC.ZS"
for ind in $WB; do
  [ -s "$OUT/wb/$ind.json" ] && continue
  for t in 1 2 3; do
    curl -sS -m 180 "https://api.worldbank.org/v2/country/all/indicator/$ind?format=json&per_page=20000&date=2005:2025" -o "$OUT/wb/$ind.json" && break
    sleep $((t*4))
  done
done
get(){ [ -s "$OUT/$1" ] || curl -sS -L -m 600 -o "$OUT/$1" "$2"; }
get wpp_demo.csv.gz "https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES/WPP2024_Demographic_Indicators_Medium.csv.gz"
get hdr.csv "https://hdr.undp.org/sites/default/files/2023-24_HDR/HDR23-24_Composite_indices_complete_time_series.csv"
get mpd2020.xlsx "https://www.rug.nl/ggdc/historicaldevelopment/maddison/data/mpd2020.xlsx"
get happy.csv "https://ourworldindata.org/grapher/happiness-cantril-ladder.csv?v=1&csvType=full&useColumnShortNames=true"
get school_long.csv "https://ourworldindata.org/grapher/mean-years-of-schooling-long-run.csv?v=1&csvType=full&useColumnShortNames=true"
get urban2050.csv "https://ourworldindata.org/grapher/urban-and-rural-population-2050.csv?v=1&csvType=full&useColumnShortNames=true"
get ucdp.zip "https://ucdp.uu.se/downloads/ucdpprio/ucdp-prio-acd-261-csv.zip" && (cd "$OUT" && unzip -o -q ucdp.zip -d ucdp)
