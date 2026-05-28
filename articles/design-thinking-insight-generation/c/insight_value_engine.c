#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_INSIGHTS 128
#define MAX_LINE 512
#define MAX_NAME 180

typedef struct {
    char name[MAX_NAME];
    double pattern_support;
    double explanatory_depth;
    double opportunity_value;
    double interpretive_risk;
    double value;
} Insight;

double insight_value(const Insight *insight) {
    const double wp = 0.30;
    const double we = 0.30;
    const double wo = 0.25;
    const double wr = 0.15;

    return wp * insight->pattern_support
         + we * insight->explanatory_depth
         + wo * insight->opportunity_value
         - wr * insight->interpretive_risk;
}

int compare_desc(const void *a, const void *b) {
    const Insight *ia = (const Insight *)a;
    const Insight *ib = (const Insight *)b;

    if (ia->value < ib->value) return 1;
    if (ia->value > ib->value) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/candidate_insights_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    Insight insights[MAX_INSIGHTS];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file); /* header */

    while (fgets(line, sizeof(line), file) && count < MAX_INSIGHTS) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(insights[count].name, token, MAX_NAME - 1);
        insights[count].name[MAX_NAME - 1] = '\0';

        token = strtok(NULL, ",");
        insights[count].pattern_support = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        insights[count].explanatory_depth = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        insights[count].opportunity_value = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        insights[count].interpretive_risk = token ? atof(token) : 0.0;

        insights[count].value = insight_value(&insights[count]);
        count++;
    }

    fclose(file);

    qsort(insights, count, sizeof(Insight), compare_desc);

    printf("rank,insight,insight_value\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f\n", i + 1, insights[i].name, insights[i].value);
    }

    return 0;
}
