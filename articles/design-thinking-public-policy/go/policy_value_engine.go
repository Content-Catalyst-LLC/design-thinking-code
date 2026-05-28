package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type PolicyPilot struct {
	Name            string
	Accessibility   float64
	Feasibility     float64
	Legitimacy      float64
	Equity          float64
	BurdenReduction float64
	Durability      float64
	Risk            float64
	PolicyValue     float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func policyValue(x PolicyPilot) float64 {
	return 0.20*x.Accessibility +
		0.16*x.Feasibility +
		0.16*x.Legitimacy +
		0.20*x.Equity +
		0.14*x.BurdenReduction +
		0.08*x.Durability -
		0.06*x.Risk
}

func loadPilots(path string) []PolicyPilot {
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

	var items []PolicyPilot

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 10 {
			log.Fatalf("malformed row: %v", row)
		}

		x := PolicyPilot{
			Name:            row[0],
			Accessibility:   parseFloat(row[3]),
			Feasibility:     parseFloat(row[4]),
			Legitimacy:      parseFloat(row[5]),
			Equity:          parseFloat(row[6]),
			BurdenReduction: parseFloat(row[7]),
			Durability:      parseFloat(row[8]),
			Risk:            parseFloat(row[9]),
		}
		x.PolicyValue = policyValue(x)
		items = append(items, x)
	}

	return items
}

func main() {
	path := "../data/raw/public_policy_pilots_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	items := loadPilots(path)

	sort.Slice(items, func(i, j int) bool {
		return items[i].PolicyValue > items[j].PolicyValue
	})

	fmt.Println("rank,pilot,policy_value,risk")
	for i, x := range items {
		fmt.Printf("%d,%s,%.6f,%.6f\n", i+1, x.Name, x.PolicyValue, x.Risk)
	}
}
