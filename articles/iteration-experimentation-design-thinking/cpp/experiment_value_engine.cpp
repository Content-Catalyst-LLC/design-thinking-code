#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct Experiment {
    std::string name;
    double learning_gain;
    double update_flexibility;
    double expected_improvement;
    double residual_risk;
};

struct ScoredExperiment {
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

std::vector<Experiment> read_experiments(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<Experiment> experiments;
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

        experiments.push_back(
            Experiment{
                fields[0],
                to_double(fields[1]),
                to_double(fields[2]),
                to_double(fields[3]),
                to_double(fields[4])
            }
        );
    }

    return experiments;
}

double experiment_value(const Experiment& experiment) {
    constexpr double wl = 0.35;
    constexpr double wu = 0.25;
    constexpr double we = 0.25;
    constexpr double wr = 0.15;

    return wl * experiment.learning_gain
         + wu * experiment.update_flexibility
         + we * experiment.expected_improvement
         - wr * experiment.residual_risk;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/experiments_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto experiments = read_experiments(input_path);
        std::vector<ScoredExperiment> scored;

        for (const auto& experiment : experiments) {
            scored.push_back(ScoredExperiment{experiment.name, experiment_value(experiment)});
        }

        std::sort(
            scored.begin(),
            scored.end(),
            [](const ScoredExperiment& a, const ScoredExperiment& b) {
                return a.value > b.value;
            }
        );

        std::cout << "rank,experiment,experiment_value\n";
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
