package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type ResearchSignal struct {
	Name                 string
	SourceStrength       float64
	Relevance            float64
	Traceability         float64
	Representativeness   float64
	Validation           float64
	Missingness          float64
	AIAssistanceRisk     float64
	DecisionRelevance    float64
	Recency              float64
	Consent              float64
	Coverage             float64
	Confidence           float64
	BiasRisk             float64
	AIRisk               float64
	DecisionReadiness    float64
	GovernancePriority   float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func clamp01(x float64) float64 {
	if x < 0.0 {
		return 0.0
	}
	if x > 1.0 {
		return 1.0
	}
	return x
}

func computeScores(x *ResearchSignal) {
	x.Confidence =
		0.18*x.SourceStrength +
			0.17*x.Relevance +
			0.15*x.Traceability +
			0.15*x.Representativeness +
			0.15*x.Validation +
			0.08*x.Recency +
			0.07*x.Consent +
			0.05*x.Coverage

	x.BiasRisk =
		0.26*x.Missingness +
			0.22*(1.0-x.Representativeness) +
			0.18*(1.0-x.Validation) +
			0.14*x.AIAssistanceRisk +
			0.10*(1.0-x.Traceability) +
			0.10*(1.0-x.Coverage)

	x.AIRisk =
		0.38*x.AIAssistanceRisk +
			0.18*(1.0-x.Traceability) +
			0.16*(1.0-x.Validation) +
			0.14*x.Missingness +
			0.14*(1.0-x.Consent)

	x.DecisionReadiness = clamp01(
		0.30*x.Confidence +
			0.24*x.DecisionRelevance +
			0.14*x.Validation +
			0.12*x.Traceability +
			0.08*x.Consent +
			0.08*x.Coverage -
			0.04*x.BiasRisk,
	)

	x.GovernancePriority =
		0.24*x.BiasRisk +
			0.22*x.AIRisk +
			0.16*(1.0-x.Traceability) +
			0.14*(1.0-x.Consent) +
			0.12*(1.0-x.Validation) +
			0.12*x.DecisionRelevance
}

func loadSignals(path string) []ResearchSignal {
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

	var items []ResearchSignal

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 13 {
			log.Fatalf("malformed row: %v", row)
		}

		x := ResearchSignal{
			Name:               row[0],
			SourceStrength:     parseFloat(row[2]),
			Relevance:          parseFloat(row[3]),
			Traceability:       parseFloat(row[4]),
			Representativeness: parseFloat(row[5]),
			Validation:         parseFloat(row[6]),
			Missingness:        parseFloat(row[7]),
			AIAssistanceRisk:   parseFloat(row[8]),
			DecisionRelevance:  parseFloat(row[9]),
			Recency:            parseFloat(row[10]),
			Consent:            parseFloat(row[11]),
			Coverage:           parseFloat(row[12]),
		}
		computeScores(&x)
		items = append(items, x)
	}

	return items
}

func main() {
	path := "../data/raw/research_signals_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	items := loadSignals(path)

	sort.Slice(items, func(i, j int) bool {
		return items[i].GovernancePriority > items[j].GovernancePriority
	})

	fmt.Println("rank,signal,confidence_score,bias_risk,ai_risk,decision_readiness,governance_priority")
	for i, x := range items {
		fmt.Printf("%d,%s,%.6f,%.6f,%.6f,%.6f,%.6f\n",
			i+1,
			x.Name,
			x.Confidence,
			x.BiasRisk,
			x.AIRisk,
			x.DecisionReadiness,
			x.GovernancePriority,
		)
	}
}
