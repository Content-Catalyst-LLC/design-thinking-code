#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct Prototype {
    std::string name;
    double learning_gain;
    double feasibility_signal;
    double user_response;
    double equity_value;
    double implementation_relevance;
    double ethical_risk;
    double operational_risk;
    double technical_risk;
    double scaling_risk;
};

struct ScoredPrototype {
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

double composite_risk(const Prototype& p) {
    return 0.30 * p.ethical_risk +
           0.30 * p.operational_risk +
           0.20 * p.technical_risk +
           0.20 * p.scaling_risk;
}

double prototype_value(const Prototype& p) {
    return 0.25 * p.learning_gain +
           0.18 * p.feasibility_signal +
           0.20 * p.user_response +
           0.15 * p.equity_value +
           0.12 * p.implementation_relevance -
           0.10 * composite_risk(p);
}

std::vector<Prototype> read_portfolio(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<Prototype> prototypes;
    std::string line;
    std::getline(file, line); // header

    while (std::getline(file, line)) {
        if (line.empty()) {
            continue;
        }

        auto fields = split_csv_line(line);
        if (fields.size() < 12) {
            throw std::runtime_error("Malformed CSV row: " + line);
        }

        prototypes.push_back(
            Prototype{
                fields[0],
                to_double(fields[3]),
                to_double(fields[4]),
                to_double(fields[5]),
                to_double(fields[6]),
                to_double(fields[7]),
                to_double(fields[8]),
                to_double(fields[9]),
                to_double(fields[10]),
                to_double(fields[11])
            }
        );
    }

    return prototypes;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/prototype_portfolio_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto prototypes = read_portfolio(input_path);
        std::vector<ScoredPrototype> scored;

        for (const auto& prototype : prototypes) {
            scored.push_back(
                ScoredPrototype{
                    prototype.name,
                    prototype_value(prototype),
                    composite_risk(prototype)
                }
            );
        }

        std::sort(
            scored.begin(),
            scored.end(),
            [](const ScoredPrototype& a, const ScoredPrototype& b) {
                return a.value > b.value;
            }
        );

        std::cout << "rank,prototype,prototype_value,composite_risk\n";
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
