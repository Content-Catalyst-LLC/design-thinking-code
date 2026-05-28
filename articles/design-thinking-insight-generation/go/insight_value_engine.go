package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type Insight struct {
	Name             string
	PatternSupport   float64
	ExplanatoryDepth float64
	OpportunityValue float64
	InterpretiveRisk float64
	Value            float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func insightValue(insight Insight) float64 {
	return 0.30*insight.PatternSupport +
		0.30*insight.ExplanatoryDepth +
		0.25*insight.OpportunityValue -
		0.15*insight.InterpretiveRisk
}

func loadInsights(path string) []Insight {
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

	var insights []Insight

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 5 {
			log.Fatalf("malformed row: %v", row)
		}

		insight := Insight{
			Name:             row[0],
			PatternSupport:   parseFloat(row[1]),
			ExplanatoryDepth: parseFloat(row[2]),
			OpportunityValue: parseFloat(row[3]),
			InterpretiveRisk: parseFloat(row[4]),
		}
		insight.Value = insightValue(insight)
		insights = append(insights, insight)
	}

	return insights
}

func main() {
	path := "../data/raw/candidate_insights_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	insights := loadInsights(path)

	sort.Slice(insights, func(i, j int) bool {
		return insights[i].Value > insights[j].Value
	})

	fmt.Println("rank,insight,insight_value")
	for i, insight := range insights {
		fmt.Printf("%d,%s,%.6f\n", i+1, insight.Name, insight.Value)
	}
}
