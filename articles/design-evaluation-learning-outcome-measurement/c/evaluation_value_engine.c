#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ITEMS 128
#define MAX_LINE 512
#define MAX_NAME 180

typedef struct {
    char name[MAX_NAME];
    double outcome_improvement;
    double burden_reduction;
    double equity_performance;
    double trust_improvement;
    double durability;
    double operational_cost;
    double residual_risk;
    double penalty;
    double evaluation_value;
} Intervention;

double compute_penalty(const Intervention *x) {
    return 0.50 * x->operational_cost + 0.50 * x->residual_risk;
}

double compute_evaluation_value(const Intervention *x) {
    return 0.24 * x->outcome_improvement +
           0.20 * x->burden_reduction +
           0.20 * x->equity_performance +
           0.16 * x->trust_improvement +
           0.14 * x->durability -
           0.06 * x->penalty;
}

int compare_desc(const void *a, const void *b) {
    const Intervention *ia = (const Intervention *)a;
    const Intervention *ib = (const Intervention *)b;

    if (ia->evaluation_value < ib->evaluation_value) return 1;
    if (ia->evaluation_value > ib->evaluation_value) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/evaluation_portfolio_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    Intervention interventions[MAX_ITEMS];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file); /* header */

    while (fgets(line, sizeof(line), file) && count < MAX_ITEMS) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(interventions[count].name, token, MAX_NAME - 1);
        interventions[count].name[MAX_NAME - 1] = '\0';

        strtok(NULL, ","); /* intervention_type */
        strtok(NULL, ","); /* evaluation_stage */

        token = strtok(NULL, ",");
        interventions[count].outcome_improvement = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].burden_reduction = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].equity_performance = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].trust_improvement = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].durability = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].operational_cost = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].residual_risk = token ? atof(token) : 0.0;

        interventions[count].penalty = compute_penalty(&interventions[count]);
        interventions[count].evaluation_value = compute_evaluation_value(&interventions[count]);

        count++;
    }

    fclose(file);

    qsort(interventions, count, sizeof(Intervention), compare_desc);

    printf("rank,intervention,evaluation_value,penalty\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f,%.6f\n", i + 1, interventions[i].name, interventions[i].evaluation_value, interventions[i].penalty);
    }

    return 0;
}
