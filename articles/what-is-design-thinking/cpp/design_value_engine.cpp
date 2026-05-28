#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct Pathway {
    std::string name;
    double human_relevance;
    double feasibility;
    double learning_value;
    double residual_risk;
};

struct ScoredPathway {
    std::string name;
    double value;
};

double to_double(const std::string& value) {
    try {
        return std::stod(value);
    } catch (...) {
        throw std::runtime_error("Unable to parse numeric value: " + value);
    }
}

std::vector<std::string> split_csv_line(const std::string& line) {
    std::vector<std::string> fields;
    std::stringstream ss(line);
    std::string item;

    while (std::getline(ss, item, ',')) {
        fields.push_back(item);
    }

    return fields;
}

std::vector<Pathway> read_pathways(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<Pathway> pathways;
    std::string line;

    std::getline(file, line); // header

    while (std::getline(file, line)) {
        if (line.empty()) {
            continue;
        }

        auto fields = split_csv_line(line);
        if (fields.size() < 5) {
            throw std::runtime_error("Malformed CSV row: " + line);
        }

        pathways.push_back(
            Pathway{
                fields[0],
                to_double(fields[1]),
                to_double(fields[2]),
                to_double(fields[3]),
                to_double(fields[4])
            }
        );
    }

    return pathways;
}

double design_value(const Pathway& p) {
    constexpr double wh = 0.35;
    constexpr double wf = 0.25;
    constexpr double wl = 0.25;
    constexpr double wr = 0.15;

    return wh * p.human_relevance
         + wf * p.feasibility
         + wl * p.learning_value
         - wr * p.residual_risk;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/design_pathways_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto pathways = read_pathways(input_path);
        std::vector<ScoredPathway> scored;

        for (const auto& pathway : pathways) {
            scored.push_back(ScoredPathway{pathway.name, design_value(pathway)});
        }

        std::sort(
            scored.begin(),
            scored.end(),
            [](const ScoredPathway& a, const ScoredPathway& b) {
                return a.value > b.value;
            }
        );

        std::cout << "rank,pathway,design_value\n";
        for (std::size_t i = 0; i < scored.size(); ++i) {
            std::cout << (i + 1) << ","
                      << scored[i].name << ","
                      << std::fixed << std::setprecision(6)
                      << scored[i].value << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "ERROR: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
