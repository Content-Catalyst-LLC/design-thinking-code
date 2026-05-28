#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ITEMS 160
#define MAX_LINE 640
#define MAX_NAME 220

typedef struct {
    char name[MAX_NAME];
    double usability;
    double feasibility;
    double ecological_benefit;
    double circularity;
    double equity;
    double durability;
    double risk;
    double sustainability_value;
} Concept;

double compute_sustainability_value(const Concept *x) {
    return 0.16 * x->usability +
           0.16 * x->feasibility +
           0.24 * x->ecological_benefit +
           0.16 * x->circularity +
           0.14 * x->equity +
           0.08 * x->durability -
           0.06 * x->risk;
}

int compare_desc(const void *a, const void *b) {
    const Concept *ia = (const Concept *)a;
    const Concept *ib = (const Concept *)b;

    if (ia->sustainability_value < ib->sustainability_value) return 1;
    if (ia->sustainability_value > ib->sustainability_value) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/sustainability_concepts_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    Concept concepts[MAX_ITEMS];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file); /* header */

    while (fgets(line, sizeof(line), file) && count < MAX_ITEMS) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(concepts[count].name, token, MAX_NAME - 1);
        concepts[count].name[MAX_NAME - 1] = '\0';

        strtok(NULL, ","); /* concept_type */
        strtok(NULL, ","); /* transition_domain */

        token = strtok(NULL, ",");
        concepts[count].usability = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        concepts[count].feasibility = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        concepts[count].ecological_benefit = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        concepts[count].circularity = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        concepts[count].equity = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        concepts[count].durability = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        concepts[count].risk = token ? atof(token) : 0.0;

        concepts[count].sustainability_value = compute_sustainability_value(&concepts[count]);

        count++;
    }

    fclose(file);

    qsort(concepts, count, sizeof(Concept), compare_desc);

    printf("rank,concept,sustainability_value,risk\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f,%.6f\n", i + 1, concepts[i].name, concepts[i].sustainability_value, concepts[i].risk);
    }

    return 0;
}
