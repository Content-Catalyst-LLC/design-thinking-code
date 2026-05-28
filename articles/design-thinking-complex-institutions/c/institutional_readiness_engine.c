#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ITEMS 200
#define MAX_LINE 1600
#define MAX_NAME 260

typedef struct {
    char name[MAX_NAME];
    double desirability;
    double authority;
    double capability;
    double funding;
    double policy_fit;
    double governance;
    double trust_gain;
    double burden_reduction;
    double coordination;
    double implementation_risk;
    double data_readiness;
    double frontline_fit;
    double maintenance;
    double equity;
    double public_value;
    double readiness;
    double absorption;
    double public_value_priority;
    double sequencing_need;
    double portfolio_score;
} Option;

void compute_scores(Option *x) {
    x->readiness =
        0.14*x->desirability +
        0.13*x->authority +
        0.12*x->capability +
        0.10*x->funding +
        0.10*x->policy_fit +
        0.11*x->governance +
        0.08*x->trust_gain +
        0.08*x->burden_reduction +
        0.06*x->data_readiness +
        0.05*x->frontline_fit +
        0.03*x->maintenance -
        0.05*x->coordination -
        0.05*x->implementation_risk;

    x->absorption =
        0.18*x->authority +
        0.18*x->capability +
        0.14*x->funding +
        0.14*x->governance +
        0.12*x->policy_fit +
        0.10*x->frontline_fit +
        0.08*x->maintenance +
        0.06*x->data_readiness;

    x->public_value_priority =
        0.24*x->public_value +
        0.20*x->burden_reduction +
        0.18*x->trust_gain +
        0.16*x->equity +
        0.12*x->desirability +
        0.10*x->policy_fit -
        0.08*x->implementation_risk;

    x->sequencing_need =
        0.28*x->coordination +
        0.24*x->implementation_risk +
        0.14*(10.0-x->authority) +
        0.12*(10.0-x->capability) +
        0.10*(10.0-x->funding) +
        0.07*(10.0-x->maintenance) +
        0.05*(10.0-x->data_readiness);

    x->portfolio_score =
        0.30*x->readiness +
        0.26*x->public_value_priority +
        0.20*x->absorption +
        0.10*x->equity +
        0.06*x->trust_gain -
        0.12*x->sequencing_need -
        0.08*x->implementation_risk;
}

int compare_desc(const void *a, const void *b) {
    const Option *ia = (const Option *)a;
    const Option *ib = (const Option *)b;
    if (ia->portfolio_score < ib->portfolio_score) return 1;
    if (ia->portfolio_score > ib->portfolio_score) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/institutional_design_options_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    Option items[MAX_ITEMS];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file);

    while (fgets(line, sizeof(line), file) && count < MAX_ITEMS) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(items[count].name, token, MAX_NAME - 1);
        items[count].name[MAX_NAME - 1] = '\0';

        strtok(NULL, ","); /* option_type */

        token = strtok(NULL, ","); items[count].desirability = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].authority = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].capability = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].funding = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].policy_fit = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].governance = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].trust_gain = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].burden_reduction = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].coordination = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].implementation_risk = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].data_readiness = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].frontline_fit = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].maintenance = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].equity = token ? atof(token) : 0.0;
        token = strtok(NULL, ","); items[count].public_value = token ? atof(token) : 0.0;

        compute_scores(&items[count]);
        count++;
    }

    fclose(file);
    qsort(items, count, sizeof(Option), compare_desc);

    printf("rank,option,change_readiness,absorption_capacity,public_value_priority,sequencing_need,portfolio_score\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f,%.6f,%.6f,%.6f,%.6f\n",
            i + 1,
            items[i].name,
            items[i].readiness,
            items[i].absorption,
            items[i].public_value_priority,
            items[i].sequencing_need,
            items[i].portfolio_score
        );
    }

    return 0;
}
