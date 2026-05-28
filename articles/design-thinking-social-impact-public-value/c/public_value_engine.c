#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ITEMS 200
#define MAX_LINE 1600
#define MAX_NAME 260

typedef struct {
    char name[MAX_NAME];
    double access;
    double equity;
    double dignity;
    double legitimacy;
    double accountability;
    double outcome_strength;
    double sustainability;
    double learning;
    double feasibility;
    double governance;
    double implementation_risk;
    double burden_risk;
    double participation;
    double community_value;
    double repair;
    double stewardship;
    double public_value;
    double readiness;
    double stewardship_need;
    double portfolio_priority;
} Intervention;

void compute_scores(Intervention *x) {
    x->public_value =
        0.13*x->access +
        0.15*x->equity +
        0.12*x->dignity +
        0.12*x->legitimacy +
        0.13*x->accountability +
        0.11*x->outcome_strength +
        0.08*x->sustainability +
        0.07*x->learning +
        0.05*x->community_value +
        0.04*x->repair;

    x->readiness =
        0.30*x->public_value +
        0.17*x->feasibility +
        0.16*x->governance +
        0.12*x->learning +
        0.10*x->participation +
        0.08*x->stewardship +
        0.07*x->repair -
        0.07*x->implementation_risk -
        0.07*x->burden_risk;

    x->stewardship_need =
        0.24*x->implementation_risk +
        0.22*x->burden_risk +
        0.16*(10.0-x->governance) +
        0.12*(10.0-x->sustainability) +
        0.10*(10.0-x->learning) +
        0.08*(10.0-x->repair) +
        0.08*(10.0-x->stewardship);

    x->portfolio_priority =
        0.36*x->public_value +
        0.28*x->readiness +
        0.14*x->equity +
        0.10*x->community_value +
        0.06*x->participation -
        0.14*x->stewardship_need -
        0.06*x->implementation_risk;
}

int compare_desc(const void *a, const void *b) {
    const Intervention *ia = (const Intervention *)a;
    const Intervention *ib = (const Intervention *)b;
    if (ia->portfolio_priority < ib->portfolio_priority) return 1;
    if (ia->portfolio_priority > ib->portfolio_priority) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/social_impact_interventions_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    Intervention items[MAX_ITEMS];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file);

    while (fgets(line, sizeof(line), file) && count < MAX_ITEMS) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(items[count].name, token, MAX_NAME - 1);
        items[count].name[MAX_NAME - 1] = '\0';

        strtok(NULL, ","); /* intervention_type */

        token = strtok(NULL, ","); items[count].access = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].equity = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].dignity = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].legitimacy = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].accountability = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].outcome_strength = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].sustainability = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].learning = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].feasibility = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].governance = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].implementation_risk = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].burden_risk = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].participation = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].community_value = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].repair = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].stewardship = token ? atof(token) : 0.0;

        compute_scores(&items[count]);
        count++;
    }

    fclose(file);
    qsort(items, count, sizeof(Intervention), compare_desc);

    printf("rank,intervention,public_value_score,impact_readiness,stewardship_need,portfolio_priority\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f,%.6f,%.6f,%.6f\n",
            i + 1,
            items[i].name,
            items[i].public_value,
            items[i].readiness,
            items[i].stewardship_need,
            items[i].portfolio_priority
        );
    }

    return 0;
}
