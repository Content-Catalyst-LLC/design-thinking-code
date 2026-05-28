#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_CONCEPTS 128
#define MAX_LINE 512
#define MAX_NAME 180

typedef struct {
    char name[MAX_NAME];
    double desirability;
    double feasibility;
    double viability;
    double responsibility;
    double friction;
    double residual_risk;
    double combined_risk;
    double validation_value;
} Concept;

double compute_combined_risk(const Concept *c) {
    return 0.50 * c->friction + 0.50 * c->residual_risk;
}

double compute_validation_value(const Concept *c) {
    return 0.25 * c->desirability +
           0.20 * c->feasibility +
           0.20 * c->viability +
           0.20 * c->responsibility -
           0.15 * c->combined_risk;
}

int compare_desc(const void *a, const void *b) {
    const Concept *ca = (const Concept *)a;
    const Concept *cb = (const Concept *)b;

    if (ca->validation_value < cb->validation_value) return 1;
    if (ca->validation_value > cb->validation_value) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/validation_concepts_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    Concept concepts[MAX_CONCEPTS];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file); /* header */

    while (fgets(line, sizeof(line), file) && count < MAX_CONCEPTS) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(concepts[count].name, token, MAX_NAME - 1);
        concepts[count].name[MAX_NAME - 1] = '\0';

        strtok(NULL, ","); /* prototype_type */
        strtok(NULL, ","); /* fidelity_level */

        token = strtok(NULL, ",");
        concepts[count].desirability = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        concepts[count].feasibility = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        concepts[count].viability = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        concepts[count].responsibility = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        concepts[count].friction = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        concepts[count].residual_risk = token ? atof(token) : 0.0;

        concepts[count].combined_risk = compute_combined_risk(&concepts[count]);
        concepts[count].validation_value = compute_validation_value(&concepts[count]);

        count++;
    }

    fclose(file);

    qsort(concepts, count, sizeof(Concept), compare_desc);

    printf("rank,concept,validation_value,combined_risk\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f,%.6f\n", i + 1, concepts[i].name, concepts[i].validation_value, concepts[i].combined_risk);
    }

    return 0;
}
