#bin/bash

# File capturing docker container stats

# Time interval
INTERVAL=2
#file output
OUTNAME=$1.txt

#first line with startin timestamp
echo $(date +'%s.%N') | tee --append $OUTNAME
# column names and delimiter
echo "Name:CPUPercent:MemUsage:Timestamp" | tee --append $OUTNAME

# function writing docker stats output to file with custom format
update_file() {
  docker stats --no-stream --format "{{.Name}}:{{.CPUPerc}}:{{.MemUsage}}:
  $(date +'%s.%N')" | tee --append $OUTNAME
}


while true; do
  update_file &
  sleep $INTERVAL
done
