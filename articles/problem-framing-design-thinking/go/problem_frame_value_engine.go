package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"sort"
	"strconv"
)

type ProblemFrame struct {
	Name                 string
	ExplanatoryAdequacy  float64
	StakeholderCoverage  float64
	OpportunityValue     float64
	FramingRisk          float64
	Value                float64
}

func parseFloat(value string) float64 {
	parsed, err := strconv.ParseFloat(value, 64)
	if err != nil {
		log.Fatalf("unable to parse numeric value %q: %v", value, err)
	}
	return parsed
}

func frameValue(frame ProblemFrame) float64 {
	return 0.30*frame.ExplanatoryAdequacy +
		0.25*frame.StakeholderCoverage +
		0.30*frame.OpportunityValue -
		0.15*frame.FramingRisk
}

func loadFrames(path string) []ProblemFrame {
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

	var frames []ProblemFrame

	for i, row := range rows {
		if i == 0 {
			continue
		}
		if len(row) < 5 {
			log.Fatalf("malformed row: %v", row)
		}

		frame := ProblemFrame{
			Name:                row[0],
			ExplanatoryAdequacy: parseFloat(row[1]),
			StakeholderCoverage: parseFloat(row[2]),
			OpportunityValue:    parseFloat(row[3]),
			FramingRisk:         parseFloat(row[4]),
		}
		frame.Value = frameValue(frame)
		frames = append(frames, frame)
	}

	return frames
}

func main() {
	path := "../data/raw/problem_frames_raw.csv"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}

	frames := loadFrames(path)

	sort.Slice(frames, func(i, j int) bool {
		return frames[i].Value > frames[j].Value
	})

	fmt.Println("rank,frame,frame_value")
	for i, frame := range frames {
		fmt.Printf("%d,%s,%.6f\n", i+1, frame.Name, frame.Value)
	}
}
