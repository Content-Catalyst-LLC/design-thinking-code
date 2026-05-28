package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type ThemeAggregate struct {
	Theme          string
	EvidenceUnits  int
	TotalStrength  float64
	TotalRisk      float64
	Confidence     float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func main() {
	path := "../data/raw/contextual_inquiry_evidence_units_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

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

	aggregates := map[string]*ThemeAggregate{}

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 7 {
			continue
		}

		theme := row[3]
		strength := parseFloat(row[5])
		risk := parseFloat(row[6])

		if _, ok := aggregates[theme]; !ok {
			aggregates[theme] = &ThemeAggregate{Theme: theme}
		}

		aggregates[theme].EvidenceUnits++
		aggregates[theme].TotalStrength += strength
		aggregates[theme].TotalRisk += risk
	}

	var out []ThemeAggregate
	for _, agg := range aggregates {
		meanStrength := agg.TotalStrength / float64(agg.EvidenceUnits)
		meanRisk := agg.TotalRisk / float64(agg.EvidenceUnits)
		agg.Confidence = 0.70*meanStrength - 0.30*meanRisk
		out = append(out, *agg)
	}

	sort.Slice(out, func(i, j int) bool {
		return out[i].Confidence > out[j].Confidence
	})

	fmt.Println("rank,theme,evidence_units,synthesis_confidence")
	for i, row := range out {
		fmt.Printf("%d,%s,%d,%.6f\n", i+1, row.Theme, row.EvidenceUnits, row.Confidence)
	}
}
