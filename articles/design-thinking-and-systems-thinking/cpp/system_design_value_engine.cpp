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
    double human_value;
    double system_leverage;
    double feasibility;
    double equity_sensitivity;
    double durability;
    double risk;
};

struct ScoredIntervention {
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

double system_design_value(const Intervention& x) {
    return 0.24 * x.human_value +
           0.26 * x.system_leverage +
           0.18 * x.feasibility +
           0.14 * x.equity_sensitivity +
           0.12 * x.durability -
           0.06 * x.risk;
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
        if (fields.size() < 9) {
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
                to_double(fields[8])
            }
        );
    }

    return interventions;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/system_intervention_portfolio_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto interventions = read_portfolio(input_path);
        std::vector<ScoredIntervention> scored;

        for (const auto& intervention : interventions) {
            scored.push_back(
                ScoredIntervention{
                    intervention.name,
                    system_design_value(intervention),
                    intervention.risk
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

        std::cout << "rank,intervention,system_design_value,risk\n";
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
