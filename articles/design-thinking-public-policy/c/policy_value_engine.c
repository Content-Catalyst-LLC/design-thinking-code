#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ITEMS 160
#define MAX_LINE 640
#define MAX_NAME 220

typedef struct {
    char name[MAX_NAME];
    double accessibility;
    double feasibility;
    double legitimacy;
    double equity;
    double burden_reduction;
    double durability;
    double risk;
    double policy_value;
} PolicyPilot;

double compute_policy_value(const PolicyPilot *x) {
    return 0.20 * x->accessibility +
           0.16 * x->feasibility +
           0.16 * x->legitimacy +
           0.20 * x->equity +
           0.14 * x->burden_reduction +
           0.08 * x->durability -
           0.06 * x->risk;
}

int compare_desc(const void *a, const void *b) {
    const PolicyPilot *ia = (const PolicyPilot *)a;
    const PolicyPilot *ib = (const PolicyPilot *)b;

    if (ia->policy_value < ib->policy_value) return 1;
    if (ia->policy_value > ib->policy_value) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/public_policy_pilots_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    PolicyPilot pilots[MAX_ITEMS];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file); /* header */

    while (fgets(line, sizeof(line), file) && count < MAX_ITEMS) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(pilots[count].name, token, MAX_NAME - 1);
        pilots[count].name[MAX_NAME - 1] = '\0';

        strtok(NULL, ","); /* policy_domain */
        strtok(NULL, ","); /* pilot_type */

        token = strtok(NULL, ",");
        pilots[count].accessibility = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        pilots[count].feasibility = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        pilots[count].legitimacy = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        pilots[count].equity = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        pilots[count].burden_reduction = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        pilots[count].durability = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        pilots[count].risk = token ? atof(token) : 0.0;

        pilots[count].policy_value = compute_policy_value(&pilots[count]);

        count++;
    }

    fclose(file);

    qsort(pilots, count, sizeof(PolicyPilot), compare_desc);

    printf("rank,pilot,policy_value,risk\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f,%.6f\n", i + 1, pilots[i].name, pilots[i].policy_value, pilots[i].risk);
    }

    return 0;
}
