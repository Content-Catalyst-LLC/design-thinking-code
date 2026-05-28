#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ITEMS 160
#define MAX_LINE 1024
#define MAX_NAME 240

typedef struct {
    char name[MAX_NAME];
    double desirability;
    double feasibility;
    double viability;
    double alignment;
    double ethics;
    double learning;
    double effort;
    double risk;
    double capability_gap;
    double evidence;
    double time_to_learn;
    double public_value;
    double strategic_score;
    double portfolio_value;
} StrategicOption;

double compute_score(const StrategicOption *x) {
    return 0.17 * x->desirability +
           0.13 * x->feasibility +
           0.13 * x->viability +
           0.16 * x->alignment +
           0.11 * x->ethics +
           0.10 * x->learning +
           0.08 * x->public_value +
           0.05 * x->evidence * 10.0 -
           0.03 * x->risk -
           0.02 * x->effort -
           0.01 * x->capability_gap -
           0.01 * x->time_to_learn;
}

double compute_portfolio_value(const StrategicOption *x) {
    return x->strategic_score +
           0.30 * x->learning +
           0.20 * x->public_value +
           0.15 * x->evidence * 10.0 -
           0.22 * x->risk -
           0.14 * x->effort -
           0.10 * x->capability_gap;
}

int compare_desc(const void *a, const void *b) {
    const StrategicOption *ia = (const StrategicOption *)a;
    const StrategicOption *ib = (const StrategicOption *)b;

    if (ia->strategic_score < ib->strategic_score) return 1;
    if (ia->strategic_score > ib->strategic_score) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/strategic_options_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    StrategicOption items[MAX_ITEMS];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file);

    while (fgets(line, sizeof(line), file) && count < MAX_ITEMS) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(items[count].name, token, MAX_NAME - 1);
        items[count].name[MAX_NAME - 1] = '\0';

        strtok(NULL, ","); /* option_type */
        strtok(NULL, ","); /* strategic_hypothesis */

        token = strtok(NULL, ","); items[count].desirability = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].feasibility = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].viability = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].alignment = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].ethics = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].learning = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].effort = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].risk = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].capability_gap = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].evidence = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].time_to_learn = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].public_value = token ? atof(token) : 0.0;

        items[count].strategic_score = compute_score(&items[count]);
        items[count].portfolio_value = compute_portfolio_value(&items[count]);

        count++;
    }

    fclose(file);

    qsort(items, count, sizeof(StrategicOption), compare_desc);

    printf("rank,option,strategic_score,portfolio_value,strategic_risk\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f,%.6f,%.6f\n", i + 1, items[i].name, items[i].strategic_score, items[i].portfolio_value, items[i].risk);
    }

    return 0;
}
