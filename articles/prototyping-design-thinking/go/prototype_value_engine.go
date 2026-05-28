package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type Prototype struct {
	Name                    string
	LearningGain            float64
	FeasibilitySignal       float64
	UserResponse            float64
	EquityValue             float64
	ImplementationRelevance float64
	EthicalRisk             float64
	OperationalRisk         float64
	TechnicalRisk           float64
	ScalingRisk             float64
	CompositeRisk           float64
	PrototypeValue          float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func compositeRisk(p Prototype) float64 {
	return 0.30*p.EthicalRisk +
		0.30*p.OperationalRisk +
		0.20*p.TechnicalRisk +
		0.20*p.ScalingRisk
}

func prototypeValue(p Prototype) float64 {
	return 0.25*p.LearningGain +
		0.18*p.FeasibilitySignal +
		0.20*p.UserResponse +
		0.15*p.EquityValue +
		0.12*p.ImplementationRelevance -
		0.10*p.CompositeRisk
}

func loadPortfolio(path string) []Prototype {
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

	var prototypes []Prototype

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 12 {
			log.Fatalf("malformed row: %v", row)
		}

		p := Prototype{
			Name:                    row[0],
			LearningGain:            parseFloat(row[3]),
			FeasibilitySignal:       parseFloat(row[4]),
			UserResponse:            parseFloat(row[5]),
			EquityValue:             parseFloat(row[6]),
			ImplementationRelevance: parseFloat(row[7]),
			EthicalRisk:             parseFloat(row[8]),
			OperationalRisk:         parseFloat(row[9]),
			TechnicalRisk:           parseFloat(row[10]),
			ScalingRisk:             parseFloat(row[11]),
		}
		p.CompositeRisk = compositeRisk(p)
		p.PrototypeValue = prototypeValue(p)
		prototypes = append(prototypes, p)
	}

	return prototypes
}

func main() {
	path := "../data/raw/prototype_portfolio_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	prototypes := loadPortfolio(path)

	sort.Slice(prototypes, func(i, j int) bool {
		return prototypes[i].PrototypeValue > prototypes[j].PrototypeValue
	})

	fmt.Println("rank,prototype,prototype_value,composite_risk")
	for i, p := range prototypes {
		fmt.Printf("%d,%s,%.6f,%.6f\n", i+1, p.Name, p.PrototypeValue, p.CompositeRisk)
	}
}
