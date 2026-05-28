#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_PROTOTYPES 128
#define MAX_LINE 512
#define MAX_NAME 180

typedef struct {
    char name[MAX_NAME];
    double learning_gain;
    double feasibility_signal;
    double user_response;
    double equity_value;
    double implementation_relevance;
    double ethical_risk;
    double operational_risk;
    double technical_risk;
    double scaling_risk;
    double composite_risk;
    double prototype_value;
} Prototype;

double compute_composite_risk(const Prototype *p) {
    return 0.30 * p->ethical_risk +
           0.30 * p->operational_risk +
           0.20 * p->technical_risk +
           0.20 * p->scaling_risk;
}

double compute_prototype_value(const Prototype *p) {
    return 0.25 * p->learning_gain +
           0.18 * p->feasibility_signal +
           0.20 * p->user_response +
           0.15 * p->equity_value +
           0.12 * p->implementation_relevance -
           0.10 * p->composite_risk;
}

int compare_desc(const void *a, const void *b) {
    const Prototype *pa = (const Prototype *)a;
    const Prototype *pb = (const Prototype *)b;

    if (pa->prototype_value < pb->prototype_value) return 1;
    if (pa->prototype_value > pb->prototype_value) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/prototype_portfolio_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    Prototype prototypes[MAX_PROTOTYPES];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file); /* header */

    while (fgets(line, sizeof(line), file) && count < MAX_PROTOTYPES) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(prototypes[count].name, token, MAX_NAME - 1);
        prototypes[count].name[MAX_NAME - 1] = '\0';

        strtok(NULL, ","); /* prototype_type */
        strtok(NULL, ","); /* fidelity_level */

        token = strtok(NULL, ",");
        prototypes[count].learning_gain = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        prototypes[count].feasibility_signal = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        prototypes[count].user_response = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        prototypes[count].equity_value = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        prototypes[count].implementation_relevance = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        prototypes[count].ethical_risk = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        prototypes[count].operational_risk = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        prototypes[count].technical_risk = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        prototypes[count].scaling_risk = token ? atof(token) : 0.0;

        prototypes[count].composite_risk = compute_composite_risk(&prototypes[count]);
        prototypes[count].prototype_value = compute_prototype_value(&prototypes[count]);

        count++;
    }

    fclose(file);

    qsort(prototypes, count, sizeof(Prototype), compare_desc);

    printf("rank,prototype,prototype_value,composite_risk\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f,%.6f\n", i + 1, prototypes[i].name, prototypes[i].prototype_value, prototypes[i].composite_risk);
    }

    return 0;
}
