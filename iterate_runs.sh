
FILEN=()
# Collect data and save the file names you saved output to
for i in {1..5}
do
    FILEN+=('temp'$i'.dat')
    #./ce_design.py > temp$i.dat
done
# Iterate through the saved files
for file in ${FILEN[@]}
do
    echo $file
done