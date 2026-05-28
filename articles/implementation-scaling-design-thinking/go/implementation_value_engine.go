package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type Intervention struct {
	Name                    string
	AdoptionReadiness       float64
	OperationalFit          float64
	Durability              float64
	GovernanceReadiness     float64
	EquityReadiness         float64
	FinancialSustainability float64
	OperationalRisk         float64
	GovernanceRisk          float64
	TechnicalRisk           float64
	EquityRisk              float64
	FinancialRisk           float64
	CompositeRisk           float64
	ImplementationValue     float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func compositeRisk(x Intervention) float64 {
	return 0.25*x.OperationalRisk +
		0.22*x.GovernanceRisk +
		0.18*x.TechnicalRisk +
		0.22*x.EquityRisk +
		0.13*x.FinancialRisk
}

func implementationValue(x Intervention) float64 {
	return 0.20*x.AdoptionReadiness +
		0.18*x.OperationalFit +
		0.18*x.Durability +
		0.15*x.GovernanceReadiness +
		0.14*x.EquityReadiness +
		0.10*x.FinancialSustainability -
		0.05*x.CompositeRisk
}

func loadPortfolio(path string) []Intervention {
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

	var items []Intervention

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 14 {
			log.Fatalf("malformed row: %v", row)
		}

		x := Intervention{
			Name:                    row[0],
			AdoptionReadiness:       parseFloat(row[3]),
			OperationalFit:          parseFloat(row[4]),
			Durability:              parseFloat(row[5]),
			GovernanceReadiness:     parseFloat(row[6]),
			EquityReadiness:         parseFloat(row[7]),
			FinancialSustainability: parseFloat(row[8]),
			OperationalRisk:         parseFloat(row[9]),
			GovernanceRisk:          parseFloat(row[10]),
			TechnicalRisk:           parseFloat(row[11]),
			EquityRisk:              parseFloat(row[12]),
			FinancialRisk:           parseFloat(row[13]),
		}
		x.CompositeRisk = compositeRisk(x)
		x.ImplementationValue = implementationValue(x)
		items = append(items, x)
	}

	return items
}

func main() {
	path := "../data/raw/implementation_portfolio_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	items := loadPortfolio(path)

	sort.Slice(items, func(i, j int) bool {
		return items[i].ImplementationValue > items[j].ImplementationValue
	})

	fmt.Println("rank,intervention,implementation_value,composite_risk")
	for i, x := range items {
		fmt.Printf("%d,%s,%.6f,%.6f\n", i+1, x.Name, x.ImplementationValue, x.CompositeRisk)
	}
}
