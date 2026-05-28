#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct DesignDecision {
    std::string name;
    double harm;
    double probability;
    double exposure;
    double detectability;
    double accountability;
    double inclusion;
    double public_value;
    double repairability;
    double privacy;
    double autonomy;
    double manipulation;
};

struct ScoredDecision {
    std::string name;
    double ethical_risk;
    double review_priority;
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

double ethical_risk(const DesignDecision& x) {
    return x.harm * x.probability * x.exposure * (1.0 - x.detectability) * (1.0 - x.accountability);
}

double review_priority(const DesignDecision& x) {
    const double r = ethical_risk(x);
    const double repair_deficit = 1.0 - x.repairability;
    return 0.32 * r +
           0.20 * x.harm +
           0.14 * x.exposure +
           0.10 * (1.0 - x.accountability) +
           0.08 * (1.0 - x.detectability) +
           0.06 * (1.0 - x.inclusion) +
           0.05 * x.privacy +
           0.03 * x.autonomy +
           0.02 * x.manipulation -
           0.12 * x.public_value +
           0.10 * repair_deficit;
}

std::vector<DesignDecision> read_decisions(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<DesignDecision> decisions;
    std::string line;
    std::getline(file, line);

    while (std::getline(file, line)) {
        if (line.empty()) {
            continue;
        }

        auto fields = split_csv_line(line);
        if (fields.size() < 13) {
            throw std::runtime_error("Malformed CSV row: " + line);
        }

        decisions.push_back(
            DesignDecision{
                fields[0],
                to_double(fields[2]),
                to_double(fields[3]),
                to_double(fields[4]),
                to_double(fields[5]),
                to_double(fields[6]),
                to_double(fields[7]),
                to_double(fields[8]),
                to_double(fields[9]),
                to_double(fields[10]),
                to_double(fields[11]),
                to_double(fields[12])
            }
        );
    }

    return decisions;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/ethical_design_decisions_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto decisions = read_decisions(input_path);
        std::vector<ScoredDecision> scored;

        for (const auto& decision : decisions) {
            scored.push_back(
                ScoredDecision{
                    decision.name,
                    ethical_risk(decision),
                    review_priority(decision)
                }
            );
        }

        std::sort(
            scored.begin(),
            scored.end(),
            [](const ScoredDecision& a, const ScoredDecision& b) {
                return a.review_priority > b.review_priority;
            }
        );

        std::cout << "rank,design_decision,ethical_risk,review_priority\n";
        for (std::size_t i = 0; i < scored.size(); ++i) {
            std::cout << (i + 1) << ","
                      << scored[i].name << ","
                      << std::fixed << std::setprecision(6)
                      << scored[i].ethical_risk << ","
                      << scored[i].review_priority << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "ERROR: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
