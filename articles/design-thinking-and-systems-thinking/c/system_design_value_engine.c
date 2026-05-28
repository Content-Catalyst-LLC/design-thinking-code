#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ITEMS 128
#define MAX_LINE 512
#define MAX_NAME 180

typedef struct {
    char name[MAX_NAME];
    double human_value;
    double system_leverage;
    double feasibility;
    double equity_sensitivity;
    double durability;
    double risk;
    double system_design_value;
} Intervention;

double compute_system_design_value(const Intervention *x) {
    return 0.24 * x->human_value +
           0.26 * x->system_leverage +
           0.18 * x->feasibility +
           0.14 * x->equity_sensitivity +
           0.12 * x->durability -
           0.06 * x->risk;
}

int compare_desc(const void *a, const void *b) {
    const Intervention *ia = (const Intervention *)a;
    const Intervention *ib = (const Intervention *)b;

    if (ia->system_design_value < ib->system_design_value) return 1;
    if (ia->system_design_value > ib->system_design_value) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/system_intervention_portfolio_raw.csv";
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
        strtok(NULL, ","); /* leverage_level */

        token = strtok(NULL, ",");
        interventions[count].human_value = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].system_leverage = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].feasibility = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].equity_sensitivity = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].durability = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        interventions[count].risk = token ? atof(token) : 0.0;

        interventions[count].system_design_value = compute_system_design_value(&interventions[count]);

        count++;
    }

    fclose(file);

    qsort(interventions, count, sizeof(Intervention), compare_desc);

    printf("rank,intervention,system_design_value,risk\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f,%.6f\n", i + 1, interventions[i].name, interventions[i].system_design_value, interventions[i].risk);
    }

    return 0;
}
