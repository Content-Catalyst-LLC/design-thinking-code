#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ITEMS 200
#define MAX_LINE 1200
#define MAX_NAME 260

typedef struct {
    char name[MAX_NAME];
    double source_strength;
    double relevance;
    double traceability;
    double representativeness;
    double validation;
    double missingness;
    double ai_assistance_risk;
    double decision_relevance;
    double recency;
    double consent;
    double coverage;
    double confidence;
    double bias_risk;
    double ai_risk;
    double decision_readiness;
    double governance_priority;
} ResearchSignal;

double clamp01(double x) {
    if (x < 0.0) return 0.0;
    if (x > 1.0) return 1.0;
    return x;
}

void compute_scores(ResearchSignal *x) {
    x->confidence =
        0.18*x->source_strength +
        0.17*x->relevance +
        0.15*x->traceability +
        0.15*x->representativeness +
        0.15*x->validation +
        0.08*x->recency +
        0.07*x->consent +
        0.05*x->coverage;

    x->bias_risk =
        0.26*x->missingness +
        0.22*(1.0-x->representativeness) +
        0.18*(1.0-x->validation) +
        0.14*x->ai_assistance_risk +
        0.10*(1.0-x->traceability) +
        0.10*(1.0-x->coverage);

    x->ai_risk =
        0.38*x->ai_assistance_risk +
        0.18*(1.0-x->traceability) +
        0.16*(1.0-x->validation) +
        0.14*x->missingness +
        0.14*(1.0-x->consent);

    x->decision_readiness = clamp01(
        0.30*x->confidence +
        0.24*x->decision_relevance +
        0.14*x->validation +
        0.12*x->traceability +
        0.08*x->consent +
        0.08*x->coverage -
        0.04*x->bias_risk
    );

    x->governance_priority =
        0.24*x->bias_risk +
        0.22*x->ai_risk +
        0.16*(1.0-x->traceability) +
        0.14*(1.0-x->consent) +
        0.12*(1.0-x->validation) +
        0.12*x->decision_relevance;
}

int compare_desc(const void *a, const void *b) {
    const ResearchSignal *ia = (const ResearchSignal *)a;
    const ResearchSignal *ib = (const ResearchSignal *)b;
    if (ia->governance_priority < ib->governance_priority) return 1;
    if (ia->governance_priority > ib->governance_priority) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/research_signals_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    ResearchSignal items[MAX_ITEMS];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file);

    while (fgets(line, sizeof(line), file) && count < MAX_ITEMS) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(items[count].name, token, MAX_NAME - 1);
        items[count].name[MAX_NAME - 1] = '\0';

        strtok(NULL, ","); /* evidence_type */

        token = strtok(NULL, ","); items[count].source_strength = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].relevance = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].traceability = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].representativeness = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].validation = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].missingness = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].ai_assistance_risk = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].decision_relevance = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].recency = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].consent = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].coverage = token ? atof(token) : 0.0;

        compute_scores(&items[count]);
        count++;
    }

    fclose(file);
    qsort(items, count, sizeof(ResearchSignal), compare_desc);

    printf("rank,signal,confidence_score,bias_risk,ai_risk,decision_readiness,governance_priority\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f,%.6f,%.6f,%.6f,%.6f\n",
            i + 1,
            items[i].name,
            items[i].confidence,
            items[i].bias_risk,
            items[i].ai_risk,
            items[i].decision_readiness,
            items[i].governance_priority
        );
    }

    return 0;
}
