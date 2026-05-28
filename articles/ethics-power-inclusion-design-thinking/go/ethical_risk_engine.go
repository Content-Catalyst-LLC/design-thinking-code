package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type DesignDecision struct {
	Name           string
	Harm           float64
	Probability    float64
	Exposure       float64
	Detectability  float64
	Accountability float64
	Inclusion      float64
	PublicValue    float64
	Repairability  float64
	Privacy        float64
	Autonomy       float64
	Manipulation   float64
	EthicalRisk    float64
	ReviewPriority float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func ethicalRisk(x DesignDecision) float64 {
	return x.Harm * x.Probability * x.Exposure * (1.0 - x.Detectability) * (1.0 - x.Accountability)
}

func reviewPriority(x DesignDecision) float64 {
	repairDeficit := 1.0 - x.Repairability
	return 0.32*x.EthicalRisk +
		0.20*x.Harm +
		0.14*x.Exposure +
		0.10*(1.0-x.Accountability) +
		0.08*(1.0-x.Detectability) +
		0.06*(1.0-x.Inclusion) +
		0.05*x.Privacy +
		0.03*x.Autonomy +
		0.02*x.Manipulation -
		0.12*x.PublicValue +
		0.10*repairDeficit
}

func loadDecisions(path string) []DesignDecision {
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

	var items []DesignDecision

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 13 {
			log.Fatalf("malformed row: %v", row)
		}

		x := DesignDecision{
			Name:           row[0],
			Harm:           parseFloat(row[2]),
			Probability:    parseFloat(row[3]),
			Exposure:       parseFloat(row[4]),
			Detectability:  parseFloat(row[5]),
			Accountability: parseFloat(row[6]),
			Inclusion:      parseFloat(row[7]),
			PublicValue:    parseFloat(row[8]),
			Repairability:  parseFloat(row[9]),
			Privacy:        parseFloat(row[10]),
			Autonomy:       parseFloat(row[11]),
			Manipulation:   parseFloat(row[12]),
		}
		x.EthicalRisk = ethicalRisk(x)
		x.ReviewPriority = reviewPriority(x)
		items = append(items, x)
	}

	return items
}

func main() {
	path := "../data/raw/ethical_design_decisions_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	items := loadDecisions(path)

	sort.Slice(items, func(i, j int) bool {
		return items[i].ReviewPriority > items[j].ReviewPriority
	})

	fmt.Println("rank,design_decision,ethical_risk,review_priority")
	for i, x := range items {
		fmt.Printf("%d,%s,%.6f,%.6f\n", i+1, x.Name, x.EthicalRisk, x.ReviewPriority)
	}
}
