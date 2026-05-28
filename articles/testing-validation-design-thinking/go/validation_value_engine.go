package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type Concept struct {
	Name            string
	Desirability   float64
	Feasibility    float64
	Viability      float64
	Responsibility float64
	Friction       float64
	ResidualRisk   float64
	CombinedRisk   float64
	ValidationValue float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func combinedRisk(c Concept) float64 {
	return 0.50*c.Friction + 0.50*c.ResidualRisk
}

func validationValue(c Concept) float64 {
	return 0.25*c.Desirability +
		0.20*c.Feasibility +
		0.20*c.Viability +
		0.20*c.Responsibility -
		0.15*c.CombinedRisk
}

func loadConcepts(path string) []Concept {
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

	var concepts []Concept

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 9 {
			log.Fatalf("malformed row: %v", row)
		}

		c := Concept{
			Name:            row[0],
			Desirability:   parseFloat(row[3]),
			Feasibility:    parseFloat(row[4]),
			Viability:      parseFloat(row[5]),
			Responsibility: parseFloat(row[6]),
			Friction:       parseFloat(row[7]),
			ResidualRisk:   parseFloat(row[8]),
		}
		c.CombinedRisk = combinedRisk(c)
		c.ValidationValue = validationValue(c)
		concepts = append(concepts, c)
	}

	return concepts
}

func main() {
	path := "../data/raw/validation_concepts_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	concepts := loadConcepts(path)

	sort.Slice(concepts, func(i, j int) bool {
		return concepts[i].ValidationValue > concepts[j].ValidationValue
	})

	fmt.Println("rank,concept,validation_value,combined_risk")
	for i, c := range concepts {
		fmt.Printf("%d,%s,%.6f,%.6f\n", i+1, c.Name, c.ValidationValue, c.CombinedRisk)
	}
}
