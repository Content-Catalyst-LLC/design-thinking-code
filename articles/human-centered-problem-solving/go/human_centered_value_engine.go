package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type DesignOption struct {
	Name           string
	HumanBenefit   float64
	Usability      float64
	StakeholderFit float64
	Burden         float64
	Value          float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func humanCenteredValue(option DesignOption) float64 {
	return 0.30*option.HumanBenefit +
		0.25*option.Usability +
		0.30*option.StakeholderFit -
		0.15*option.Burden
}

func loadOptions(path string) []DesignOption {
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

	var options []DesignOption

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 5 {
			log.Fatalf("malformed row: %v", row)
		}

		option := DesignOption{
			Name:           row[0],
			HumanBenefit:   parseFloat(row[1]),
			Usability:      parseFloat(row[2]),
			StakeholderFit: parseFloat(row[3]),
			Burden:         parseFloat(row[4]),
		}
		option.Value = humanCenteredValue(option)
		options = append(options, option)
	}

	return options
}

func main() {
	path := "../data/raw/human_centered_options_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	options := loadOptions(path)

	sort.Slice(options, func(i, j int) bool {
		return options[i].Value > options[j].Value
	})

	fmt.Println("rank,option,hc_value")
	for i, option := range options {
		fmt.Printf("%d,%s,%.6f\n", i+1, option.Name, option.Value)
	}
}
