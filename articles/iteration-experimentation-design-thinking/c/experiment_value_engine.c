#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_EXPERIMENTS 128
#define MAX_LINE 512
#define MAX_NAME 128

typedef struct {
    char name[MAX_NAME];
    double learning_gain;
    double update_flexibility;
    double expected_improvement;
    double residual_risk;
    double value;
} Experiment;

double experiment_value(const Experiment *experiment) {
    const double wl = 0.35;
    const double wu = 0.25;
    const double we = 0.25;
    const double wr = 0.15;

    return wl * experiment->learning_gain
         + wu * experiment->update_flexibility
         + we * experiment->expected_improvement
         - wr * experiment->residual_risk;
}

int compare_desc(const void *a, const void *b) {
    const Experiment *ea = (const Experiment *)a;
    const Experiment *eb = (const Experiment *)b;

    if (ea->value < eb->value) return 1;
    if (ea->value > eb->value) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/experiments_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    Experiment experiments[MAX_EXPERIMENTS];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file); /* header */

    while (fgets(line, sizeof(line), file) && count < MAX_EXPERIMENTS) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(experiments[count].name, token, MAX_NAME - 1);
        experiments[count].name[MAX_NAME - 1] = '\0';

        token = strtok(NULL, ",");
        experiments[count].learning_gain = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        experiments[count].update_flexibility = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        experiments[count].expected_improvement = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        experiments[count].residual_risk = token ? atof(token) : 0.0;

        experiments[count].value = experiment_value(&experiments[count]);
        count++;
    }

    fclose(file);

    qsort(experiments, count, sizeof(Experiment), compare_desc);

    printf("rank,experiment,experiment_value\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f\n", i + 1, experiments[i].name, experiments[i].value);
    }

    return 0;
}
