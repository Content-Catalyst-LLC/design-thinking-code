#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct Intervention {
    std::string name;
    double outcome_improvement;
    double burden_reduction;
    double equity_performance;
    double trust_improvement;
    double durability;
    double operational_cost;
    double residual_risk;
};

struct ScoredIntervention {
    std::string name;
    double value;
    double penalty;
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

double penalty(const Intervention& x) {
    return 0.50 * x.operational_cost + 0.50 * x.residual_risk;
}

double evaluation_value(const Intervention& x) {
    return 0.24 * x.outcome_improvement +
           0.20 * x.burden_reduction +
           0.20 * x.equity_performance +
           0.16 * x.trust_improvement +
           0.14 * x.durability -
           0.06 * penalty(x);
}

std::vector<Intervention> read_portfolio(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<Intervention> interventions;
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

        interventions.push_back(
            Intervention{
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

    return interventions;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/evaluation_portfolio_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto interventions = read_portfolio(input_path);
        std::vector<ScoredIntervention> scored;

        for (const auto& intervention : interventions) {
            scored.push_back(
                ScoredIntervention{
                    intervention.name,
                    evaluation_value(intervention),
                    penalty(intervention)
                }
            );
        }

        std::sort(
            scored.begin(),
            scored.end(),
            [](const ScoredIntervention& a, const ScoredIntervention& b) {
                return a.value > b.value;
            }
        );

        std::cout << "rank,intervention,evaluation_value,penalty\n";
        for (std::size_t i = 0; i < scored.size(); ++i) {
            std::cout << (i + 1) << ","
                      << scored[i].name << ","
                      << std::fixed << std::setprecision(6)
                      << scored[i].value << ","
                      << scored[i].penalty << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "ERROR: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
