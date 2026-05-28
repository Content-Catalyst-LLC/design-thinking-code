#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ITEMS 160
#define MAX_LINE 640
#define MAX_NAME 220

typedef struct {
    char name[MAX_NAME];
    double desirability;
    double feasibility;
    double viability;
    double equity;
    double learning_value;
    double implementation_readiness;
    double risk;
    double design_value;
} InnovationConcept;

double compute_design_value(const InnovationConcept *x) {
    return 0.22 * x->desirability +
           0.16 * x->feasibility +
           0.16 * x->viability +
           0.18 * x->equity +
           0.12 * x->learning_value +
           0.10 * x->implementation_readiness -
           0.06 * x->risk;
}

int compare_desc(const void *a, const void *b) {
    const InnovationConcept *ia = (const InnovationConcept *)a;
    const InnovationConcept *ib = (const InnovationConcept *)b;

    if (ia->design_value < ib->design_value) return 1;
    if (ia->design_value > ib->design_value) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/organizational_innovation_concepts_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    InnovationConcept concepts[MAX_ITEMS];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file); /* header */

    while (fgets(line, sizeof(line), file) && count < MAX_ITEMS) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(concepts[count].name, token, MAX_NAME - 1);
        concepts[count].name[MAX_NAME - 1] = '\0';

        strtok(NULL, ","); /* concept_type */
        strtok(NULL, ","); /* organizational_domain */

        token = strtok(NULL, ",");
        concepts[count].desirability = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        concepts[count].feasibility = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        concepts[count].viability = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        concepts[count].equity = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        concepts[count].learning_value = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        concepts[count].implementation_readiness = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        concepts[count].risk = token ? atof(token) : 0.0;

        concepts[count].design_value = compute_design_value(&concepts[count]);

        count++;
    }

    fclose(file);

    qsort(concepts, count, sizeof(InnovationConcept), compare_desc);

    printf("rank,concept,design_value,risk\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f,%.6f\n", i + 1, concepts[i].name, concepts[i].design_value, concepts[i].risk);
    }

    return 0;
}
