package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type Pathway struct {
	Name           string
	HumanRelevance float64
	Feasibility    float64
	LearningValue  float64
	ResidualRisk   float64
	Value          float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func designValue(p Pathway) float64 {
	return 0.35*p.HumanRelevance +
		0.25*p.Feasibility +
		0.25*p.LearningValue -
		0.15*p.ResidualRisk
}

func loadPathways(path string) []Pathway {
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

	var pathways []Pathway

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 5 {
			log.Fatalf("malformed row: %v", row)
		}

		p := Pathway{
			Name:            row[0],
			HumanRelevance:  parseFloat(row[1]),
			Feasibility:     parseFloat(row[2]),
			LearningValue:   parseFloat(row[3]),
			ResidualRisk:    parseFloat(row[4]),
		}
		p.Value = designValue(p)
		pathways = append(pathways, p)
	}

	return pathways
}

func main() {
	path := "../data/raw/design_pathways_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	pathways := loadPathways(path)

	sort.Slice(pathways, func(i, j int) bool {
		return pathways[i].Value > pathways[j].Value
	})

	fmt.Println("rank,pathway,design_value")
	for i, pathway := range pathways {
		fmt.Printf("%d,%s,%.6f\n", i+1, pathway.Name, pathway.Value)
	}
}
