package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type InnovationConcept struct {
	Name                    string
	Desirability            float64
	Feasibility             float64
	Viability               float64
	Equity                  float64
	LearningValue           float64
	ImplementationReadiness float64
	Risk                    float64
	DesignValue             float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func designValue(x InnovationConcept) float64 {
	return 0.22*x.Desirability +
		0.16*x.Feasibility +
		0.16*x.Viability +
		0.18*x.Equity +
		0.12*x.LearningValue +
		0.10*x.ImplementationReadiness -
		0.06*x.Risk
}

func loadConcepts(path string) []InnovationConcept {
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

	var items []InnovationConcept

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 10 {
			log.Fatalf("malformed row: %v", row)
		}

		x := InnovationConcept{
			Name:                    row[0],
			Desirability:            parseFloat(row[3]),
			Feasibility:             parseFloat(row[4]),
			Viability:               parseFloat(row[5]),
			Equity:                  parseFloat(row[6]),
			LearningValue:           parseFloat(row[7]),
			ImplementationReadiness: parseFloat(row[8]),
			Risk:                    parseFloat(row[9]),
		}
		x.DesignValue = designValue(x)
		items = append(items, x)
	}

	return items
}

func main() {
	path := "../data/raw/organizational_innovation_concepts_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	items := loadConcepts(path)

	sort.Slice(items, func(i, j int) bool {
		return items[i].DesignValue > items[j].DesignValue
	})

	fmt.Println("rank,concept,design_value,risk")
	for i, x := range items {
		fmt.Printf("%d,%s,%.6f,%.6f\n", i+1, x.Name, x.DesignValue, x.Risk)
	}
}
