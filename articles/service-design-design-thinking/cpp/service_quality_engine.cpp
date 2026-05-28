#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct ServiceStage {
    std::string name;
    double completion_probability;
    double clarity;
    double trust;
    double accessibility;
    double user_burden;
    double staff_load;
    double recovery_quality;
};

struct ScoredStage {
    std::string name;
    double quality;
    double redesign_priority;
    double completion_probability;
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

double service_stage_quality(const ServiceStage& x) {
    return 0.22 * x.completion_probability * 10.0 +
           0.18 * x.clarity +
           0.18 * x.trust +
           0.16 * x.accessibility +
           0.14 * x.recovery_quality -
           0.07 * x.user_burden -
           0.05 * x.staff_load;
}

double redesign_priority(const ServiceStage& x) {
    const double failure_risk = 1.0 - x.completion_probability;
    const double burden_risk = 0.55 * x.user_burden + 0.45 * x.staff_load;
    return 0.34 * failure_risk * 10.0 +
           0.26 * burden_risk +
           0.18 * (10.0 - x.clarity) +
           0.12 * (10.0 - x.accessibility) +
           0.10 * (10.0 - x.recovery_quality);
}

std::vector<ServiceStage> read_stages(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::vector<ServiceStage> stages;
    std::string line;
    std::getline(file, line);

    while (std::getline(file, line)) {
        if (line.empty()) {
            continue;
        }

        auto fields = split_csv_line(line);
        if (fields.size() < 10) {
            throw std::runtime_error("Malformed CSV row: " + line);
        }

        stages.push_back(
            ServiceStage{
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

    return stages;
}

int main(int argc, char* argv[]) {
    const std::string default_path = "../data/raw/service_journey_stages_raw.csv";
    const std::string input_path = argc > 1 ? argv[1] : default_path;

    try {
        auto stages = read_stages(input_path);
        std::vector<ScoredStage> scored;
        double reliability = 1.0;

        for (const auto& stage : stages) {
            reliability *= stage.completion_probability;
            scored.push_back(
                ScoredStage{
                    stage.name,
                    service_stage_quality(stage),
                    redesign_priority(stage),
                    stage.completion_probability
                }
            );
        }

        std::sort(
            scored.begin(),
            scored.end(),
            [](const ScoredStage& a, const ScoredStage& b) {
                return a.redesign_priority > b.redesign_priority;
            }
        );

        std::cout << "end_to_end_reliability," << std::fixed << std::setprecision(8) << reliability << "\n";
        std::cout << "rank,stage,service_stage_quality,redesign_priority,completion_probability\n";
        for (std::size_t i = 0; i < scored.size(); ++i) {
            std::cout << (i + 1) << ","
                      << scored[i].name << ","
                      << std::fixed << std::setprecision(6)
                      << scored[i].quality << ","
                      << scored[i].redesign_priority << ","
                      << scored[i].completion_probability << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "ERROR: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
