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
    double adoption_readiness;
    double operational_fit;
    double durability;
    double governance_readiness;
    double equity_readiness;
    double financial_sustainability;
    double operational_risk;
    double governance_risk;
    double technical_risk;
    double equity_risk;
    double financial_risk;
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

double composite_risk(const Intervention& x) {
    return 0.25 * x.operational_risk +
           0.22 * x.governance_risk +
           0.18 * x.technical_risk +
           0.22 * x.equity_risk +
           0.13 * x.financial_risk;
}

double implementation_value(const Intervention& x) {
    return 0.20 * x.adoption_readiness +
           0.18 * x.operational_fit +
           0.18 * x.durability +
           0.15 * x.governance_readiness +
           0.14 * x.equity_readiness +
           0.10 * x.financial_sustainability -
           0.05 * composite_risk(x);
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
        if (fields.size() < 14) {
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
                to_double(fields[9]),
                to_double(fields[10]),
                to_double(fields[11]),
                to_double(fields[12]),
                to_double(fields[13])
            }
        );
    }

    return interventions;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/implementation_portfolio_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto interventions = read_portfolio(input_path);
        std::vector<ScoredIntervention> scored;

        for (const auto& intervention : interventions) {
            scored.push_back(
                ScoredIntervention{
                    intervention.name,
                    implementation_value(intervention),
                    composite_risk(intervention)
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

        std::cout << "rank,intervention,implementation_value,composite_risk\n";
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
