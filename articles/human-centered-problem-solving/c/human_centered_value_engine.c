#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_OPTIONS 128
#define MAX_LINE 512
#define MAX_NAME 128

typedef struct {
    char name[MAX_NAME];
    double human_benefit;
    double usability;
    double stakeholder_fit;
    double burden;
    double value;
} DesignOption;

double human_centered_value(const DesignOption *option) {
    const double wb = 0.30;
    const double wu = 0.25;
    const double ws = 0.30;
    const double wc = 0.15;

    return wb * option->human_benefit
         + wu * option->usability
         + ws * option->stakeholder_fit
         - wc * option->burden;
}

int compare_desc(const void *a, const void *b) {
    const DesignOption *oa = (const DesignOption *)a;
    const DesignOption *ob = (const DesignOption *)b;

    if (oa->value < ob->value) return 1;
    if (oa->value > ob->value) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/human_centered_options_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    DesignOption options[MAX_OPTIONS];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file); /* header */

    while (fgets(line, sizeof(line), file) && count < MAX_OPTIONS) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(options[count].name, token, MAX_NAME - 1);
        options[count].name[MAX_NAME - 1] = '\0';

        token = strtok(NULL, ",");
        options[count].human_benefit = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        options[count].usability = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        options[count].stakeholder_fit = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        options[count].burden = token ? atof(token) : 0.0;

        options[count].value = human_centered_value(&options[count]);
        count++;
    }

    fclose(file);

    qsort(options, count, sizeof(DesignOption), compare_desc);

    printf("rank,option,hc_value\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f\n", i + 1, options[i].name, options[i].value);
    }

    return 0;
}
