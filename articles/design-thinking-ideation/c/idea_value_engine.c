#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_IDEAS 128
#define MAX_LINE 512
#define MAX_NAME 180

typedef struct {
    char name[MAX_NAME];
    double desirability;
    double feasibility;
    double novelty;
    double equity_value;
    double learning_value;
    double residual_risk;
    double value;
} Idea;

double idea_value(const Idea *idea) {
    const double wd = 0.24;
    const double wf = 0.18;
    const double wn = 0.18;
    const double we = 0.18;
    const double wl = 0.12;
    const double wr = 0.10;

    return wd * idea->desirability
         + wf * idea->feasibility
         + wn * idea->novelty
         + we * idea->equity_value
         + wl * idea->learning_value
         - wr * idea->residual_risk;
}

int compare_desc(const void *a, const void *b) {
    const Idea *ia = (const Idea *)a;
    const Idea *ib = (const Idea *)b;

    if (ia->value < ib->value) return 1;
    if (ia->value > ib->value) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/idea_portfolio_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    Idea ideas[MAX_IDEAS];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file); /* header */

    while (fgets(line, sizeof(line), file) && count < MAX_IDEAS) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(ideas[count].name, token, MAX_NAME - 1);
        ideas[count].name[MAX_NAME - 1] = '\0';

        strtok(NULL, ","); /* idea_cluster */

        token = strtok(NULL, ",");
        ideas[count].desirability = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        ideas[count].feasibility = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        ideas[count].novelty = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        ideas[count].equity_value = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        ideas[count].learning_value = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        ideas[count].residual_risk = token ? atof(token) : 0.0;

        ideas[count].value = idea_value(&ideas[count]);
        count++;
    }

    fclose(file);

    qsort(ideas, count, sizeof(Idea), compare_desc);

    printf("rank,idea,idea_value\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f\n", i + 1, ideas[i].name, ideas[i].value);
    }

    return 0;
}
