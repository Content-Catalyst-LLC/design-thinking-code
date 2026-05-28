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
	Name                string
	Usability           float64
	Feasibility         float64
	EcologicalBenefit   float64
	Circularity         float64
	Equity              float64
	Durability          float64
	Risk                float64
	SustainabilityValue float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func sustainabilityValue(x Concept) float64 {
	return 0.16*x.Usability +
		0.16*x.Feasibility +
		0.24*x.EcologicalBenefit +
		0.16*x.Circularity +
		0.14*x.Equity +
		0.08*x.Durability -
		0.06*x.Risk
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

	var items []Concept

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 10 {
			log.Fatalf("malformed row: %v", row)
		}

		x := Concept{
			Name:              row[0],
			Usability:         parseFloat(row[3]),
			Feasibility:       parseFloat(row[4]),
			EcologicalBenefit: parseFloat(row[5]),
			Circularity:       parseFloat(row[6]),
			Equity:            parseFloat(row[7]),
			Durability:        parseFloat(row[8]),
			Risk:              parseFloat(row[9]),
		}
		x.SustainabilityValue = sustainabilityValue(x)
		items = append(items, x)
	}

	return items
}

func main() {
	path := "../data/raw/sustainability_concepts_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	items := loadConcepts(path)

	sort.Slice(items, func(i, j int) bool {
		return items[i].SustainabilityValue > items[j].SustainabilityValue
	})

	fmt.Println("rank,concept,sustainability_value,risk")
	for i, x := range items {
		fmt.Printf("%d,%s,%.6f,%.6f\n", i+1, x.Name, x.SustainabilityValue, x.Risk)
	}
}
