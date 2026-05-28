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
	Access             float64
	Equity             float64
	Dignity            float64
	Legitimacy         float64
	Accountability     float64
	OutcomeStrength    float64
	Sustainability     float64
	Learning           float64
	Feasibility        float64
	Governance         float64
	ImplementationRisk float64
	BurdenRisk         float64
	Participation      float64
	CommunityValue     float64
	Repair             float64
	Stewardship        float64
	PublicValue        float64
	Readiness          float64
	StewardshipNeed    float64
	PortfolioPriority  float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func computeScores(x *Intervention) {
	x.PublicValue =
		0.13*x.Access +
			0.15*x.Equity +
			0.12*x.Dignity +
			0.12*x.Legitimacy +
			0.13*x.Accountability +
			0.11*x.OutcomeStrength +
			0.08*x.Sustainability +
			0.07*x.Learning +
			0.05*x.CommunityValue +
			0.04*x.Repair

	x.Readiness =
		0.30*x.PublicValue +
			0.17*x.Feasibility +
			0.16*x.Governance +
			0.12*x.Learning +
			0.10*x.Participation +
			0.08*x.Stewardship +
			0.07*x.Repair -
			0.07*x.ImplementationRisk -
			0.07*x.BurdenRisk

	x.StewardshipNeed =
		0.24*x.ImplementationRisk +
			0.22*x.BurdenRisk +
			0.16*(10.0-x.Governance) +
			0.12*(10.0-x.Sustainability) +
			0.10*(10.0-x.Learning) +
			0.08*(10.0-x.Repair) +
			0.08*(10.0-x.Stewardship)

	x.PortfolioPriority =
		0.36*x.PublicValue +
			0.28*x.Readiness +
			0.14*x.Equity +
			0.10*x.CommunityValue +
			0.06*x.Participation -
			0.14*x.StewardshipNeed -
			0.06*x.ImplementationRisk
}

func loadInterventions(path string) []Intervention {
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
		if len(row) < 18 {
			log.Fatalf("malformed row: %v", row)
		}

		x := Intervention{
			Name:               row[0],
			Access:             parseFloat(row[2]),
			Equity:             parseFloat(row[3]),
			Dignity:            parseFloat(row[4]),
			Legitimacy:         parseFloat(row[5]),
			Accountability:     parseFloat(row[6]),
			OutcomeStrength:    parseFloat(row[7]),
			Sustainability:     parseFloat(row[8]),
			Learning:           parseFloat(row[9]),
			Feasibility:        parseFloat(row[10]),
			Governance:         parseFloat(row[11]),
			ImplementationRisk: parseFloat(row[12]),
			BurdenRisk:         parseFloat(row[13]),
			Participation:      parseFloat(row[14]),
			CommunityValue:     parseFloat(row[15]),
			Repair:             parseFloat(row[16]),
			Stewardship:        parseFloat(row[17]),
		}
		computeScores(&x)
		items = append(items, x)
	}

	return items
}

func main() {
	path := "../data/raw/social_impact_interventions_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	items := loadInterventions(path)

	sort.Slice(items, func(i, j int) bool {
		return items[i].PortfolioPriority > items[j].PortfolioPriority
	})

	fmt.Println("rank,intervention,public_value_score,impact_readiness,stewardship_need,portfolio_priority")
	for i, x := range items {
		fmt.Printf("%d,%s,%.6f,%.6f,%.6f,%.6f\n",
			i+1,
			x.Name,
			x.PublicValue,
			x.Readiness,
			x.StewardshipNeed,
			x.PortfolioPriority,
		)
	}
}
