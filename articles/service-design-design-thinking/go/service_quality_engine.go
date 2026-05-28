package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type ServiceStage struct {
	Name                  string
	CompletionProbability float64
	Clarity               float64
	Trust                 float64
	Accessibility         float64
	UserBurden            float64
	StaffLoad             float64
	RecoveryQuality       float64
	Quality               float64
	Priority              float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func quality(x ServiceStage) float64 {
	return 0.22*x.CompletionProbability*10.0 +
		0.18*x.Clarity +
		0.18*x.Trust +
		0.16*x.Accessibility +
		0.14*x.RecoveryQuality -
		0.07*x.UserBurden -
		0.05*x.StaffLoad
}

func priority(x ServiceStage) float64 {
	failureRisk := 1.0 - x.CompletionProbability
	burdenRisk := 0.55*x.UserBurden + 0.45*x.StaffLoad
	return 0.34*failureRisk*10.0 +
		0.26*burdenRisk +
		0.18*(10.0-x.Clarity) +
		0.12*(10.0-x.Accessibility) +
		0.10*(10.0-x.RecoveryQuality)
}

func loadStages(path string) []ServiceStage {
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

	var items []ServiceStage

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 10 {
			log.Fatalf("malformed row: %v", row)
		}

		x := ServiceStage{
			Name:                  row[0],
			CompletionProbability: parseFloat(row[3]),
			Clarity:               parseFloat(row[4]),
			Trust:                 parseFloat(row[5]),
			Accessibility:         parseFloat(row[6]),
			UserBurden:            parseFloat(row[7]),
			StaffLoad:             parseFloat(row[8]),
			RecoveryQuality:       parseFloat(row[9]),
		}
		x.Quality = quality(x)
		x.Priority = priority(x)
		items = append(items, x)
	}

	return items
}

func main() {
	path := "../data/raw/service_journey_stages_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	items := loadStages(path)
	reliability := 1.0
	for _, x := range items {
		reliability *= x.CompletionProbability
	}

	sort.Slice(items, func(i, j int) bool {
		return items[i].Priority > items[j].Priority
	})

	fmt.Printf("end_to_end_reliability,%.8f\n", reliability)
	fmt.Println("rank,stage,service_stage_quality,redesign_priority,completion_probability")
	for i, x := range items {
		fmt.Printf("%d,%s,%.6f,%.6f,%.6f\n", i+1, x.Name, x.Quality, x.Priority, x.CompletionProbability)
	}
}
