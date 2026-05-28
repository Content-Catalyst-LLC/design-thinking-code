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
	Name               string
	OutcomeImprovement float64
	BurdenReduction    float64
	EquityPerformance  float64
	TrustImprovement   float64
	Durability         float64
	OperationalCost    float64
	ResidualRisk       float64
	Penalty            float64
	EvaluationValue    float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func penalty(x Intervention) float64 {
	return 0.50*x.OperationalCost + 0.50*x.ResidualRisk
}

func evaluationValue(x Intervention) float64 {
	return 0.24*x.OutcomeImprovement +
		0.20*x.BurdenReduction +
		0.20*x.EquityPerformance +
		0.16*x.TrustImprovement +
		0.14*x.Durability -
		0.06*x.Penalty
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
		if len(row) < 10 {
			log.Fatalf("malformed row: %v", row)
		}

		x := Intervention{
			Name:               row[0],
			OutcomeImprovement: parseFloat(row[3]),
			BurdenReduction:    parseFloat(row[4]),
			EquityPerformance:  parseFloat(row[5]),
			TrustImprovement:   parseFloat(row[6]),
			Durability:         parseFloat(row[7]),
			OperationalCost:    parseFloat(row[8]),
			ResidualRisk:       parseFloat(row[9]),
		}
		x.Penalty = penalty(x)
		x.EvaluationValue = evaluationValue(x)
		items = append(items, x)
	}

	return items
}

func main() {
	path := "../data/raw/evaluation_portfolio_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	items := loadPortfolio(path)

	sort.Slice(items, func(i, j int) bool {
		return items[i].EvaluationValue > items[j].EvaluationValue
	})

	fmt.Println("rank,intervention,evaluation_value,penalty")
	for i, x := range items {
		fmt.Printf("%d,%s,%.6f,%.6f\n", i+1, x.Name, x.EvaluationValue, x.Penalty)
	}
}
