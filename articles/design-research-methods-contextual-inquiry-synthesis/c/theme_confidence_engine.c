#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_ROWS 256
#define MAX_THEMES 64
#define MAX_LINE 512
#define MAX_TEXT 128

typedef struct {
    char theme[MAX_TEXT];
    int evidence_units;
    double total_strength;
    double total_risk;
    double confidence;
} ThemeAggregate;

int find_theme(ThemeAggregate *themes, int count, const char *theme) {
    for (int i = 0; i < count; i++) {
        if (strcmp(themes[i].theme, theme) == 0) {
            return i;
        }
    }
    return -1;
}

int compare_desc(const void *a, const void *b) {
    const ThemeAggregate *ta = (const ThemeAggregate *)a;
    const ThemeAggregate *tb = (const ThemeAggregate *)b;
    if (ta->confidence < tb->confidence) return 1;
    if (ta->confidence > tb->confidence) return -1;
    return 0;
}

int main(int argc, char **argv) {
    const char *path = argc > 1 ? argv[1] : "../data/raw/contextual_inquiry_evidence_units_raw.csv";
    FILE *file = fopen(path, "r");
    if (!file) {
        fprintf(stderr, "ERROR: Unable to open input file: %s\n", path);
        return 1;
    }

    ThemeAggregate themes[MAX_THEMES];
    int theme_count = 0;
    char line[MAX_LINE];

    memset(themes, 0, sizeof(themes));
    fgets(line, sizeof(line), file);

    while (fgets(line, sizeof(line), file)) {
        char *fields[12];
        int field_count = 0;
        char *token = strtok(line, ",");

        while (token != NULL && field_count < 12) {
            fields[field_count++] = token;
            token = strtok(NULL, ",");
        }

        if (field_count < 7) {
            continue;
        }

        const char *theme = fields[3];
        double strength = atof(fields[5]);
        double risk = atof(fields[6]);

        int idx = find_theme(themes, theme_count, theme);
        if (idx < 0 && theme_count < MAX_THEMES) {
            idx = theme_count++;
            strncpy(themes[idx].theme, theme, MAX_TEXT - 1);
            themes[idx].theme[MAX_TEXT - 1] = '\0';
        }

        if (idx >= 0) {
            themes[idx].evidence_units += 1;
            themes[idx].total_strength += strength;
            themes[idx].total_risk += risk;
        }
    }

    fclose(file);

    for (int i = 0; i < theme_count; i++) {
        double mean_strength = themes[i].total_strength / themes[i].evidence_units;
        double mean_risk = themes[i].total_risk / themes[i].evidence_units;
        themes[i].confidence = 0.70 * mean_strength - 0.30 * mean_risk;
    }

    qsort(themes, theme_count, sizeof(ThemeAggregate), compare_desc);

    printf("rank,theme,evidence_units,synthesis_confidence\n");
    for (int i = 0; i < theme_count; i++) {
        printf("%d,%s,%d,%.6f\n", i + 1, themes[i].theme, themes[i].evidence_units, themes[i].confidence);
    }

    return 0;
}
