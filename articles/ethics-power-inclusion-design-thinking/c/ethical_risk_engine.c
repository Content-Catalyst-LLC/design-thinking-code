#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ITEMS 160
#define MAX_LINE 1024
#define MAX_NAME 240

typedef struct {
    char name[MAX_NAME];
    double harm;
    double probability;
    double exposure;
    double detectability;
    double accountability;
    double inclusion;
    double public_value;
    double repairability;
    double privacy;
    double autonomy;
    double manipulation;
    double ethical_risk;
    double review_priority;
} DesignDecision;

double compute_risk(const DesignDecision *x) {
    return x->harm * x->probability * x->exposure * (1.0 - x->detectability) * (1.0 - x->accountability);
}

double compute_priority(const DesignDecision *x) {
    double repair_deficit = 1.0 - x->repairability;
    return 0.32 * x->ethical_risk +
           0.20 * x->harm +
           0.14 * x->exposure +
           0.10 * (1.0 - x->accountability) +
           0.08 * (1.0 - x->detectability) +
           0.06 * (1.0 - x->inclusion) +
           0.05 * x->privacy +
           0.03 * x->autonomy +
           0.02 * x->manipulation -
           0.12 * x->public_value +
           0.10 * repair_deficit;
}

int compare_desc(const void *a, const void *b) {
    const DesignDecision *ia = (const DesignDecision *)a;
    const DesignDecision *ib = (const DesignDecision *)b;

    if (ia->review_priority < ib->review_priority) return 1;
    if (ia->review_priority > ib->review_priority) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/ethical_design_decisions_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    DesignDecision items[MAX_ITEMS];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file);

    while (fgets(line, sizeof(line), file) && count < MAX_ITEMS) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(items[count].name, token, MAX_NAME - 1);
        items[count].name[MAX_NAME - 1] = '\0';

        strtok(NULL, ","); /* decision_type */

        token = strtok(NULL, ","); items[count].harm = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].probability = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].exposure = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].detectability = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].accountability = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].inclusion = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].public_value = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].repairability = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].privacy = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].autonomy = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].manipulation = token ? atof(token) : 0.0;

        items[count].ethical_risk = compute_risk(&items[count]);
        items[count].review_priority = compute_priority(&items[count]);

        count++;
    }

    fclose(file);

    qsort(items, count, sizeof(DesignDecision), compare_desc);

    printf("rank,design_decision,ethical_risk,review_priority\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f,%.6f\n", i + 1, items[i].name, items[i].ethical_risk, items[i].review_priority);
    }

    return 0;
}
