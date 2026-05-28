#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ITEMS 128
#define MAX_LINE 512
#define MAX_NAME 180

typedef struct {
    char name[MAX_NAME];
    double adoption_readiness;
    double operational_fit;
    double durability;
    double governance_readiness;
    double equity_readiness;
    double financial_sustainability;
    double operational_risk;
    double governance_risk;
    double technical_risk;
    double equity_risk;
    double financial_risk;
    double composite_risk;
    double implementation_value;
} Intervention;

double compute_composite_risk(const Intervention *x) {
    return 0.25 * x->operational_risk +
           0.22 * x->governance_risk +
           0.18 * x->technical_risk +
           0.22 * x->equity_risk +
           0.13 * x->financial_risk;
}

double compute_implementation_value(const Intervention *x) {
    return 0.20 * x->adoption_readiness +
           0.18 * x->operational_fit +
           0.18 * x->durability +
           0.15 * x->governance_readiness +
           0.14 * x->equity_readiness +
           0.10 * x->financial_sustainability -
           0.05 * x->composite_risk;
}

int compare_desc(const void *a, const void *b) {
    const Intervention *ia = (const Intervention *)a;
    const Intervention *ib = (const Intervention *)b;

    if (ia->implementation_value < ib->implementation_value) return 1;
    if (ia->implementation_value > ib->implementation_value) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/implementation_portfolio_raw.csv";
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
        strtok(NULL, ","); /* implementation_stage */

        token = strtok(NULL, ",");
        interventions[count].adoption_readiness = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].operational_fit = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].durability = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].governance_readiness = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].equity_readiness = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].financial_sustainability = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].operational_risk = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].governance_risk = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].technical_risk = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].equity_risk = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].financial_risk = token ? atof(token) : 0.0;

        interventions[count].composite_risk = compute_composite_risk(&interventions[count]);
        interventions[count].implementation_value = compute_implementation_value(&interventions[count]);

        count++;
    }

    fclose(file);

    qsort(interventions, count, sizeof(Intervention), compare_desc);

    printf("rank,intervention,implementation_value,composite_risk\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f,%.6f\n", i + 1, interventions[i].name, interventions[i].implementation_value, interventions[i].composite_risk);
    }

    return 0;
}
