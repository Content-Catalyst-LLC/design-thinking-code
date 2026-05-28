#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct PolicyPilot {
    std::string name;
    double accessibility;
    double feasibility;
    double legitimacy;
    double equity;
    double burden_reduction;
    double durability;
    double risk;
};

struct ScoredPilot {
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

double policy_value(const PolicyPilot& x) {
    return 0.20 * x.accessibility +
           0.16 * x.feasibility +
           0.16 * x.legitimacy +
           0.20 * x.equity +
           0.14 * x.burden_reduction +
           0.08 * x.durability -
           0.06 * x.risk;
}

std::vector<PolicyPilot> read_pilots(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<PolicyPilot> pilots;
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

        pilots.push_back(
            PolicyPilot{
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

    return pilots;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/public_policy_pilots_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto pilots = read_pilots(input_path);
        std::vector<ScoredPilot> scored;

        for (const auto& pilot : pilots) {
            scored.push_back(
                ScoredPilot{
                    pilot.name,
                    policy_value(pilot),
                    pilot.risk
                }
            );
        }

        std::sort(
            scored.begin(),
            scored.end(),
            [](const ScoredPilot& a, const ScoredPilot& b) {
                return a.value > b.value;
            }
        );

        std::cout << "rank,pilot,policy_value,risk\n";
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
