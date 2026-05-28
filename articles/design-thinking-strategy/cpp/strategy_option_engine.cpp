#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct StrategicOption {
    std::string name;
    double desirability;
    double feasibility;
    double viability;
    double alignment;
    double ethics;
    double learning;
    double effort;
    double risk;
    double capability_gap;
    double evidence;
    double time_to_learn;
    double public_value;
};

struct ScoredOption {
    std::string name;
    double score;
    double portfolio_value;
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

double strategic_score(const StrategicOption& x) {
    return 0.17 * x.desirability +
           0.13 * x.feasibility +
           0.13 * x.viability +
           0.16 * x.alignment +
           0.11 * x.ethics +
           0.10 * x.learning +
           0.08 * x.public_value +
           0.05 * x.evidence * 10.0 -
           0.03 * x.risk -
           0.02 * x.effort -
           0.01 * x.capability_gap -
           0.01 * x.time_to_learn;
}

double portfolio_value(const StrategicOption& x) {
    return strategic_score(x) + 0.30 * x.learning + 0.20 * x.public_value + 0.15 * x.evidence * 10.0 -
           0.22 * x.risk - 0.14 * x.effort - 0.10 * x.capability_gap;
}

std::vector<StrategicOption> read_options(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<StrategicOption> options;
    std::string line;
    std::getline(file, line);

    while (std::getline(file, line)) {
        if (line.empty()) {
            continue;
        }

        auto fields = split_csv_line(line);
        if (fields.size() < 15) {
            throw std::runtime_error("Malformed CSV row: " + line);
        }

        options.push_back(
            StrategicOption{
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
                to_double(fields[13]),
                to_double(fields[14])
            }
        );
    }

    return options;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/strategic_options_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto options = read_options(input_path);
        std::vector<ScoredOption> scored;

        for (const auto& option : options) {
            scored.push_back(
                ScoredOption{
                    option.name,
                    strategic_score(option),
                    portfolio_value(option),
                    option.risk
                }
            );
        }

        std::sort(
            scored.begin(),
            scored.end(),
            [](const ScoredOption& a, const ScoredOption& b) {
                return a.score > b.score;
            }
        );

        std::cout << "rank,option,strategic_score,portfolio_value,strategic_risk\n";
        for (std::size_t i = 0; i < scored.size(); ++i) {
            std::cout << (i + 1) << ","
                      << scored[i].name << ","
                      << std::fixed << std::setprecision(6)
                      << scored[i].score << ","
                      << scored[i].portfolio_value << ","
                      << scored[i].risk << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "ERROR: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
