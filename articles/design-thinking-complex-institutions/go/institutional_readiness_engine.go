package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type OptionItem struct {
	Name               string
	Desirability       float64
	Authority          float64
	Capability         float64
	Funding            float64
	PolicyFit          float64
	Governance         float64
	TrustGain          float64
	BurdenReduction    float64
	Coordination       float64
	ImplementationRisk float64
	DataReadiness      float64
	FrontlineFit       float64
	Maintenance        float64
	Equity             float64
	PublicValue        float64
	Readiness          float64
	Absorption         float64
	PublicPriority     float64
	SequencingNeed     float64
	PortfolioScore     float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func computeScores(x *OptionItem) {
	x.Readiness =
		0.14*x.Desirability +
			0.13*x.Authority +
			0.12*x.Capability +
			0.10*x.Funding +
			0.10*x.PolicyFit +
			0.11*x.Governance +
			0.08*x.TrustGain +
			0.08*x.BurdenReduction +
			0.06*x.DataReadiness +
			0.05*x.FrontlineFit +
			0.03*x.Maintenance -
			0.05*x.Coordination -
			0.05*x.ImplementationRisk

	x.Absorption =
		0.18*x.Authority +
			0.18*x.Capability +
			0.14*x.Funding +
			0.14*x.Governance +
			0.12*x.PolicyFit +
			0.10*x.FrontlineFit +
			0.08*x.Maintenance +
			0.06*x.DataReadiness

	x.PublicPriority =
		0.24*x.PublicValue +
			0.20*x.BurdenReduction +
			0.18*x.TrustGain +
			0.16*x.Equity +
			0.12*x.Desirability +
			0.10*x.PolicyFit -
			0.08*x.ImplementationRisk

	x.SequencingNeed =
		0.28*x.Coordination +
			0.24*x.ImplementationRisk +
			0.14*(10.0-x.Authority) +
			0.12*(10.0-x.Capability) +
			0.10*(10.0-x.Funding) +
			0.07*(10.0-x.Maintenance) +
			0.05*(10.0-x.DataReadiness)

	x.PortfolioScore =
		0.30*x.Readiness +
			0.26*x.PublicPriority +
			0.20*x.Absorption +
			0.10*x.Equity +
			0.06*x.TrustGain -
			0.12*x.SequencingNeed -
			0.08*x.ImplementationRisk
}

func loadOptions(path string) []OptionItem {
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

	var items []OptionItem

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 17 {
			log.Fatalf("malformed row: %v", row)
		}

		x := OptionItem{
			Name:               row[0],
			Desirability:       parseFloat(row[2]),
			Authority:          parseFloat(row[3]),
			Capability:         parseFloat(row[4]),
			Funding:            parseFloat(row[5]),
			PolicyFit:          parseFloat(row[6]),
			Governance:         parseFloat(row[7]),
			TrustGain:          parseFloat(row[8]),
			BurdenReduction:    parseFloat(row[9]),
			Coordination:       parseFloat(row[10]),
			ImplementationRisk: parseFloat(row[11]),
			DataReadiness:      parseFloat(row[12]),
			FrontlineFit:       parseFloat(row[13]),
			Maintenance:        parseFloat(row[14]),
			Equity:             parseFloat(row[15]),
			PublicValue:        parseFloat(row[16]),
		}
		computeScores(&x)
		items = append(items, x)
	}

	return items
}

func main() {
	path := "../data/raw/institutional_design_options_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	items := loadOptions(path)

	sort.Slice(items, func(i, j int) bool {
		return items[i].PortfolioScore > items[j].PortfolioScore
	})

	fmt.Println("rank,option,change_readiness,absorption_capacity,public_value_priority,sequencing_need,portfolio_score")
	for i, x := range items {
		fmt.Printf("%d,%s,%.6f,%.6f,%.6f,%.6f,%.6f\n",
			i+1,
			x.Name,
			x.Readiness,
			x.Absorption,
			x.PublicPriority,
			x.SequencingNeed,
			x.PortfolioScore,
		)
	}
}
