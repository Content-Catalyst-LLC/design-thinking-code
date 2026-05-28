#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ITEMS 160
#define MAX_LINE 640
#define MAX_NAME 220

typedef struct {
    char name[MAX_NAME];
    double completion_probability;
    double clarity;
    double trust;
    double accessibility;
    double user_burden;
    double staff_load;
    double recovery_quality;
    double service_stage_quality;
    double redesign_priority;
} ServiceStage;

double compute_quality(const ServiceStage *x) {
    return 0.22 * x->completion_probability * 10.0 +
           0.18 * x->clarity +
           0.18 * x->trust +
           0.16 * x->accessibility +
           0.14 * x->recovery_quality -
           0.07 * x->user_burden -
           0.05 * x->staff_load;
}

double compute_priority(const ServiceStage *x) {
    double failure_risk = 1.0 - x->completion_probability;
    double burden_risk = 0.55 * x->user_burden + 0.45 * x->staff_load;
    return 0.34 * failure_risk * 10.0 +
           0.26 * burden_risk +
           0.18 * (10.0 - x->clarity) +
           0.12 * (10.0 - x->accessibility) +
           0.10 * (10.0 - x->recovery_quality);
}

int compare_desc(const void *a, const void *b) {
    const ServiceStage *ia = (const ServiceStage *)a;
    const ServiceStage *ib = (const ServiceStage *)b;

    if (ia->redesign_priority < ib->redesign_priority) return 1;
    if (ia->redesign_priority > ib->redesign_priority) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/service_journey_stages_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    ServiceStage stages[MAX_ITEMS];
    char line[MAX_LINE];
    int count = 0;
    double reliability = 1.0;

    fgets(line, sizeof(line), file);

    while (fgets(line, sizeof(line), file) && count < MAX_ITEMS) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(stages[count].name, token, MAX_NAME - 1);
        stages[count].name[MAX_NAME - 1] = '\0';

        strtok(NULL, ","); /* stage_order */
        strtok(NULL, ","); /* channel */

        token = strtok(NULL, ",");
        stages[count].completion_probability = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        stages[count].clarity = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        stages[count].trust = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        stages[count].accessibility = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        stages[count].user_burden = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        stages[count].staff_load = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        stages[count].recovery_quality = token ? atof(token) : 0.0;

        stages[count].service_stage_quality = compute_quality(&stages[count]);
        stages[count].redesign_priority = compute_priority(&stages[count]);
        reliability *= stages[count].completion_probability;

        count++;
    }

    fclose(file);

    qsort(stages, count, sizeof(ServiceStage), compare_desc);

    printf("end_to_end_reliability,%.8f\n", reliability);
    printf("rank,stage,service_stage_quality,redesign_priority,completion_probability\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f,%.6f,%.6f\n", i + 1, stages[i].name, stages[i].service_stage_quality, stages[i].redesign_priority, stages[i].completion_probability);
    }

    return 0;
}
