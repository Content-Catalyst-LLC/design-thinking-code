package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type Experiment struct {
	Name                string
	LearningGain        float64
	UpdateFlexibility   float64
	ExpectedImprovement float64
	ResidualRisk        float64
	Value               float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func experimentValue(experiment Experiment) float64 {
	return 0.35*experiment.LearningGain +
		0.25*experiment.UpdateFlexibility +
		0.25*experiment.ExpectedImprovement -
		0.15*experiment.ResidualRisk
}

func loadExperiments(path string) []Experiment {
	file, err := os.Open(path)
	if err != nil {
		log.Fatalf("unable to open input file: %v", err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	rows, err := reader.ReadAll()
	if err != nil {
		log.Fatalf("unable to read CSV: %v", err)
	}

	var experiments []Experiment

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 5 {
			log.Fatalf("malformed row: %v", row)
		}

		experiment := Experiment{
			Name:                row[0],
			LearningGain:        parseFloat(row[1]),
			UpdateFlexibility:   parseFloat(row[2]),
			ExpectedImprovement: parseFloat(row[3]),
			ResidualRisk:        parseFloat(row[4]),
		}
		experiment.Value = experimentValue(experiment)
		experiments = append(experiments, experiment)
	}

	return experiments
}

func main() {
	path := "../data/raw/experiments_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	experiments := loadExperiments(path)

	sort.Slice(experiments, func(i, j int) bool {
		return experiments[i].Value > experiments[j].Value
	})

	fmt.Println("rank,experiment,experiment_value")
	for i, experiment := range experiments {
		fmt.Printf("%d,%s,%.6f\n", i+1, experiment.Name, experiment.Value)
	}
}
