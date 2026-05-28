package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type CodesignActivity struct {
	Name                         string
	Representation               float64
	Accessibility                float64
	ParticipantInfluence         float64
	TrustQuality                 float64
	EvidenceQuality              float64
	ImplementationAccountability float64
	DecisionImpact               float64
	EthicalRisk                  float64
	ParticipationQuality         float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func participationQuality(x CodesignActivity) float64 {
	return 0.18*x.Representation +
		0.14*x.Accessibility +
		0.22*x.ParticipantInfluence +
		0.12*x.TrustQuality +
		0.12*x.EvidenceQuality +
		0.12*x.ImplementationAccountability +
		0.14*x.DecisionImpact -
		0.08*x.EthicalRisk
}

func loadActivities(path string) []CodesignActivity {
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

	var items []CodesignActivity

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 11 {
			log.Fatalf("malformed row: %v", row)
		}

		x := CodesignActivity{
			Name:                         row[0],
			Representation:               parseFloat(row[3]),
			Accessibility:                parseFloat(row[4]),
			ParticipantInfluence:         parseFloat(row[5]),
			TrustQuality:                 parseFloat(row[6]),
			EvidenceQuality:              parseFloat(row[7]),
			ImplementationAccountability: parseFloat(row[8]),
			DecisionImpact:               parseFloat(row[9]),
			EthicalRisk:                  parseFloat(row[10]),
		}
		x.ParticipationQuality = participationQuality(x)
		items = append(items, x)
	}

	return items
}

func main() {
	path := "../data/raw/codesign_activities_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	items := loadActivities(path)

	sort.Slice(items, func(i, j int) bool {
		return items[i].ParticipationQuality > items[j].ParticipationQuality
	})

	fmt.Println("rank,activity,participation_quality,ethical_risk")
	for i, x := range items {
		fmt.Printf("%d,%s,%.6f,%.6f\n", i+1, x.Name, x.ParticipationQuality, x.EthicalRisk)
	}
}
