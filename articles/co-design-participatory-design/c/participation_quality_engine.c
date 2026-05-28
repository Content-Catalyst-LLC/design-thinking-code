#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ITEMS 160
#define MAX_LINE 640
#define MAX_NAME 220

typedef struct {
    char name[MAX_NAME];
    double representation;
    double accessibility;
    double participant_influence;
    double trust_quality;
    double evidence_quality;
    double implementation_accountability;
    double decision_impact;
    double ethical_risk;
    double participation_quality;
} CodesignActivity;

double compute_participation_quality(const CodesignActivity *x) {
    return 0.18 * x->representation +
           0.14 * x->accessibility +
           0.22 * x->participant_influence +
           0.12 * x->trust_quality +
           0.12 * x->evidence_quality +
           0.12 * x->implementation_accountability +
           0.14 * x->decision_impact -
           0.08 * x->ethical_risk;
}

int compare_desc(const void *a, const void *b) {
    const CodesignActivity *ia = (const CodesignActivity *)a;
    const CodesignActivity *ib = (const CodesignActivity *)b;

    if (ia->participation_quality < ib->participation_quality) return 1;
    if (ia->participation_quality > ib->participation_quality) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/codesign_activities_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    CodesignActivity activities[MAX_ITEMS];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file);

    while (fgets(line, sizeof(line), file) && count < MAX_ITEMS) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(activities[count].name, token, MAX_NAME - 1);
        activities[count].name[MAX_NAME - 1] = '\0';

        strtok(NULL, ","); /* activity_type */
        strtok(NULL, ","); /* design_stage */

        token = strtok(NULL, ",");
        activities[count].representation = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        activities[count].accessibility = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        activities[count].participant_influence = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        activities[count].trust_quality = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        activities[count].evidence_quality = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        activities[count].implementation_accountability = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        activities[count].decision_impact = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        activities[count].ethical_risk = token ? atof(token) : 0.0;

        activities[count].participation_quality = compute_participation_quality(&activities[count]);

        count++;
    }

    fclose(file);

    qsort(activities, count, sizeof(CodesignActivity), compare_desc);

    printf("rank,activity,participation_quality,ethical_risk\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f,%.6f\n", i + 1, activities[i].name, activities[i].participation_quality, activities[i].ethical_risk);
    }

    return 0;
}
