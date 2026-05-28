#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_FRAMES 128
#define MAX_LINE 512
#define MAX_NAME 128

typedef struct {
    char name[MAX_NAME];
    double explanatory_adequacy;
    double stakeholder_coverage;
    double opportunity_value;
    double framing_risk;
    double value;
} ProblemFrame;

double frame_value(const ProblemFrame *frame) {
    const double we = 0.30;
    const double ws = 0.25;
    const double wo = 0.30;
    const double wr = 0.15;

    return we * frame->explanatory_adequacy
         + ws * frame->stakeholder_coverage
         + wo * frame->opportunity_value
         - wr * frame->framing_risk;
}

int compare_desc(const void *a, const void *b) {
    const ProblemFrame *fa = (const ProblemFrame *)a;
    const ProblemFrame *fb = (const ProblemFrame *)b;

    if (fa->value < fb->value) return 1;
    if (fa->value > fb->value) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/problem_frames_raw.csv";
    FILE *file = fopen(path, "r");

    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    ProblemFrame frames[MAX_FRAMES];
    char line[MAX_LINE];
    int count = 0;

    fgets(line, sizeof(line), file); /* header */

    while (fgets(line, sizeof(line), file) && count < MAX_FRAMES) {
        char *token = strtok(line, ",");
        if (!token) continue;

        strncpy(frames[count].name, token, MAX_NAME - 1);
        frames[count].name[MAX_NAME - 1] = '\0';

        token = strtok(NULL, ",");
        frames[count].explanatory_adequacy = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        frames[count].stakeholder_coverage = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        frames[count].opportunity_value = token ? atof(token) : 0.0;

        token = strtok(NULL, ",");
        frames[count].framing_risk = token ? atof(token) : 0.0;

        frames[count].value = frame_value(&frames[count]);
        count++;
    }

    fclose(file);

    qsort(frames, count, sizeof(ProblemFrame), compare_desc);

    printf("rank,frame,frame_value\n");
    for (int i = 0; i < count; i++) {
        printf("%d,%s,%.6f\n", i + 1, frames[i].name, frames[i].value);
    }

    return 0;
}
