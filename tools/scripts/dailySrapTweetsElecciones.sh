begin=2019-04-01
end=2019-04-30
while [ "$begin" != "$end" ]; do
  next=$(date -I -d "$begin + 1 day")
  echo "$begin - $next"
  output="tweets$begin.csv"
  echo "$output"

  twitterscraper \
    "#ElecccionesGenerales28A OR Congreso OR Senado OR #28AEnÀPunt OR España OR #eleccionesmediaset OR #Elecciones28A OR #Elecciones2019 OR #28AUnidasPodemos OR #VotaPorFavor OR #VotaCoño OR #YoVoto OR #28DeAbril OR #TodosAVotar OR #votar OR #democracia OR #vota OR #28abr OR votar OR voto" \
    -bd "$begin" \
    -ed "$next" \
    -l 10000000 \
    -c \
    -o $output

  begin=$(date -I -d "$begin + 1 day")

done
