package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type StrategicOption struct {
	Name          string
	Desirability  float64
	Feasibility   float64
	Viability     float64
	Alignment     float64
	Ethics        float64
	Learning      float64
	Effort        float64
	Risk          float64
	CapabilityGap float64
	Evidence      float64
	TimeToLearn   float64
	PublicValue   float64
	Score         float64
	Portfolio     float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func strategicScore(x StrategicOption) float64 {
	return 0.17*x.Desirability +
		0.13*x.Feasibility +
		0.13*x.Viability +
		0.16*x.Alignment +
		0.11*x.Ethics +
		0.10*x.Learning +
		0.08*x.PublicValue +
		0.05*x.Evidence*10.0 -
		0.03*x.Risk -
		0.02*x.Effort -
		0.01*x.CapabilityGap -
		0.01*x.TimeToLearn
}

func portfolioValue(x StrategicOption) float64 {
	return x.Score + 0.30*x.Learning + 0.20*x.PublicValue + 0.15*x.Evidence*10.0 -
		0.22*x.Risk - 0.14*x.Effort - 0.10*x.CapabilityGap
}

func loadOptions(path string) []StrategicOption {
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

	var items []StrategicOption

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 15 {
			log.Fatalf("malformed row: %v", row)
		}

		x := StrategicOption{
			Name:          row[0],
			Desirability:  parseFloat(row[3]),
			Feasibility:   parseFloat(row[4]),
			Viability:     parseFloat(row[5]),
			Alignment:     parseFloat(row[6]),
			Ethics:        parseFloat(row[7]),
			Learning:      parseFloat(row[8]),
			Effort:        parseFloat(row[9]),
			Risk:          parseFloat(row[10]),
			CapabilityGap: parseFloat(row[11]),
			Evidence:      parseFloat(row[12]),
			TimeToLearn:   parseFloat(row[13]),
			PublicValue:   parseFloat(row[14]),
		}
		x.Score = strategicScore(x)
		x.Portfolio = portfolioValue(x)
		items = append(items, x)
	}

	return items
}

func main() {
	path := "../data/raw/strategic_options_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	items := loadOptions(path)

	sort.Slice(items, func(i, j int) bool {
		return items[i].Score > items[j].Score
	})

	fmt.Println("rank,option,strategic_score,portfolio_value,strategic_risk")
	for i, x := range items {
		fmt.Printf("%d,%s,%.6f,%.6f,%.6f\n", i+1, x.Name, x.Score, x.Portfolio, x.Risk)
	}
}
