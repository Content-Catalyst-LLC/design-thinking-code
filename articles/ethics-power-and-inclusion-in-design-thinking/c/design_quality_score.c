#include <stdio.h>

// Toy responsible design quality score.
// Educational only.
// Compile with: cc c/design_quality_score.c -o outputs/design_quality_score

double design_quality_score(double human_relevance, double interpretive_rigor, double system_fit, double evidence_strength, double feasibility, double equity, double risk) {
    return 0.16 * human_relevance + 0.16 * interpretive_rigor + 0.15 * system_fit + 0.15 * evidence_strength + 0.14 * feasibility + 0.14 * equity - 0.18 * risk;
}

int main(void) {
    double score = design_quality_score(0.85, 0.78, 0.70, 0.74, 0.72, 0.80, 0.30);
    printf("Responsible design quality score: %.3f\n", score);
    return 0;
}
