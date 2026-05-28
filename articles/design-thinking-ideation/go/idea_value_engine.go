package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type Idea struct {
	Name          string
	Desirability  float64
	Feasibility   float64
	Novelty       float64
	EquityValue   float64
	LearningValue float64
	ResidualRisk  float64
	Value         float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func ideaValue(idea Idea) float64 {
	return 0.24*idea.Desirability +
		0.18*idea.Feasibility +
		0.18*idea.Novelty +
		0.18*idea.EquityValue +
		0.12*idea.LearningValue -
		0.10*idea.ResidualRisk
}

func loadIdeas(path string) []Idea {
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

	var ideas []Idea

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 8 {
			log.Fatalf("malformed row: %v", row)
		}

		idea := Idea{
			Name:          row[0],
			Desirability:  parseFloat(row[2]),
			Feasibility:   parseFloat(row[3]),
			Novelty:       parseFloat(row[4]),
			EquityValue:   parseFloat(row[5]),
			LearningValue: parseFloat(row[6]),
			ResidualRisk:  parseFloat(row[7]),
		}
		idea.Value = ideaValue(idea)
		ideas = append(ideas, idea)
	}

	return ideas
}

func main() {
	path := "../data/raw/idea_portfolio_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	ideas := loadIdeas(path)

	sort.Slice(ideas, func(i, j int) bool {
		return ideas[i].Value > ideas[j].Value
	})

	fmt.Println("rank,idea,idea_value")
	for i, idea := range ideas {
		fmt.Printf("%d,%s,%.6f\n", i+1, idea.Name, idea.Value)
	}
}
