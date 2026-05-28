#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct InnovationConcept {
    std::string name;
    double desirability;
    double feasibility;
    double viability;
    double equity;
    double learning_value;
    double implementation_readiness;
    double risk;
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

double design_value(const InnovationConcept& x) {
    return 0.22 * x.desirability +
           0.16 * x.feasibility +
           0.16 * x.viability +
           0.18 * x.equity +
           0.12 * x.learning_value +
           0.10 * x.implementation_readiness -
           0.06 * x.risk;
}

std::vector<InnovationConcept> read_concepts(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<InnovationConcept> concepts;
    std::string line;
    std::getline(file, line); // header

    while (std::getline(file, line)) {
        if (line.empty()) {
            continue;
        }

        auto fields = split_csv_line(line);
        if (fields.size() < 10) {
            throw std::runtime_error("Malformed CSV row: " + line);
        }

        concepts.push_back(
            InnovationConcept{
                fields[0],
                to_double(fields[3]),
                to_double(fields[4]),
                to_double(fields[5]),
                to_double(fields[6]),
                to_double(fields[7]),
                to_double(fields[8]),
                to_double(fields[9])
            }
        );
    }

    return concepts;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/organizational_innovation_concepts_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto concepts = read_concepts(input_path);
        std::vector<ScoredConcept> scored;

        for (const auto& concept : concepts) {
            scored.push_back(
                ScoredConcept{
                    concept.name,
                    design_value(concept),
                    concept.risk
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

        std::cout << "rank,concept,design_value,risk\n";
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
