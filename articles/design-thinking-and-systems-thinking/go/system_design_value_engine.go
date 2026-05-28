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
	Name              string
	HumanValue        float64
	SystemLeverage    float64
	Feasibility       float64
	EquitySensitivity float64
	Durability        float64
	Risk              float64
	SystemDesignValue float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func systemDesignValue(x Intervention) float64 {
	return 0.24*x.HumanValue +
		0.26*x.SystemLeverage +
		0.18*x.Feasibility +
		0.14*x.EquitySensitivity +
		0.12*x.Durability -
		0.06*x.Risk
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
		if len(row) < 9 {
			log.Fatalf("malformed row: %v", row)
		}

		x := Intervention{
			Name:              row[0],
			HumanValue:        parseFloat(row[3]),
			SystemLeverage:    parseFloat(row[4]),
			Feasibility:       parseFloat(row[5]),
			EquitySensitivity: parseFloat(row[6]),
			Durability:        parseFloat(row[7]),
			Risk:              parseFloat(row[8]),
		}
		x.SystemDesignValue = systemDesignValue(x)
		items = append(items, x)
	}

	return items
}

func main() {
	path := "../data/raw/system_intervention_portfolio_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	items := loadPortfolio(path)

	sort.Slice(items, func(i, j int) bool {
		return items[i].SystemDesignValue > items[j].SystemDesignValue
	})

	fmt.Println("rank,intervention,system_design_value,risk")
	for i, x := range items {
		fmt.Printf("%d,%s,%.6f,%.6f\n", i+1, x.Name, x.SystemDesignValue, x.Risk)
	}
}
