package main

import "fmt"

func designValue(humanRelevance, feasibility, learningValue, residualRisk float64) float64 {
	return 0.35*humanRelevance + 0.25*feasibility + 0.25*learningValue - 0.15*residualRisk
}

func main() {
	score := designValue(8.8, 7.4, 8.1, 4.0)
	fmt.Printf("Design value: %.3f\n", score)
}
