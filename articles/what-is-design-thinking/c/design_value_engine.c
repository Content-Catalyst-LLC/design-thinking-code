#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_PATHWAYS 128
#define MAX_LINE 512
#define MAX_NAME 128

typedef struct {
    char name[MAX_NAME];
    double human_relevance;
    double feasibility;
    double learning_value;
    double residual_risk;
    double value;
} Pathway;

double design_value(const Pathway *p) {
    const double wh = 0.35;
    const double wf = 0.25;
    const double wl = 0.25;
    const double wr = 0.15;

    return wh * p->human_relevance
         + wf * p->feasibility
         + wl * p->learning_value
         - wr * p->residual_risk;
}

int compare_desc(const void *a, const void *b) {
    const Pathway *pa = (const Pathway *)a;
    const Pathway *pb = (const Pathway *)b;

    if (pa->value < pb->value) return 1;
    if (pa->value > pb->value) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/design_pathways_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    Pathway pathways[MAX_PATHWAYS];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file); /* header */

    while (fgets(line, sizeof(line), file) && count < MAX_PATHWAYS) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(pathways[count].name, token, MAX_NAME - 1);
        pathways[count].name[MAX_NAME - 1] = '\0';

        token = strtok(NULL, ",");
        pathways[count].human_relevance = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        pathways[count].feasibility = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        pathways[count].learning_value = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        pathways[count].residual_risk = token ? atof(token) : 0.0;

        pathways[count].value = design_value(&pathways[count]);
        count++;
    }

    fclose(file);

    qsort(pathways, count, sizeof(Pathway), compare_desc);

    printf("rank,pathway,design_value\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f\n", i + 1, pathways[i].name, pathways[i].value);
    }

    return 0;
}
