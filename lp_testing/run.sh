glpsol --cpxlp -o temp.dat $1

if [ $# > 1 ]; then
	if [ "$2" == "y" ]; then
		cat temp.dat
	fi
fi
