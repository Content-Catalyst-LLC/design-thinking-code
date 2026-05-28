#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct Concept {
    std::string name;
    double desirability;
    double feasibility;
    double viability;
    double responsibility;
    double friction;
    double residual_risk;
};

struct ScoredConcept {
    std::string name;
    double value;
    double risk;
};

std::vector<std::string> split_csv_line(const std::string& line) {
    std::vector<std::string> fields;
    std::stringstream ss(line);
    std::string item;
    while (std::getline(ss, item, ',')) {
        fields.push_back(item);
    }
    return fields;
}

double to_double(const std::string& value) {
    try {
        return std::stod(value);
    } catch (...) {
        throw std::runtime_error("Unable to parse numeric value: " + value);
    }
}

double combined_risk(const Concept& c) {
    return 0.50 * c.friction + 0.50 * c.residual_risk;
}

double validation_value(const Concept& c) {
    return 0.25 * c.desirability +
           0.20 * c.feasibility +
           0.20 * c.viability +
           0.20 * c.responsibility -
           0.15 * combined_risk(c);
}

std::vector<Concept> read_concepts(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<Concept> concepts;
    std::string line;
    std::getline(file, line); // header

    while (std::getline(file, line)) {
        if (line.empty()) {
            continue;
        }

        auto fields = split_csv_line(line);
        if (fields.size() < 9) {
            throw std::runtime_error("Malformed CSV row: " + line);
        }

        concepts.push_back(
            Concept{
                fields[0],
                to_double(fields[3]),
                to_double(fields[4]),
                to_double(fields[5]),
                to_double(fields[6]),
                to_double(fields[7]),
                to_double(fields[8])
            }
        );
    }

    return concepts;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/validation_concepts_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto concepts = read_concepts(input_path);
        std::vector<ScoredConcept> scored;

        for (const auto& concept : concepts) {
            scored.push_back(
                ScoredConcept{
                    concept.name,
                    validation_value(concept),
                    combined_risk(concept)
                }
            );
        }

        std::sort(
            scored.begin(),
            scored.end(),
            [](const ScoredConcept& a, const ScoredConcept& b) {
                return a.value > b.value;
            }
        );

        std::cout << "rank,concept,validation_value,combined_risk\n";
        for (std::size_t i = 0; i < scored.size(); ++i) {
            std::cout << (i + 1) << ","
                      << scored[i].name << ","
                      << std::fixed << std::setprecision(6)
                      << scored[i].value << ","
                      << scored[i].risk << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "ERROR: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
